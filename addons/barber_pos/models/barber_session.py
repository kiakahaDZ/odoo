# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class BarberSession(models.Model):
    _name = 'barber.session'
    _description = 'Session POS Coiffeur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_open desc'

    # ─── Identification ───────────────────────────────────────────────────────
    name = fields.Char(
        string='Référence session', readonly=True,
        copy=False, default='Nouvelle')
    barber_id = fields.Many2one(
        'barber.barber', string='Coiffeur', required=True,
        tracking=True, ondelete='restrict')

    # ─── Dates ────────────────────────────────────────────────────────────────
    date_open = fields.Datetime(
        string='Ouverture', default=fields.Datetime.now, required=True)
    date_close = fields.Datetime(string='Fermeture', tracking=True)
    duration = fields.Float(
        string='Durée (h)', compute='_compute_duration', store=True)

    # ─── Caisse ───────────────────────────────────────────────────────────────
    cash_in = fields.Float(
        string='Fond de caisse ouverture', default=0.0,
        help='Montant en caisse au début de la session.')
    cash_out = fields.Float(
        string='Montant caisse fermeture', default=0.0,
        compute='_compute_cash_out', store=True)
    cash_difference = fields.Float(
        string='Différence caisse', compute='_compute_cash_difference',
        store=True)

    # ─── Statistiques de session ──────────────────────────────────────────────
    order_ids = fields.One2many(
        'barber.order', 'session_id', string='Commandes')
    order_count = fields.Integer(
        string='Nb Commandes', compute='_compute_totals', store=True)
    total_revenue = fields.Float(
        string='CA Session', compute='_compute_totals', store=True,
        digits=(10, 2))
    total_cash = fields.Float(
        string='Total Espèces', compute='_compute_totals', store=True)
    total_card = fields.Float(
        string='Total Carte', compute='_compute_totals', store=True)
    total_mobile = fields.Float(
        string='Total Mobile', compute='_compute_totals', store=True)

    # ─── Statut ───────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('open', '🟢 Ouverte'),
        ('closing', '🟡 En fermeture'),
        ('closed', '🔴 Fermée'),
    ], string='État', default='open', tracking=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Devise',
        related='company_id.currency_id', readonly=True)
    notes = fields.Text(string='Notes de session')

    # ─── Compute ──────────────────────────────────────────────────────────────
    @api.depends('date_open', 'date_close')
    def _compute_duration(self):
        for session in self:
            if session.date_open and session.date_close:
                delta = session.date_close - session.date_open
                session.duration = delta.total_seconds() / 3600.0
            else:
                session.duration = 0.0

    @api.depends('order_ids', 'order_ids.amount_total',
                 'order_ids.state', 'order_ids.payment_method')
    def _compute_totals(self):
        for session in self:
            paid = session.order_ids.filtered(lambda o: o.state == 'paid')
            session.order_count = len(paid)
            session.total_revenue = sum(paid.mapped('amount_total'))
            session.total_cash = sum(
                paid.filtered(
                    lambda o: o.payment_method == 'cash'
                ).mapped('amount_total'))
            session.total_card = sum(
                paid.filtered(
                    lambda o: o.payment_method == 'card'
                ).mapped('amount_total'))
            session.total_mobile = sum(
                paid.filtered(
                    lambda o: o.payment_method == 'mobile'
                ).mapped('amount_total'))

    @api.depends('cash_in', 'total_cash')
    def _compute_cash_out(self):
        for session in self:
            session.cash_out = session.cash_in + session.total_cash

    @api.depends('cash_out', 'total_cash', 'cash_in')
    def _compute_cash_difference(self):
        for session in self:
            session.cash_difference = (
                session.cash_out - session.cash_in - session.total_cash)

    # ─── ORM overrides ────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouvelle') == 'Nouvelle':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'barber.session') or 'SES-0001'
        return super().create(vals_list)

    # ─── Contraintes ──────────────────────────────────────────────────────────
    @api.constrains('barber_id', 'state')
    def _check_unique_open_session(self):
        for session in self:
            if session.state == 'open':
                other = self.search([
                    ('barber_id', '=', session.barber_id.id),
                    ('state', '=', 'open'),
                    ('id', '!=', session.id),
                ])
                if other:
                    raise ValidationError(_(
                        'Le coiffeur "%s" a déjà une session ouverte (#%s).'
                    ) % (session.barber_id.name, other[0].name))

    # ─── Actions ─────────────────────────────────────────────────────────────
    def action_new_order(self):
        """Crée une nouvelle commande dans cette session."""
        self.ensure_one()
        if self.state != 'open':
            raise UserError(_('Impossible de créer une commande. La session est fermée.'))
        order = self.env['barber.order'].create({
            'session_id': self.id,
            'barber_id': self.barber_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nouvelle Commande'),
            'res_model': 'barber.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_close_session(self):
        """Lance le wizard de fermeture de session."""
        self.ensure_one()
        if self.state == 'closed':
            raise UserError(_('Cette session est déjà fermée.'))
        # Vérifier qu'il n'y a pas de commandes en cours
        draft_orders = self.order_ids.filtered(lambda o: o.state == 'draft')
        if draft_orders:
            raise UserError(_(
                'Il y a %d commande(s) non finalisée(s). '
                'Veuillez les traiter avant de fermer la session.'
            ) % len(draft_orders))
        self.write({'state': 'closing'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Fermeture de session'),
            'res_model': 'barber.close.session.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_session_id': self.id},
        }

    def action_force_close(self):
        """Fermeture forcée sans wizard (admin uniquement)."""
        self.ensure_one()
        self.write({
            'state': 'closed',
            'date_close': fields.Datetime.now(),
        })

    def action_reopen(self):
        """Réouvre une session pour correction (admin)."""
        self.ensure_one()
        if self.state == 'open':
            raise UserError(_('La session est déjà ouverte.'))
        self.write({'state': 'open', 'date_close': False})

    def action_view_pos_interface(self):
        """Ouvre l'interface POS pour cette session."""
        self.ensure_one()
        if self.state != 'open':
            raise UserError(_('La session doit être ouverte pour accéder à la caisse.'))
        return {
            'type': 'ir.actions.act_url',
            'url': f'/barber/pos/{self.id}',
            'target': 'self',
        }
