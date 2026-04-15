# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ClinicReception(models.Model):
    _name = 'clinic.reception'
    _description = 'Réception Clinique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reception_date desc, id desc'

    name = fields.Char(
        string='Numéro de Ticket',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
        help='Numéro unique du ticket de réception'
    )
    
    reception_date = fields.Datetime(
        string='Date de Réception',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help='Date et heure de réception du patient'
    )
    
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        domain=[('is_patient', '=', True)],
        tracking=True,
        help='Patient reçu'
    )
    
    # Informations patient (pour affichage rapide)
    patient_number = fields.Char(
        related='patient_id.patient_number',
        string='N° Dossier',
        readonly=True,
        store=True
    )
    
    patient_age = fields.Integer(
        related='patient_id.age',
        string='Âge',
        readonly=True
    )
    
    patient_phone = fields.Char(
        related='patient_id.phone',
        string='Téléphone',
        readonly=True
    )
    
    # Actes médicaux demandés
    medical_act_line_ids = fields.One2many(
        'clinic.reception.line',
        'reception_id',
        string='Actes Demandés',
        help='Liste des actes médicaux demandés'
    )
    
    # Totaux
    total_amount = fields.Monetary(
        string='Montant Total',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id',
        help='Montant total des actes'
    )
    
    act_count = fields.Integer(
        string='Nombre d\'Actes',
        compute='_compute_act_count',
        help='Nombre d\'actes demandés'
    )
    
    # Statut
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting', 'En Attente Caisse'),
        ('paid', 'Payé'),
        ('in_progress', 'En Cours'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft', required=True, tracking=True)
    
    # Utilisateur
    receptionist_id = fields.Many2one(
        'res.users',
        string='Réceptionniste',
        default=lambda self: self.env.user,
        readonly=True,
        help='Réceptionniste qui a créé le ticket'
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
        """Génère un numéro de ticket unique"""
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('clinic.reception') or _('Nouveau')
        return super(ClinicReception, self).create(vals_list)

    @api.depends('medical_act_line_ids', 'medical_act_line_ids.price_total')
    def _compute_total_amount(self):
        """Calcule le montant total"""
        for reception in self:
            reception.total_amount = sum(reception.medical_act_line_ids.mapped('price_total'))

    @api.depends('medical_act_line_ids')
    def _compute_act_count(self):
        """Compte le nombre d'actes"""
        for reception in self:
            reception.act_count = len(reception.medical_act_line_ids)

    def action_send_to_cashier(self):
        """Envoie le ticket à la caisse"""
        self.ensure_one()
        if not self.medical_act_line_ids:
            raise UserError(_('Veuillez ajouter au moins un acte medical!'))
        
        # Creer les lignes d'actes medicaux liees a ce ticket de reception
        for line in self.medical_act_line_ids:
            self.env['clinic.medical.act.line'].create({
                'patient_id': self.patient_id.id,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'state': 'waiting',
                'reception_id': self.id,
                'notes': f'Ticket de reception: {self.name}',
            })
        
        self.write({'state': 'waiting'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'message': _('Le ticket a été envoyé à la caisse.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_mark_paid(self):
        """Marque le ticket comme payé"""
        self.write({'state': 'paid'})

    def action_mark_done(self):
        """Marque le ticket comme terminé"""
        self.write({'state': 'done'})

    def action_cancel(self):
        """Annule le ticket"""
        if self.state == 'done':
            raise UserError(_('Impossible d\'annuler un ticket terminé!'))
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        """Remet le ticket en brouillon"""
        self.write({'state': 'draft'})

    def action_view_medical_acts(self):
        """Affiche les actes médicaux créés depuis cette réception"""
        self.ensure_one()
        acts = self.env['clinic.medical.act.line'].search([('reception_id', '=', self.id)])
        
        if not acts:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('Aucun acte médical créé pour cette réception.'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.medical.act.line',
            'view_mode': 'list,form,kanban',
            'domain': [('reception_id', '=', self.id)],
            'context': {'default_reception_id': self.id},
            'target': 'current',
            'name': _('Actes Médicaux - %s') % self.name,
        }

