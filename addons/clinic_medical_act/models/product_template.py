# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Identifier si c'est un acte médical
    is_medical_act = fields.Boolean(
        string='Acte Médical',
        default=False,
        help='Cocher si ce produit est un acte médical'
    )
    
    # Type d'acte médical
    medical_act_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('laboratory', 'Laboratoire'),
        ('imaging', 'Imagerie Medicale'),
    ], string='Type d\'Acte', help='Type d\'acte médical')
    
    # Service concerné
    service_type = fields.Selection([
        ('general', 'Medecine Generale'),
        ('cardiology', 'Cardiologie'),
        ('traumatology', 'Traumatologie'),
        ('pediatrics', 'Pediatrie'),
        ('gynecology', 'Gynecologie'),
        ('dermatology', 'Dermatologie'),
        ('ophthalmology', 'Ophtalmologie'),
        ('ent', 'ORL'),
        ('neurology', 'Neurologie'),
        ('psychiatry', 'Psychiatrie'),
        ('radiology', 'Radiologie'),
        ('laboratory', 'Laboratoire'),
        ('imaging', 'Imagerie'),
        ('other', 'Autre'),
    ], string='Service')
    
    # Nécessite validation
    requires_validation = fields.Boolean(
        string='Nécessite Validation',
        default=False,
        help='Cocher si l\'acte nécessite une validation (labo, imagerie)'
    )
    
    # Médecin associé (pour les consultations)
    doctor_id = fields.Many2one(
        'clinic.doctor',
        string='Médecin',
        help='Médecin qui effectue la consultation'
    )
    
    # Partage des honoraires
    doctor_share_percentage = fields.Float(
        string='Part Médecin (%)',
        default=0.0,
        help='Pourcentage de la part du médecin (0-100)'
    )
    
    clinic_share_percentage = fields.Float(
        string='Part Clinique (%)',
        compute='_compute_clinic_share',
        store=True,
        help='Pourcentage de la part de la clinique'
    )
    
    doctor_share_amount = fields.Monetary(
        string='Montant Part Médecin',
        compute='_compute_share_amounts',
        store=True,
        currency_field='currency_id'
    )
    
    clinic_share_amount = fields.Monetary(
        string='Montant Part Clinique',
        compute='_compute_share_amounts',
        store=True,
        currency_field='currency_id'
    )

    @api.depends('doctor_share_percentage')
    def _compute_clinic_share(self):
        """Calcule automatiquement la part de la clinique"""
        for record in self:
            record.clinic_share_percentage = 100.0 - record.doctor_share_percentage

    @api.depends('list_price', 'doctor_share_percentage')
    def _compute_share_amounts(self):
        """Calcule les montants de partage"""
        for record in self:
            if record.is_medical_act and record.list_price:
                record.doctor_share_amount = record.list_price * (record.doctor_share_percentage / 100.0)
                record.clinic_share_amount = record.list_price * (record.clinic_share_percentage / 100.0)
            else:
                record.doctor_share_amount = 0.0
                record.clinic_share_amount = 0.0

    @api.constrains('doctor_share_percentage')
    def _check_doctor_share_percentage(self):
        """Valide que le pourcentage est entre 0 et 100"""
        for record in self:
            if record.doctor_share_percentage < 0 or record.doctor_share_percentage > 100:
                raise ValidationError(_('Le pourcentage de la part du médecin doit être entre 0 et 100!'))

    @api.onchange('medical_act_type')
    def _onchange_medical_act_type(self):
        """Configure les valeurs par défaut selon le type d'acte"""
        if self.medical_act_type == 'consultation':
            self.requires_validation = False
        elif self.medical_act_type in ['laboratory', 'imaging']:
            self.requires_validation = True
            self.doctor_share_percentage = 0.0

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        """Applique le taux de commission par défaut du médecin"""
        if self.doctor_id and self.doctor_id.default_commission_rate:
            self.doctor_share_percentage = self.doctor_id.default_commission_rate
