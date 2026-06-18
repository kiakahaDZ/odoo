# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_vip = fields.Boolean(string='Client VIP', default=False)
    vip_points = fields.Float(string='Points Fidélité', default=0.0, tracking=True)
    vip_card_number = fields.Char(string='N° Carte VIP', copy=False)

    _vip_card_uniq = models.Constraint('unique(vip_card_number)', 'Le numéro de carte VIP doit être unique !')

    def action_view_barber_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commandes — %s') % self.name,
            'res_model': 'barber.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
        }
