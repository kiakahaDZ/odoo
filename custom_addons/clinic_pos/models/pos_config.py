# -*- coding: utf-8 -*-

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    is_medical_pos = fields.Boolean(
        string='Caisse Médicale',
        default=False,
        help='Cocher si ce POS est utilisé comme caisse médicale'
    )
    
    require_patient = fields.Boolean(
        string='Patient Obligatoire',
        default=True,
        help='Obliger la sélection d\'un patient avant paiement'
    )
    
    medical_acts_only = fields.Boolean(
        string='Actes Médicaux Uniquement',
        default=True,
        help='Limiter la vente aux actes médicaux uniquement'
    )
