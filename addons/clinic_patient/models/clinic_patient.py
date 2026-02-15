# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ClinicPatient(models.Model):
    _inherit = 'res.partner'
    _description = 'Patient de la Clinique'

    # ==========================================
    # IDENTIFICATION PATIENT
    # ==========================================
    is_patient = fields.Boolean(
        string='Est un Patient',
        default=False,
        help='Cocher si ce contact est un patient de la clinique'
    )

    is_doctor = fields.Boolean(
        string='Est un Médecin',
        default=False,
        help='Cocher si ce contact est un médecin/praticien'
    )

    # Numéro de dossier patient unique
    patient_number = fields.Char(
        string='N° Dossier Patient',
        readonly=True,
        copy=False,
        index=True,
        help='Numéro unique du dossier patient'
    )

    # ==========================================
    # INFORMATIONS PERSONNELLES PATIENT
    # ==========================================
    date_of_birth = fields.Date(
        string='Date de Naissance',
        help='Date de naissance du patient'
    )

    age = fields.Integer(
        string='Âge',
        compute='_compute_age',
        store=True,
        help='Âge calculé automatiquement'
    )

    gender = fields.Selection([
        ('male', 'Masculin'),
        ('female', 'Féminin'),
        ('other', 'Autre')
    ], string='Sexe', help='Sexe du patient')

    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
    ], string='Groupe Sanguin')

    # ==========================================
    # CONTACTS D'URGENCE
    # ==========================================
    emergency_contact = fields.Char(
        string="Contact d'Urgence",
        help="Nom du contact en cas d'urgence"
    )

    emergency_phone = fields.Char(
        string="Téléphone d'Urgence",
        help="Numéro de téléphone du contact d'urgence"
    )

    # ==========================================
    # INFORMATIONS MÉDICALES
    # ==========================================
    allergies = fields.Text(
        string='Allergies',
        help='Liste des allergies connues'
    )

    chronic_diseases = fields.Text(
        string='Maladies Chroniques',
        help='Maladies chroniques du patient'
    )

    medical_notes = fields.Text(
        string='Notes Médicales',
        help='Notes médicales importantes'
    )

    # ==========================================
    # ASSURANCE
    # ==========================================
    insurance_company = fields.Char(
        string='Assurance',
        help="Nom de la compagnie d'assurance (CNAS, etc.)"
    )

    insurance_number = fields.Char(
        string='N° Assurance',
        help="Numéro d'assuré social"
    )

    # ==========================================
    # STATUT & DEVISE
    # ==========================================
    patient_status = fields.Selection([
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('archived', 'Archivé')
    ], string='Statut', default='active')

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )

    # ==========================================
    # CHAMPS MÉDECIN / PRATICIEN
    # ==========================================
    doctor_specialty = fields.Selection([
        ('general', 'Médecine Générale'),
        ('laboratory', 'Laboratoire'),
        ('imaging', 'Imagerie / Radiologie'),
        ('surgery', 'Chirurgie'),
        ('cardiology', 'Cardiologie'),
        ('pediatrics', 'Pédiatrie'),
        ('gynecology', 'Gynécologie'),
        ('ophthalmology', 'Ophtalmologie'),
        ('dermatology', 'Dermatologie'),
        ('other', 'Autre'),
    ], string='Spécialité', help='Spécialité du médecin')

    doctor_license = fields.Char(
        string='N° Ordre des Médecins',
        help="Numéro d'inscription à l'ordre des médecins"
    )

    # ==========================================
    # RELATIONS - VISITES
    # ==========================================
    visit_ids = fields.One2many(
        'clinic.visit', 'patient_id',
        string='Visites',
        help='Historique des visites du patient'
    )

    visit_count = fields.Integer(
        string='Nombre de Visites',
        compute='_compute_visit_count',
        store=True,
    )

    # ==========================================
    # MÉTHODES
    # ==========================================

    @api.model_create_multi
    def create(self, vals_list):
        """Génère automatiquement un numéro de dossier patient"""
        for vals in vals_list:
            if vals.get('is_patient', False) and not vals.get('patient_number'):
                vals['patient_number'] = self.env['ir.sequence'].next_by_code(
                    'clinic.patient.sequence'
                ) or 'PAT/NEW'
        return super(ClinicPatient, self).create(vals_list)

    @api.depends('date_of_birth')
    def _compute_age(self):
        """Calcule l'âge du patient"""
        from datetime import date
        for patient in self:
            if patient.date_of_birth:
                today = date.today()
                born = patient.date_of_birth
                patient.age = today.year - born.year - (
                    (today.month, today.day) < (born.month, born.day)
                )
            else:
                patient.age = 0

    @api.depends('visit_ids')
    def _compute_visit_count(self):
        """Calcule le nombre de visites du patient"""
        for patient in self:
            patient.visit_count = len(patient.visit_ids)

    @api.constrains('patient_number')
    def _check_patient_number_unique(self):
        """Vérifie l'unicité du numéro de dossier patient"""
        for patient in self:
            if patient.patient_number:
                duplicate = self.search([
                    ('patient_number', '=', patient.patient_number),
                    ('id', '!=', patient.id)
                ])
                if duplicate:
                    raise ValidationError(
                        f"Le numéro de dossier {patient.patient_number} "
                        f"existe déjà pour {duplicate.name}!"
                    )
