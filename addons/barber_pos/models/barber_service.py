# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BarberServiceCategory(models.Model):
    _name = 'barber.service.category'
    _description = 'Catégorie de Prestation'
    _order = 'sequence, name'

    name = fields.Char(string='Catégorie', required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Couleur', default=0)
    icon = fields.Char(string='Icône', default='✂️',
                       help='Emoji ou classe CSS (ex: ✂️, 🪒, 💆)')
    description = fields.Text(string='Description')
    service_ids = fields.One2many(
        'barber.service', 'category_id', string='Prestations')
    service_count = fields.Integer(
        string='Nb Prestations', compute='_compute_service_count')
    active = fields.Boolean(default=True)

    @api.depends('service_ids')
    def _compute_service_count(self):
        for cat in self:
            cat.service_count = len(cat.service_ids)


class BarberServiceProduct(models.Model):
    """Produits consommés lors d'une prestation."""
    _name = 'barber.service.product'
    _description = 'Produit utilisé dans la prestation'

    service_id = fields.Many2one(
        'barber.service', string='Prestation',
        required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', string='Produit',
        required=True,
        domain=[('type', 'in', ['consu', 'product'])])
    product_name = fields.Char(
        related='product_id.name', readonly=True)
    qty = fields.Float(
        string='Quantité utilisée', required=True, default=1.0)
    uom_id = fields.Many2one(
        related='product_id.uom_id', string='Unité', readonly=True)
    cost = fields.Float(
        string='Coût unitaire', related='product_id.standard_price',
        readonly=True)
    total_cost = fields.Float(
        string='Coût total', compute='_compute_total_cost')
    notes = fields.Char(string='Remarques')

    @api.depends('qty', 'cost')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.qty * line.cost


class BarberService(models.Model):
    _name = 'barber.service'
    _description = 'Prestation / Service du Salon'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'sequence, category_id, name'

    # ─── Identification ───────────────────────────────────────────────────────
    name = fields.Char(string='Nom de la prestation', required=True,
                       translate=True, tracking=True)
    code = fields.Char(string='Code court', help='Ex: COUPE-H, BARBE, SOIN')
    sequence = fields.Integer(default=10)

    # ─── Catégorie & Visuel ───────────────────────────────────────────────────
    category_id = fields.Many2one(
        'barber.service.category', string='Catégorie', tracking=True)
    image = fields.Binary(string='Image', attachment=True)
    color = fields.Integer(string='Couleur', default=0)
    description = fields.Text(string='Description')

    # ─── Tarification ─────────────────────────────────────────────────────────
    price = fields.Float(
        string='Prix (DZD)', required=True, tracking=True,
        digits=(10, 2))
    price_min = fields.Float(
        string='Prix minimum', default=0.0,
        help='Prix plancher en cas de remise accordée.')
    allow_price_override = fields.Boolean(
        string='Prix modifiable en caisse',
        default=True,
        help='Permet au coiffeur de modifier le prix lors de la saisie.')
    duration = fields.Integer(
        string='Durée (min)', default=30,
        help='Durée estimée de la prestation en minutes.')

    # ─── Produits consommés ───────────────────────────────────────────────────
    product_line_ids = fields.One2many(
        'barber.service.product', 'service_id',
        string='Produits consommés')
    material_cost = fields.Float(
        string='Coût matières', compute='_compute_material_cost',
        store=True, digits=(10, 2))
    margin = fields.Float(
        string='Marge (%)', compute='_compute_margin', store=True)

    # ─── Devise ────────────────────────────────────────────────────────────────
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string='Devise',
        related='company_id.currency_id', readonly=True)

    # ─── Statut ───────────────────────────────────────────────────────────────
    active = fields.Boolean(default=True, tracking=True)
    barber_type = fields.Selection([
        ('both', '✂️ Coiffure & Barbier'),
        ('hair', '💇 Coiffure uniquement'),
        ('barber', '🪒 Barbier uniquement'),
        ('care', '💆 Soins & Beauté'),
    ], string='Type de service', default='both')

    # ─── Statistiques ─────────────────────────────────────────────────────────
    order_count = fields.Integer(
        string='Fois commandée', compute='_compute_order_count')

    # ─── Compute ──────────────────────────────────────────────────────────────
    @api.depends('product_line_ids', 'product_line_ids.total_cost')
    def _compute_material_cost(self):
        for svc in self:
            svc.material_cost = sum(
                svc.product_line_ids.mapped('total_cost'))

    @api.depends('price', 'material_cost')
    def _compute_margin(self):
        for svc in self:
            if svc.price > 0:
                svc.margin = ((svc.price - svc.material_cost) / svc.price) * 100
            else:
                svc.margin = 0.0

    def _compute_order_count(self):
        OrderLine = self.env['barber.order.line']
        for svc in self:
            svc.order_count = OrderLine.search_count([
                ('service_id', '=', svc.id),
                ('order_id.state', '=', 'paid'),
            ])

    # ─── Contraintes ──────────────────────────────────────────────────────────
    @api.constrains('price')
    def _check_price(self):
        for svc in self:
            if svc.price < 0:
                raise ValidationError(_('Le prix ne peut pas être négatif.'))

    @api.constrains('price', 'price_min')
    def _check_price_min(self):
        for svc in self:
            if svc.price_min > svc.price:
                raise ValidationError(
                    _('Le prix minimum ne peut pas dépasser le prix standard.'))

    # ─── Actions ──────────────────────────────────────────────────────────────
    def action_archive(self):
        self.write({'active': False})

    def action_unarchive(self):
        self.write({'active': True})

    def action_view_orders(self):
        lines = self.env['barber.order.line'].search([
            ('service_id', '=', self.id)])
        order_ids = lines.mapped('order_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commandes — %s') % self.name,
            'res_model': 'barber.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', order_ids)],
        }
