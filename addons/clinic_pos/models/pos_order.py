# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        domain=[('is_patient', '=', True)],
        help='Patient associé à cette commande'
    )
    
    is_medical_order = fields.Boolean(
        string='Commande Médicale',
        compute='_compute_is_medical_order',
        store=True,
        help='Indique si c\'est une commande médicale'
    )

    @api.depends('config_id', 'config_id.is_medical_pos')
    def _compute_is_medical_order(self):
        """Détermine si c'est une commande médicale"""
        for order in self:
            order.is_medical_order = order.config_id.is_medical_pos

    @api.constrains('patient_id', 'config_id')
    def _check_patient_required(self):
        """Vérifie que le patient est renseigné si requis"""
        for order in self:
            if order.config_id.is_medical_pos and order.config_id.require_patient and not order.patient_id:
                raise ValidationError(_('Vous devez sélectionner un patient pour cette commande médicale!'))

    def _prepare_invoice_vals(self):
        """Ajoute le patient comme partenaire de facturation"""
        vals = super(PosOrder, self)._prepare_invoice_vals()
        if self.patient_id:
            vals['partner_id'] = self.patient_id.id
        return vals

    def action_pos_order_paid(self):
        """Marque les actes médicaux comme payés après paiement"""
        res = super(PosOrder, self).action_pos_order_paid()
        
        # Mettre à jour les actes médicaux associés
        if self.is_medical_order and self.patient_id:
            for line in self.lines:
                if line.product_id.is_medical_act:
                    # Rechercher ou créer l'acte médical
                    medical_act = self.env['clinic.medical.act.line'].search([
                        ('patient_id', '=', self.patient_id.id),
                        ('product_id', '=', line.product_id.id),
                        ('state', '=', 'waiting'),
                    ], limit=1)
                    
                    if medical_act:
                        medical_act.write({
                            'state': 'paid',
                            'pos_order_id': self.id,
                            'payment_date': fields.Datetime.now(),
                        })
                    else:
                        # Créer un nouvel acte médical
                        self.env['clinic.medical.act.line'].create({
                            'patient_id': self.patient_id.id,
                            'product_id': line.product_id.id,
                            'price_unit': line.price_unit,
                            'quantity': line.qty,
                            'state': 'paid',
                            'pos_order_id': self.id,
                            'payment_date': fields.Datetime.now(),
                        })
        
        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.constrains('product_id', 'order_id')
    def _check_medical_acts_only(self):
        """Vérifie que seuls les actes médicaux sont vendus si configuré"""
        for line in self:
            if line.order_id.config_id.is_medical_pos and line.order_id.config_id.medical_acts_only:
                if not line.product_id.is_medical_act:
                    raise ValidationError(
                        _('Seuls les actes médicaux peuvent être vendus dans cette caisse médicale!\n'
                          'Produit non autorisé: %s') % line.product_id.name
                    )
