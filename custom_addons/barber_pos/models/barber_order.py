# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BarberOrderLine(models.Model):
    _name = 'barber.order.line'
    _description = 'Ligne de Commande POS'
    _order = 'sequence, id'

    # ─── Relation ─────────────────────────────────────────────────────────────
    order_id = fields.Many2one(
        'barber.order', string='Commande',
        required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)

    # ─── Prestation ───────────────────────────────────────────────────────────
    service_id = fields.Many2one(
        'barber.service', string='Prestation', required=True,
        domain=[('active', '=', True)])
    service_code = fields.Char(
        related='service_id.code', readonly=True, string='Code')
    category_id = fields.Many2one(
        related='service_id.category_id', string='Catégorie', readonly=True)

    # ─── Tarification ─────────────────────────────────────────────────────────
    qty = fields.Float(string='Quantité', default=1.0, required=True)
    unit_price = fields.Float(
        string='Prix unitaire', required=True, digits=(10, 2))
    discount = fields.Float(
        string='Remise (%)', default=0.0,
        help='Remise en pourcentage appliquée sur le prix unitaire.')
    subtotal = fields.Float(
        string='Sous-total', compute='_compute_subtotal',
        store=True, digits=(10, 2))

    # ─── Infos supplémentaires ────────────────────────────────────────────────
    barber_id = fields.Many2one(
        related='order_id.barber_id', string='Coiffeur', readonly=True,
        store=True)
    notes = fields.Char(string='Note sur la prestation')
    allow_price_override = fields.Boolean(
        related='service_id.allow_price_override', readonly=True)
    color = fields.Integer(related='service_id.color', readonly=True)

    # ─── Compute ──────────────────────────────────────────────────────────────
    @api.depends('qty', 'unit_price', 'discount')
    def _compute_subtotal(self):
        for line in self:
            price_after_discount = line.unit_price * (1 - line.discount / 100.0)
            line.subtotal = line.qty * price_after_discount

    @api.onchange('service_id')
    def _onchange_service(self):
        if self.service_id:
            self.unit_price = self.service_id.price
            self.discount = 0.0

    # ─── Contraintes ──────────────────────────────────────────────────────────
    @api.constrains('qty')
    def _check_qty(self):
        for line in self:
            if line.qty <= 0:
                raise ValidationError(
                    _('La quantité doit être supérieure à 0.'))

    @api.constrains('unit_price', 'service_id')
    def _check_price_override(self):
        for line in self:
            if not line.service_id.allow_price_override:
                if line.unit_price != line.service_id.price:
                    raise ValidationError(_(
                        'La prestation "%s" n\'autorise pas la modification du prix.'
                    ) % line.service_id.name)

    @api.constrains('unit_price', 'service_id')
    def _check_price_min(self):
        for line in self:
            svc = line.service_id
            if svc.price_min > 0 and line.unit_price < svc.price_min:
                raise ValidationError(_(
                    'Le prix de "%s" ne peut pas être inférieur au minimum '
                    'de %.2f DZD.'
                ) % (svc.name, svc.price_min))

    @api.constrains('discount')
    def _check_discount(self):
        for line in self:
            if not (0 <= line.discount <= 100):
                raise ValidationError(
                    _('La remise doit être entre 0 et 100 %.'))


class BarberOrder(models.Model):
    _name = 'barber.order'
    _description = 'Commande / Ticket POS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_order desc'

    # ─── Identification ───────────────────────────────────────────────────────
    name = fields.Char(
        string='N° Ticket', readonly=True, copy=False, default='Nouveau')
    session_id = fields.Many2one(
        'barber.session', string='Session', required=True,
        ondelete='restrict', tracking=True,
        domain=[('state', '=', 'open')])
    barber_id = fields.Many2one(
        'barber.barber', string='Coiffeur', required=True,
        tracking=True, ondelete='restrict')
    partner_id = fields.Many2one(
        'res.partner', string='Client', tracking=True)

    # ─── Date & heure ─────────────────────────────────────────────────────────
    date_order = fields.Datetime(
        string='Date/Heure', required=True,
        default=fields.Datetime.now, tracking=True)

    # ─── Lignes de commande ───────────────────────────────────────────────────
    order_line_ids = fields.One2many(
        'barber.order.line', 'order_id', string='Prestations')

    # ─── Totaux ───────────────────────────────────────────────────────────────
    amount_untaxed = fields.Float(
        string='Sous-total HT', compute='_compute_amounts',
        store=True, digits=(10, 2))
    tax_rate = fields.Float(string='TVA (%)', default=0.0)
    amount_tax = fields.Float(
        string='TVA', compute='_compute_amounts',
        store=True, digits=(10, 2))
    amount_total = fields.Float(
        string='Total TTC', compute='_compute_amounts',
        store=True, digits=(10, 2))
    amount_paid = fields.Float(
        string='Montant payé', digits=(10, 2))
    amount_change = fields.Float(
        string='Rendu monnaie', compute='_compute_change',
        store=True, digits=(10, 2))

    # ─── Système VIP ──────────────────────────────────────────────────────────
    points_earned = fields.Float(string='Points gagnés', readonly=True)
    points_used = fields.Float(string='Points utilisés', default=0.0)
    points_amount = fields.Float(
        string='Remise Points (DZD)', compute='_compute_points_amount')

    # ─── Paiement ─────────────────────────────────────────────────────────────
    payment_method = fields.Selection([
        ('cash', '💵 Espèces'),
        ('card', '💳 Carte bancaire'),
        ('mobile', '📱 Paiement mobile'),
    ], string='Mode de paiement', default='cash', tracking=True)

    # ─── Statut ───────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft', '📝 En cours'),
        ('paid', '✅ Payé'),
        ('cancelled', '❌ Annulé'),
    ], string='État', default='draft', tracking=True)

    note = fields.Text(
        string='Remarques / Notes client')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Devise',
        related='company_id.currency_id', readonly=True)

    # ─── Compute ──────────────────────────────────────────────────────────────
    @api.depends('order_line_ids', 'order_line_ids.subtotal', 'tax_rate')
    def _compute_amounts(self):
        for order in self:
            subtotal = sum(order.order_line_ids.mapped('subtotal'))
            order.amount_untaxed = subtotal
            order.amount_tax = subtotal * (order.tax_rate / 100.0)
            order.amount_total = subtotal + order.amount_tax

    @api.depends('amount_paid', 'amount_total', 'points_amount')
    def _compute_change(self):
        for order in self:
            order.amount_change = max(
                0.0, (order.amount_paid + order.points_amount) - order.amount_total)

    @api.depends('points_used')
    def _compute_points_amount(self):
        config = self.env['barber.config'].get_current_config()
        for order in self:
            order.points_amount = order.points_used * config.vip_point_value

    @api.onchange('session_id')
    def _onchange_session(self):
        if self.session_id:
            self.barber_id = self.session_id.barber_id

    # ─── ORM overrides ────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'barber.order') or 'TKT-0001'
        return super().create(vals_list)

    # ─── Contraintes ──────────────────────────────────────────────────────────
    @api.constrains('order_line_ids')
    def _check_has_lines(self):
        for order in self:
            if order.state == 'paid' and not order.order_line_ids:
                raise ValidationError(
                    _('Impossible de valider une commande vide.'))

    # ─── Actions ──────────────────────────────────────────────────────────────
    def action_pay(self):
        """Lance le wizard de paiement."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Cette commande est déjà %s.') % self.state)
        if not self.order_line_ids:
            raise UserError(_('Ajoutez au moins une prestation avant de payer.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Paiement — %s') % self.name,
            'res_model': 'barber.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_amount_total': self.amount_total,
                'default_payment_method': self.payment_method,
            },
        }

    def action_confirm_payment(self, payment_method, amount_paid, points_used=0.0):
        """Confirme le paiement et clôture la commande."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Cette commande est déjà traitée.'))
        
        config = self.env['barber.config'].get_current_config()
        points_val = points_used * config.vip_point_value
        
        if (amount_paid + points_val) < self.amount_total:
            raise UserError(_(
                'Le montant total payé (%.2f + %.2f points = %.2f) est insuffisant. '
                'Total dû : %.2f DZD.'
            ) % (amount_paid, points_used, amount_paid + points_val, self.amount_total))

        # Vérifier si le client a assez de points
        if points_used > 0:
            if not self.partner_id:
                raise UserError(_('Un client doit être sélectionné pour utiliser des points VIP.'))
            if self.partner_id.vip_points < points_used:
                raise UserError(_('Le client n\'a pas assez de points (Dispo: %.2f).') % self.partner_id.vip_points)

        # Calcul des points gagnés
        earned = 0.0
        if config.enable_vip and self.partner_id:
            earned = (self.amount_total / 100.0) * config.vip_point_ratio

        self.write({
            'state': 'paid',
            'payment_method': payment_method,
            'amount_paid': amount_paid,
            'points_used': points_used,
            'points_earned': earned,
        })

        # Mettre à jour les points du partenaire
        if self.partner_id:
            self.partner_id.vip_points += (earned - points_used)
        
        return True

    def action_cancel(self):
        """Annule la commande."""
        self.ensure_one()
        if self.state == 'paid':
            raise UserError(_(
                'Impossible d\'annuler une commande déjà payée. '
                'Contactez l\'administrateur.'))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def action_print_receipt(self):
        """Imprime le ticket de caisse."""
        self.ensure_one()
        return self.env.ref('barber_pos.action_report_barber_receipt').report_action(self)

    def action_add_service(self, service_id, qty=1, unit_price=None, discount=0):
        """Ajoute une prestation à la commande (appelé depuis l'interface POS)."""
        self.ensure_one()
        service = self.env['barber.service'].browse(service_id)
        if not service.exists():
            raise UserError(_('Prestation introuvable.'))
        price = unit_price if unit_price is not None else service.price
        self.env['barber.order.line'].create({
            'order_id': self.id,
            'service_id': service_id,
            'qty': qty,
            'unit_price': price,
            'discount': discount,
        })

    @api.model
    def create_from_pos(self, vals):
        """
        Crée une commande et ses lignes depuis l'interface web POS.
        vals = { 'session_id': id, 'barber_id': id, 'partner_id': id, 'points_used': float, 'lines': [...] }
        """
        session = self.env['barber.session'].browse(vals.get('session_id'))
        if not session or session.state != 'open':
            raise UserError(_("La session est inexistante ou fermée."))

        order = self.create({
            'session_id': session.id,
            'barber_id': vals.get('barber_id'),
            'partner_id': vals.get('partner_id'),
            'state': 'draft', # On crée en draft puis on confirme
        })

        for line in vals.get('lines', []):
            self.env['barber.order.line'].create({
                'order_id': order.id,
                'service_id': line['service_id'],
                'qty': line.get('qty', 1),
                'unit_price': line.get('unit_price', 0.0),
            })
        
        # Confirmer le paiement avec points
        points_used = vals.get('points_used', 0.0)
        config = self.env['barber.config'].get_current_config()
        points_val = points_used * config.vip_point_value
        
        # Le montant payé réellement (cash/card) est le total moins les points
        amount_to_pay = max(0.0, order.amount_total - points_val)
        
        order.action_confirm_payment('cash', amount_to_pay, points_used)
        
        return order.name
