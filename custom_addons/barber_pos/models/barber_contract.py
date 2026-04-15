# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class BarberContract(models.Model):
    _name = 'barber.contract'
    _description = 'Contrat Coiffeur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _order = 'date_start desc'

    # ─── Relation ─────────────────────────────────────────────────────────────
    barber_id = fields.Many2one(
        'barber.barber', string='Coiffeur', required=True,
        ondelete='cascade', tracking=True)

    # ─── Type de contrat ──────────────────────────────────────────────────────
    contract_type = fields.Selection([
        ('rent', '🏠 Location Mensuelle'),
        ('percentage', '📊 Pourcentage du CA'),
    ], string='Type de contrat', required=True,
        default='percentage', tracking=True)

    # ─── Loyer mensuel ────────────────────────────────────────────────────────
    monthly_rent = fields.Float(
        string='Loyer mensuel (DZD)',
        help='Montant fixe que le coiffeur paie chaque mois pour sa place.')
    rent_due_day = fields.Integer(
        string='Jour d\'échéance', default=1,
        help='Jour du mois où le loyer est dû (1-28).')

    # ─── Pourcentage ──────────────────────────────────────────────────────────
    percentage = fields.Float(
        string='Pourcentage (%)',
        help='Pourcentage du CA du coiffeur reversé au salon.')
    percentage_base = fields.Selection([
        ('gross', 'CA Brut (avant remises)'),
        ('net', 'CA Net (après remises)'),
    ], string='Base de calcul', default='net')

    # ─── Dates ────────────────────────────────────────────────────────────────
    date_start = fields.Date(
        string='Date de début', required=True, default=fields.Date.today,
        tracking=True)
    date_end = fields.Date(string='Date de fin', tracking=True)

    # ─── Statut ───────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft', '📝 Brouillon'),
        ('active', '✅ Actif'),
        ('expired', '❌ Expiré'),
        ('cancelled', '🚫 Annulé'),
    ], string='Statut', default='draft', tracking=True)

    notes = fields.Text(string='Conditions & remarques')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Devise',
        related='company_id.currency_id', readonly=True)

    # ─── Computed ─────────────────────────────────────────────────────────────
    display_name = fields.Char(
        string='Référence', compute='_compute_display_name', store=True)
    is_expired = fields.Boolean(
        string='Expiré', compute='_compute_is_expired', store=True)

    @api.depends('barber_id', 'contract_type', 'date_start')
    def _compute_display_name(self):
        for rec in self:
            type_label = dict(rec._fields['contract_type'].selection).get(
                rec.contract_type, '')
            rec.display_name = (
                f"{rec.barber_id.name or ''} — {type_label} "
                f"({rec.date_start or ''})"
            )

    @api.depends('date_end', 'state')
    def _compute_is_expired(self):
        today = date.today()
        for rec in self:
            if rec.date_end and rec.date_end < today and rec.state == 'active':
                rec.is_expired = True
            else:
                rec.is_expired = False

    # ─── Contraintes ──────────────────────────────────────────────────────────
    @api.constrains('percentage')
    def _check_percentage(self):
        for rec in self:
            if rec.contract_type == 'percentage':
                if not (0 < rec.percentage <= 100):
                    raise ValidationError(
                        _('Le pourcentage doit être entre 0 et 100 %.'))

    @api.constrains('monthly_rent')
    def _check_rent(self):
        for rec in self:
            if rec.contract_type == 'rent' and rec.monthly_rent <= 0:
                raise ValidationError(
                    _('Le loyer mensuel doit être supérieur à 0.'))

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(
                    _('La date de fin doit être postérieure à la date de début.'))

    @api.constrains('barber_id', 'state')
    def _check_unique_active_contract(self):
        for rec in self:
            if rec.state == 'active':
                other = self.search([
                    ('barber_id', '=', rec.barber_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', rec.id),
                ])
                if other:
                    raise ValidationError(_(
                        'Le coiffeur "%s" a déjà un contrat actif. '
                        'Veuillez d\'abord clôturer l\'ancien contrat.'
                    ) % rec.barber_id.name)

    # ─── Actions ──────────────────────────────────────────────────────────────
    def action_activate(self):
        self.write({'state': 'active'})

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def _cron_check_expired_contracts(self):
        """Cron job: marque les contrats expirés automatiquement."""
        today = date.today()
        expired = self.search([
            ('state', '=', 'active'),
            ('date_end', '<', today),
        ])
        expired.write({'state': 'expired'})
