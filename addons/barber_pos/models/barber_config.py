# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class BarberConfig(models.Model):
    _name = 'barber.config'
    _description = 'Configuration du Salon'
    _rec_name = 'salon_name'

    salon_name = fields.Char(
        string='Nom du Salon', required=True, default='Mon Salon')
    address = fields.Text(string='Adresse')
    phone = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')
    logo = fields.Binary(string='Logo', attachment=True)
    currency_id = fields.Many2one(
        'res.currency', string='Devise',
        default=lambda self: self.env.company.currency_id)
    tax_rate = fields.Float(string='Taux TVA (%)', default=0.0)
    receipt_header = fields.Text(
        string='En-tête ticket',
        default='Bienvenue dans notre salon !')
    receipt_footer = fields.Text(
        string='Pied de ticket',
        default='Merci de votre visite. À bientôt !')
    opening_time = fields.Float(string='Heure ouverture', default=8.0)
    closing_time = fields.Float(string='Heure fermeture', default=20.0)
    company_id = fields.Many2one(
        'res.company', string='Société',
        default=lambda self: self.env.company)

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_config', 'UNIQUE(company_id)',
         'Une seule configuration par société est autorisée.')
    ]

    @api.model
    def get_current_config(self):
        """Retourne la configuration active du salon."""
        config = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not config:
            config = self.create({'salon_name': self.env.company.name})
        return config
