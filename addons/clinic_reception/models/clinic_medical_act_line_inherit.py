# -*- coding: utf-8 -*-

from odoo import models, fields


class ClinicMedicalActLineInherit(models.Model):
    """Étendre clinic.medical.act.line avec le champ reception_id"""
    _inherit = 'clinic.medical.act.line'

    reception_id = fields.Many2one(
        'clinic.reception',
        string='Ticket de Reception',
        readonly=True,
        help='Ticket de réception associé'
    )
