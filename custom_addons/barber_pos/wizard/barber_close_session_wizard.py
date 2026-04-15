# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class BarberCloseSessionWizard(models.TransientModel):
    _name = 'barber.close.session.wizard'
    _description = 'Wizard de Fermeture de Session'

    session_id = fields.Many2one('barber.session', string='Session', required=True)
    cash_out = fields.Float(string='Montant Caisse', required=True)
    notes = fields.Text(string='Remarques de clôture')

    @api.onchange('session_id')
    def _onchange_session(self):
        if self.session_id:
            # Suggère le montant théorique
            self.cash_out = self.session_id.cash_in + self.session_id.total_cash

    def action_close(self):
        self.ensure_one()
        self.session_id.write({
            'state': 'closed',
            'cash_out': self.cash_out,
            'date_close': fields.Datetime.now(),
            'notes': self.notes,
        })
        return {'type': 'ir.actions.act_window_close'}
