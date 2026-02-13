# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ClinicDoctor(models.Model):
    _name = 'clinic.doctor'
    _description = 'Médecin de la Clinique'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nom Complet',
        required=True,
        tracking=True,
        help='Nom complet du médecin (Dr. Nom Prénom)'
    )
    
    code = fields.Char(
        string='Code Médecin',
        required=True,
        copy=False,
        index=True,
        help='Code unique du médecin'
    )
    
    specialty = fields.Selection([
        ('general', 'Médecine Générale'),
        ('cardiology', 'Cardiologie'),
        ('traumatology', 'Traumatologie'),
        ('pediatrics', 'Pédiatrie'),
        ('gynecology', 'Gynécologie'),
        ('dermatology', 'Dermatologie'),
        ('ophthalmology', 'Ophtalmologie'),
        ('ent', 'ORL'),
        ('neurology', 'Neurologie'),
        ('psychiatry', 'Psychiatrie'),
        ('radiology', 'Radiologie'),
        ('laboratory', 'Laboratoire'),
        ('other', 'Autre'),
    ], string='Spécialité', required=True, tracking=True)
    
    specialty_other = fields.Char(
        string='Autre Spécialité',
        help='Préciser si "Autre" est sélectionné'
    )
    
    phone = fields.Char(string='Téléphone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    
    # Informations professionnelles
    license_number = fields.Char(
        string='N° Ordre',
        help='Numéro d\'inscription à l\'ordre des médecins'
    )
    
    # Partage des honoraires
    default_commission_rate = fields.Float(
        string='Taux Commission (%)',
        default=0.0,
        help='Pourcentage par défaut de la part du médecin (0-100)'
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True,
        help='Décocher pour archiver le médecin'
    )
    
    # Relations
    medical_act_ids = fields.One2many(
        'product.template',
        'doctor_id',
        string='Actes Médicaux'
    )
    
    notes = fields.Text(string='Notes')
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Le code médecin doit être unique!')
    ]

    @api.onchange('specialty')
    def _onchange_specialty(self):
        """Réinitialise specialty_other si la spécialité n'est pas 'other'"""
        if self.specialty != 'other':
            self.specialty_other = False
