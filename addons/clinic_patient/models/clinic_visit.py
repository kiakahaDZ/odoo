# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, AccessError


class ClinicVisit(models.Model):
    _name = 'clinic.visit'
    _description = 'Visite Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'visit_date desc, id desc'

    # ==========================================
    # IDENTIFICATION
    # ==========================================
    name = fields.Char(
        string='Référence',
        readonly=True,
        copy=False,
        index=True,
        default='Nouveau',
    )

    # ==========================================
    # RELATIONS
    # ==========================================
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        domain=[('is_patient', '=', True)],
        tracking=True,
    )

    doctor_id = fields.Many2one(
        'res.partner',
        string='Médecin Traitant',
        domain=[('is_doctor', '=', True)],
        tracking=True,
    )

    # ==========================================
    # DATES & INFOS VISITE
    # ==========================================
    visit_date = fields.Datetime(
        string='Date de Visite',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )

    visit_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('laboratory', 'Laboratoire'),
        ('imaging', 'Imagerie'),
        ('surgery', 'Chirurgie'),
        ('emergency', 'Urgence'),
        ('follow_up', 'Suivi'),
    ], string='Type de Visite', required=True, tracking=True)

    # Orientation Dynamique (per cahier des charges)
    orientation = fields.Selection([
        ('consultation', 'Consultation'),
        ('laboratory', 'Laboratoire'),
        ('imaging', 'Imagerie'),
        ('consultation_lab', 'Consultation + Labo'),
        ('consultation_imaging', 'Consultation + Imagerie'),
        ('full_checkup', 'Bilan Complet'),
    ], string='Orientation', tracking=True,
       help="Direction du patient dans le parcours clinique")

    # ==========================================
    # WORKFLOW / STATUT
    # ==========================================
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('reception', 'Réception'),
        ('waiting', 'Salle d\'Attente'),
        ('in_progress', 'En Examen'),
        ('waiting_results', 'En Attente Résultats'),
        ('waiting_payment', 'En Attente Paiement'),
        ('paid', 'Payé'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft', tracking=True,
       help="Suivi du parcours patient dans la clinique")

    # ==========================================
    # ACTES MÉDICAUX
    # ==========================================
    visit_line_ids = fields.One2many(
        'clinic.visit.line', 'visit_id',
        string='Actes Médicaux',
    )

    # ==========================================
    # FINANCIER
    # ==========================================
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
    )

    total_amount = fields.Monetary(
        string='Montant Total',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
    )

    doctor_share = fields.Monetary(
        string='Part Médecin',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
    )

    clinic_share = fields.Monetary(
        string='Part Clinique',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
    )

    is_paid = fields.Boolean(
        string='Payé',
        default=False,
        tracking=True,
    )

    payment_date = fields.Datetime(
        string='Date de Paiement',
    )

    payment_method = fields.Selection([
        ('cash', 'Espèces'),
        ('bank', 'Virement Bancaire'),
        ('check', 'Chèque'),
        ('insurance', 'Assurance / Tiers Payant'),
    ], string='Mode de Paiement')

    cashier_id = fields.Many2one(
        'res.users',
        string='Caissier',
        help='Utilisateur ayant encaissé le paiement',
    )

    # ==========================================
    # NOTES
    # ==========================================
    notes = fields.Text(
        string='Notes',
        help='Notes supplémentaires sur la visite',
    )

    reason = fields.Text(
        string='Motif de Consultation',
    )

    diagnosis = fields.Text(
        string='Diagnostic',
    )

    # ==========================================
    # CHAMPS CALCULÉS
    # ==========================================

    def _compute_display_name(self):
        for visit in self:
            if visit.patient_id and visit.name:
                visit.display_name = f"{visit.name} - {visit.patient_id.name}"
            else:
                visit.display_name = visit.name or 'Nouveau'

    @api.depends('visit_line_ids.subtotal',
                 'visit_line_ids.doctor_amount',
                 'visit_line_ids.clinic_amount')
    def _compute_amounts(self):
        for visit in self:
            visit.total_amount = sum(visit.visit_line_ids.mapped('subtotal'))
            visit.doctor_share = sum(visit.visit_line_ids.mapped('doctor_amount'))
            visit.clinic_share = sum(visit.visit_line_ids.mapped('clinic_amount'))

    # ==========================================
    # ACTIONS WORKFLOW
    # ==========================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'clinic.visit.sequence'
                ) or 'VIS/NEW'
        return super().create(vals_list)

    def action_reception(self):
        """Enregistrer le patient à la réception"""
        self.write({'state': 'reception'})

    def action_waiting(self):
        """Envoyer en salle d'attente"""
        self.write({'state': 'waiting'})

    def action_in_progress(self):
        """Commencer l'examen"""
        self.write({'state': 'in_progress'})

    def action_waiting_results(self):
        """En attente des résultats"""
        self.write({'state': 'waiting_results'})

    def action_waiting_payment(self):
        """En attente de paiement"""
        for visit in self:
            if not visit.visit_line_ids:
                raise UserError("Veuillez ajouter au moins un acte médical avant de passer au paiement.")
        self.write({'state': 'waiting_payment'})

    def action_pay(self):
        """Encaisser le paiement"""
        if not self.env.user.has_group('clinic_patient.group_clinic_cashier') and not self.env.user.has_group('clinic_patient.group_clinic_manager'):
            raise AccessError("Seuls les caissiers/gestionnaires peuvent valider un paiement.")
        self.ensure_one()
        if not self.payment_method:
            raise UserError("Veuillez sélectionner un mode de paiement.")
        self.write({
            'state': 'in_progress',  # Examen débute automatiquement après paiement
            'is_paid': True,
            'payment_date': fields.Datetime.now(),
            'cashier_id': self.env.user.id,
        })
        # Mettre les actes en cours automatiquement
        self.visit_line_ids.filtered(lambda l: l.act_state == 'pending').write({'act_state': 'in_progress'})

    def action_refund(self):
        """Remboursement et retour en attente de paiement"""
        self.write({
            'state': 'waiting_payment',
            'is_paid': False,
            'payment_date': False,
            'cashier_id': False,
        })

    def action_done(self):
        """Terminer la visite"""
        for visit in self:
            if not visit.is_paid:
                raise UserError(
                    "⚠️ Pas de Paiement, Pas d'Acte!\n"
                    "Le paiement doit être effectué avant de clôturer la visite."
                )
        self.write({'state': 'done'})

    def action_cancel(self):
        """Annuler la visite"""
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        """Remettre en brouillon"""
        self.write({'state': 'draft', 'is_paid': False})


class ClinicVisitLine(models.Model):
    _name = 'clinic.visit.line'
    _description = 'Ligne d\'Acte Médical'

    visit_id = fields.Many2one(
        'clinic.visit',
        string='Visite',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Acte Médical',
        required=True,
        domain=[('is_medical_act', '=', True)],
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            # Si on ajoute un acte payant à une visite déjà avancée
            if line.visit_id.state in ['paid', 'in_progress', 'waiting', 'done'] and line.subtotal > 0:
                line.visit_id.write({
                    'state': 'waiting_payment',
                    'is_paid': False
                })
        return lines

    medical_type = fields.Selection(
        related='product_id.medical_act_type',
        store=True,
        string="Type d'Acte"
    )

    description = fields.Text(
        string='Description',
    )

    quantity = fields.Float(
        string='Quantité',
        default=1.0,
    )

    unit_price = fields.Float(
        string='Prix Unitaire',
    )

    currency_id = fields.Many2one(
        related='visit_id.currency_id',
    )

    subtotal = fields.Monetary(
        string='Sous-total',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id',
    )

    # Répartition financière Part Clinique vs Part Praticien
    doctor_percentage = fields.Float(
        string='% Médecin',
    )

    clinic_percentage = fields.Float(
        string='% Clinique',
    )

    doctor_amount = fields.Monetary(
        string='Part Médecin',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id',
    )

    clinic_amount = fields.Monetary(
        string='Part Clinique',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id',
    )

    # Statut de l'acte
    act_state = fields.Selection([
        ('pending', 'En Attente'),
        ('in_progress', 'En Cours'),
        ('completed', 'Réalisé'),
        ('cancelled', 'Annulé'),
    ], string='Statut Acte', default='pending')

    result_notes = fields.Text(
        string='Résultats / Compte-rendu',
    )

    technician_id = fields.Many2one(
        'res.users',
        string='Technicien / Réalisé par',
    )

    @api.depends('quantity', 'unit_price', 'doctor_percentage', 'clinic_percentage')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
            line.doctor_amount = line.subtotal * (line.doctor_percentage / 100.0)
            line.clinic_amount = line.subtotal * (line.clinic_percentage / 100.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-remplir le prix et les pourcentages depuis le produit"""
        if self.product_id:
            self.unit_price = self.product_id.list_price
            self.description = self.product_id.description or self.product_id.name
            tmpl = self.product_id.product_tmpl_id
            self.doctor_percentage = tmpl.doctor_share_percentage
            self.clinic_percentage = tmpl.clinic_share_percentage

    def action_validate_act(self):
        """Valider l'acte médical (Technicien)"""
        self.ensure_one()
        self.write({
            'act_state': 'completed',
            'technician_id': self.env.user.id,
        })
        # Auto-Clôture si tous les actes sont terminés
        if self.visit_id.visit_line_ids and all(l.act_state == 'completed' for l in self.visit_id.visit_line_ids):
            self.visit_id.action_done()
