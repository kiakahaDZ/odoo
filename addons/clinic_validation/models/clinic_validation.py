# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ClinicMedicalActLine(models.Model):
    _inherit = 'clinic.medical.act.line'

    medical_result = fields.Html(
        string='Résultat / Rapport',
        help='Résultat de l\'analyse ou compte-rendu de l\'imagerie'
    )
    
    performer_id = fields.Many2one(
        'res.users',
        string='Réalisé par',
        copy=False,
        help='Technicien ou médecin ayant réalisé l\'acte'
    )
    

        
    def action_validate(self):
        """Surcharge pour enregistrer le réalisateur"""
        res = super(ClinicMedicalActLine, self).action_validate()
        self.write({'performer_id': self.env.user.id})
        return res
