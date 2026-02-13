# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ClinicPatientMedical(models.Model):
    _inherit = 'res.partner'

    # Relations avec les actes médicaux
    medical_act_ids = fields.One2many(
        'clinic.medical.act.line',
        'patient_id',
        string='Actes Médicaux',
        help='Historique des actes médicaux'
    )
    
    medical_act_count = fields.Integer(
        string='Nombre d\'Actes',
        compute='_compute_medical_act_count',
        help='Nombre total d\'actes médicaux'
    )
    
    # Statistiques
    total_spent = fields.Monetary(
        string='Total Dépensé',
        compute='_compute_total_spent',
        currency_field='currency_id',
        help='Montant total dépensé par le patient'
    )
    
    last_visit_date = fields.Datetime(
        string='Dernière Visite',
        compute='_compute_last_visit_date',
        store=True,
        help='Date de la dernière visite'
    )

    @api.depends('medical_act_ids')
    def _compute_medical_act_count(self):
        """Compte le nombre d'actes médicaux"""
        for patient in self:
            patient.medical_act_count = len(patient.medical_act_ids)

    @api.depends('medical_act_ids', 'medical_act_ids.price_total')
    def _compute_total_spent(self):
        """Calcule le total dépensé par le patient"""
        for patient in self:
            patient.total_spent = sum(patient.medical_act_ids.mapped('price_total'))

    @api.depends('medical_act_ids', 'medical_act_ids.date')
    def _compute_last_visit_date(self):
        """Détermine la date de la dernière visite"""
        for patient in self:
            if patient.medical_act_ids:
                patient.last_visit_date = max(patient.medical_act_ids.mapped('date'))
            else:
                patient.last_visit_date = False

    def action_view_medical_acts(self):
        """Action pour voir les actes médicaux du patient"""
        self.ensure_one()
        return {
            'name': f'Actes Médicaux - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'clinic.medical.act.line',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
