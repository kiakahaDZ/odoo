# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BarberBarber(models.Model):
    _name = 'barber.barber'
    _description = 'Coiffeur / Barbier'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name asc'

    # ─── Identification ───────────────────────────────────────────────────────
    name = fields.Char(string='Nom complet', required=True, tracking=True)
    code = fields.Char(
        string='Code', readonly=True, copy=False,
        default='Nouveau')
    photo = fields.Binary(string='Photo', attachment=True)
    photo_filename = fields.Char(string='Nom fichier photo')

    # ─── Contact ──────────────────────────────────────────────────────────────
    phone = fields.Char(string='Téléphone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    address = fields.Text(string='Adresse')

    # ─── Compte utilisateur Odoo ──────────────────────────────────────────────
    user_id = fields.Many2one(
        'res.users', string='Compte utilisateur',
        help='Compte Odoo utilisé pour se connecter à la caisse.',
        tracking=True)

    # ─── Contrats ─────────────────────────────────────────────────────────────
    contract_ids = fields.One2many(
        'barber.contract', 'barber_id', string='Contrats')
    active_contract_id = fields.Many2one(
        'barber.contract', string='Contrat actif',
        compute='_compute_active_contract', store=True)
    contract_type = fields.Selection(
        related='active_contract_id.contract_type',
        string='Type de contrat', readonly=True, store=True)

    # ─── Sessions & Statistiques ──────────────────────────────────────────────
    session_ids = fields.One2many(
        'barber.session', 'barber_id', string='Sessions')
    order_ids = fields.One2many(
        'barber.order', 'barber_id', string='Commandes')

    total_revenue = fields.Float(
        string='CA Total', compute='_compute_stats', store=True)
    total_orders = fields.Integer(
        string='Nb Commandes', compute='_compute_stats', store=True)
    commission_due = fields.Float(
        string='Commission Due', compute='_compute_commission', store=True,
        help='Montant dû selon le type de contrat actif.')

    # ─── Statut ───────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
    ], string='Statut', default='active', tracking=True)
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes internes')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Devise',
        related='company_id.currency_id', readonly=True)

    # ─── Compute methods ──────────────────────────────────────────────────────
    @api.depends('contract_ids', 'contract_ids.state', 'contract_ids.date_start')
    def _compute_active_contract(self):
        for barber in self:
            active = barber.contract_ids.filtered(
                lambda c: c.state == 'active'
            ).sorted('date_start', reverse=True)
            barber.active_contract_id = active[:1]

    @api.depends('order_ids', 'order_ids.amount_total', 'order_ids.state')
    def _compute_stats(self):
        for barber in self:
            paid_orders = barber.order_ids.filtered(
                lambda o: o.state == 'paid')
            barber.total_orders = len(paid_orders)
            barber.total_revenue = sum(paid_orders.mapped('amount_total'))

    @api.depends('active_contract_id', 'total_revenue',
                 'active_contract_id.contract_type',
                 'active_contract_id.percentage',
                 'active_contract_id.monthly_rent')
    def _compute_commission(self):
        for barber in self:
            contract = barber.active_contract_id
            if not contract:
                barber.commission_due = 0.0
            elif contract.contract_type == 'percentage':
                barber.commission_due = (
                    barber.total_revenue * contract.percentage / 100.0)
            else:
                # Loyer mensuel : fixe
                barber.commission_due = contract.monthly_rent

    # ─── ORM overrides ────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'Nouveau') == 'Nouveau':
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    'barber.barber') or 'BAR-0001'
        return super().create(vals_list)

    @api.constrains('user_id')
    def _check_unique_user(self):
        for barber in self:
            if barber.user_id:
                other = self.search([
                    ('user_id', '=', barber.user_id.id),
                    ('id', '!=', barber.id),
                ])
                if other:
                    raise ValidationError(_(
                        'L\'utilisateur "%s" est déjà assigné à un autre coiffeur.'
                    ) % barber.user_id.name)

    def action_set_active(self):
        self.write({'state': 'active'})

    def action_set_inactive(self):
        self.write({'state': 'inactive'})

    def action_view_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commandes de %s') % self.name,
            'res_model': 'barber.order',
            'view_mode': 'list,form',
            'domain': [('barber_id', '=', self.id)],
            'context': {'default_barber_id': self.id},
        }

    def action_open_session(self):
        """Ouvre une nouvelle session POS pour ce coiffeur."""
        existing = self.env['barber.session'].search([
            ('barber_id', '=', self.id),
            ('state', '=', 'open'),
        ], limit=1)
        if existing:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Session en cours'),
                'res_model': 'barber.session',
                'res_id': existing.id,
                'view_mode': 'form',
            }
        session = self.env['barber.session'].create({
            'barber_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nouvelle Session'),
            'res_model': 'barber.session',
            'res_id': session.id,
            'view_mode': 'form',
        }
