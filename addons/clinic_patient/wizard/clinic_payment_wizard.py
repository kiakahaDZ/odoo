# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ClinicPaymentWizard(models.TransientModel):
    _name = 'clinic.payment.wizard'
    _description = 'Assistant de Paiement (POS)'

    visit_id = fields.Many2one(
        'clinic.visit', string='Visite', required=True,
        default=lambda self: self.env.context.get('active_id')
    )
    total_amount = fields.Monetary(related='visit_id.total_amount', readonly=True)
    currency_id = fields.Many2one(related='visit_id.currency_id', readonly=True)
    
    payment_method = fields.Selection([
        ('cash', 'Espèces'),
        ('bank', 'Virement Bancaire'),
        ('check', 'Chèque'),
        ('insurance', 'Assurance / Tiers Payant'),
    ], string='Mode de Paiement', required=True, default='cash')

    def action_confirm_payment(self):
        """Valider le paiement (Appelé depuis le bouton Valider)"""
        self.ensure_one()
        self.visit_id.write({
            'payment_method': self.payment_method,
            # Le reste des champs (state, cashier, date) est géré par action_pay
        })
        return self.visit_id.action_pay()
