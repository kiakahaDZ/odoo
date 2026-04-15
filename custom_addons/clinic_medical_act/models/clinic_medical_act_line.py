# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ClinicMedicalActLine(models.Model):
    _name = 'clinic.medical.act.line'
    _description = 'Ligne d\'Acte Médical'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
        help='Référence unique de l\'acte'
    )
    
    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help='Date et heure de l\'acte'
    )
    
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        domain=[('is_patient', '=', True)],
        tracking=True,
        help='Patient concerné'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Acte Médical',
        required=True,
        domain=[('is_medical_act', '=', True)],
        tracking=True,
        help='Acte médical effectué'
    )
    
    # Champs liés au produit
    medical_act_type = fields.Selection(
        related='product_id.product_tmpl_id.medical_act_type',
        string='Type d\'Acte',
        store=True,
        readonly=True
    )
    
    service_type = fields.Selection(
        related='product_id.product_tmpl_id.service_type',
        string='Service',
        store=True,
        readonly=True
    )
    
    requires_validation = fields.Boolean(
        related='product_id.product_tmpl_id.requires_validation',
        string='Nécessite Validation',
        store=True,
        readonly=True
    )
    
    doctor_id = fields.Many2one(
        related='product_id.product_tmpl_id.doctor_id',
        string='Médecin',
        store=True,
        readonly=True
    )
    
    doctor_share_percentage = fields.Float(
        related='product_id.product_tmpl_id.doctor_share_percentage',
        string='Pourcentage Partage Médecin',
        store=True,
        readonly=True
    )

    # Prix et partage
    price_unit = fields.Monetary(
        string='Prix Unitaire',
        required=True,
        currency_field='currency_id',
        help='Prix de l\'acte'
    )
    
    quantity = fields.Float(
        string='Quantité',
        default=1.0,
        required=True,
        help='Quantité (généralement 1 pour un acte médical)'
    )
    
    price_total = fields.Monetary(
        string='Prix Total',
        compute='_compute_price_total',
        store=True,
        currency_field='currency_id'
    )
    
    doctor_share_amount = fields.Monetary(
        string='Part Médecin',
        compute='_compute_share_amounts',
        store=True,
        currency_field='currency_id'
    )
    
    clinic_share_amount = fields.Monetary(
        string='Part Clinique',
        compute='_compute_share_amounts',
        store=True,
        currency_field='currency_id'
    )
    
    # Statut de l'acte
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting', 'En Attente'),
        ('paid', 'Payé'),
        ('in_progress', 'En Cours'),
        ('done', 'Réalisé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft', required=True, tracking=True)
    
    # Validation
    validated_by = fields.Many2one(
        'res.users',
        string='Validé Par',
        readonly=True,
        help='Utilisateur qui a validé l\'acte'
    )
    
    validation_date = fields.Datetime(
        string='Date de Validation',
        readonly=True,
        help='Date de validation de l\'acte'
    )
    
    # Paiement
    pos_order_id = fields.Many2one(
        'pos.order',
        string='Commande POS',
        readonly=True,
        help='Commande POS associée'
    )
    
    payment_date = fields.Datetime(
        string='Date de Paiement',
        readonly=True,
        help='Date du paiement'
    )
    
    # Notes
    notes = fields.Text(string='Notes')
    
    # Devise
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Génère une référence unique pour l'acte"""
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('clinic.medical.act.line') or _('Nouveau')
        return super(ClinicMedicalActLine, self).create(vals_list)

    @api.depends('price_unit', 'quantity')
    def _compute_price_total(self):
        """Calcule le prix total"""
        for line in self:
            line.price_total = line.price_unit * line.quantity

    @api.depends('price_total', 'product_id')
    def _compute_share_amounts(self):
        """Calcule les parts médecin et clinique"""
        for line in self:
            if line.product_id and line.product_id.product_tmpl_id.is_medical_act:
                template = line.product_id.product_tmpl_id
                line.doctor_share_amount = line.price_total * (template.doctor_share_percentage / 100.0)
                line.clinic_share_amount = line.price_total * (template.clinic_share_percentage / 100.0)
            else:
                line.doctor_share_amount = 0.0
                line.clinic_share_amount = 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Met à jour le prix unitaire selon le produit"""
        if self.product_id:
            self.price_unit = self.product_id.list_price

    def action_set_waiting(self):
        """Passe l'acte en attente"""
        self.write({'state': 'waiting'})

    def action_set_paid(self):
        """Marque l'acte comme payé"""
        self.write({
            'state': 'paid',
            'payment_date': fields.Datetime.now()
        })

    def action_set_in_progress(self):
        """Marque l'acte comme en cours"""
        if self.state != 'paid':
            raise UserError(_('L\'acte doit être payé avant de passer en cours!'))
        self.write({'state': 'in_progress'})

    def action_validate(self):
        """Valide l'acte (pour labo et imagerie)"""
        if self.state != 'in_progress':
            raise UserError(_('L\'acte doit être en cours pour être validé!'))
        self.write({
            'state': 'done',
            'validated_by': self.env.user.id,
            'validation_date': fields.Datetime.now()
        })

    def action_cancel(self):
        """Annule l'acte"""
        if self.state == 'done':
            raise UserError(_('Impossible d\'annuler un acte déjà réalisé!'))
        self.write({'state': 'cancelled'})
