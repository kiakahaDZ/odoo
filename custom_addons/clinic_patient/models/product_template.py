# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_medical_act = fields.Boolean(
        string='Est un Acte Médical',
        default=False,
        help='Cocher si ce produit est un acte médical'
    )

    medical_act_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('laboratory', 'Laboratoire'),
        ('imaging', 'Imagerie'),
        ('surgery', 'Chirurgie'),
        ('nursing', 'Soins Infirmiers'),
        ('other', 'Autre')
    ], string="Type d'Acte", help="Type de l'acte médical")

    service_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('analysis', 'Analyse'),
        ('imaging', 'Imagerie'),
        ('procedure', 'Procédure'),
        ('other', 'Autre')
    ], string='Type de Service', help='Catégorie du service')

    doctor_share_percentage = fields.Float(
        string='Part Médecin (%)',
        default=0.0,
        help='Pourcentage reversé au médecin'
    )

    clinic_share_percentage = fields.Float(
        string='Part Clinique (%)',
        default=100.0,
        help='Pourcentage conservé par la clinique'
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Related field so we can filter product.product with domain
    is_medical_act = fields.Boolean(
        related='product_tmpl_id.is_medical_act',
        store=True,
    )
