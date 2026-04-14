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
    amount_change = fields.Float(string='Monnaie à rendre', compute='_compute_change')
    
    @api.depends('amount_total', 'amount_paid')
    def _compute_change(self):
        for wiz in self:
            wiz.amount_change = max(0.0, wiz.amount_paid - wiz.amount_total)

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        if self.amount_total and not self.amount_paid:
            self.amount_paid = self.amount_total

    def action_confirm(self):
        self.ensure_one()
        if self.amount_paid < self.amount_total:
            raise UserError(_('Le montant reçu ne peut pas être inférieur au total.'))
        
        self.order_id.action_confirm_payment(self.payment_method, self.amount_paid)
        
        # Option: imprimer le ticket directement après paiement
        return self.order_id.action_print_receipt()
