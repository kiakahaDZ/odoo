# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ClinicReceptionLine(models.Model):
    _name = 'clinic.reception.line'
    _description = 'Ligne de Réception'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Séquence', default=10)
    
    reception_id = fields.Many2one(
        'clinic.reception',
        string='Réception',
        required=True,
        ondelete='cascade',
        help='Ticket de réception associé'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Acte Médical',
        required=True,
        domain=[('is_medical_act', '=', True)],
        help='Acte médical demandé'
    )
    
    # Champs liés au produit
    medical_act_type = fields.Selection(
        related='product_id.product_tmpl_id.medical_act_type',
        string='Type',
        readonly=True
    )
    
    service_type = fields.Selection(
        related='product_id.product_tmpl_id.service_type',
        string='Service',
        readonly=True
    )
    
    doctor_id = fields.Many2one(
        related='product_id.product_tmpl_id.doctor_id',
        string='Médecin',
        readonly=True
    )
    
    # Prix
    price_unit = fields.Monetary(
        string='Prix Unitaire',
        required=True,
        currency_field='currency_id'
    )
    
    quantity = fields.Float(
        string='Quantité',
        default=1.0,
        required=True
    )
    
    price_total = fields.Monetary(
        string='Total',
        compute='_compute_price_total',
        store=True,
        currency_field='currency_id'
    )
    
    # Devise
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )
    
    # Notes
    notes = fields.Char(string='Notes')

    @api.depends('price_unit', 'quantity')
    def _compute_price_total(self):
        """Calcule le prix total"""
        for line in self:
            line.price_total = line.price_unit * line.quantity

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Met à jour le prix unitaire selon le produit"""
        if self.product_id:
            self.price_unit = self.product_id.list_price
