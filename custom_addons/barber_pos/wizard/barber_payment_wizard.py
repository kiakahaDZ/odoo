# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BarberPaymentWizard(models.TransientModel):
    _name = 'barber.payment.wizard'
    _description = 'Wizard de Paiement POS'

    order_id = fields.Many2one('barber.order', string='Commande', required=True)
    amount_total = fields.Float(string='Total à payer', readonly=True)
    payment_method = fields.Selection([
        ('cash', '💵 Espèces'),
        ('card', '💳 Carte bancaire'),
        ('mobile', '📱 Paiement mobile'),
    ], string='Mode de paiement', required=True, default='cash')
    amount_paid = fields.Float(string='Montant reçu', required=True)
    points_used = fields.Float(string='Points VIP utilisés', default=0.0)
    partner_id = fields.Many2one(related='order_id.partner_id', readonly=True)
    partner_points = fields.Float(related='partner_id.vip_points', readonly=True)
    amount_change = fields.Float(string='Monnaie à rendre', compute='_compute_change')
    
    @api.depends('amount_total', 'amount_paid', 'points_used', 'order_id')
    def _compute_change(self):
        config = self.env['barber.config'].get_current_config()
        for wiz in self:
            points_val = wiz.points_used * config.vip_point_value
            wiz.amount_change = max(0.0, (wiz.amount_paid + points_val) - wiz.amount_total)

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        if self.amount_total and not self.amount_paid:
            self.amount_paid = self.amount_total

    def action_confirm(self):
        self.ensure_one()
        config = self.env['barber.config'].get_current_config()
        points_val = self.points_used * config.vip_point_value

        if (self.amount_paid + points_val) < self.amount_total:
            raise UserError(_('Le montant total (Espèces + Points) ne peut pas être inférieur au total dû.'))
        
        self.order_id.action_confirm_payment(self.payment_method, self.amount_paid, self.points_used)
        
        return self.order_id.action_print_receipt()
