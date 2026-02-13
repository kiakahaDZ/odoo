from odoo import api, models, fields
from num2words import num2words

class LabInformation(models.Model):
    _name = 'lab.information'
    _description = 'Lab Information'
    _rec_name = 'lab_name'

    lab_name = fields.Char('Lab Name')
    street = fields.Char('Lab street')
    street1 = fields.Char('Lab street 1')
    city = fields.Char('Lab City')
    state_name = fields.Char('Lab State')
    lab_tel_no = fields.Char('Telephone number')
    gst_no = fields.Char('GST NO.')
    lab_logo = fields.Binary("LAB Logo")

class LabReport(models.Model):
    _name = 'lab.report'
    _description = 'Lab Report'

    lab_id = fields.Many2one('lab.information', string='Lab', required=True)
    patient_name = fields.Char('Patient Name')
    patient_age = fields.Char('Patient Age')
    patient_gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    patient_mobile = fields.Char('Mobile')
    patient_umr = fields.Char('UMR No')
    bill_no = fields.Char('Bill No')
    bill_date = fields.Date('Bill Date')
    visit_type = fields.Char('Visit type')
    ref_doctor = fields.Char('Ref Doctor')
    organization_name = fields.Char('Organization Name')
    gross_value = fields.Float('Gross Value',compute="_compute_gross_value", store=True)
    discount_value = fields.Float('Discount Value',compute="_compute_total_discount", store=True)
    paid_value = fields.Float('Paid Value',compute="_compute_paid_value", store=True)
    amount_in_words = fields.Char('Amount in Words')
    created_by = fields.Char('Created By')
    created_on = fields.Datetime('Created On')
    printed_by = fields.Char('Printed By')
    printed_on = fields.Datetime('Printed On')
    stamp = fields.Binary("LAB Stamp")  # Image field
    signature = fields.Binary("LAB Signature")
    services = fields.One2many('lab.report.service', 'report_id', string='Services')
    payments = fields.One2many('lab.report.payment', 'report_id', string='Payments')
    total_amount = fields.Float("Total", compute="_compute_total", store=True)
    amount_in_words = fields.Char("Amount in Words", compute="_compute_amount_in_words", store=True)


    @api.depends('services.sub_total')
    def _compute_total(self):
        """Compute total from all service subtotals"""
        for report in self:
            report.total_amount = sum(service.sub_total for service in report.services)

    @api.depends('services.qty', 'services.rate')
    def _compute_gross_value(self):
        """Gross = sum of qty * rate (ignoring discounts)"""
        for report in self:
            report.gross_value = sum(line.qty * line.rate for line in report.services)

    @api.depends('payments.amount')
    def _compute_paid_value(self):
        """Compute paid value = sum of all payment line amounts"""
        for report in self:
            report.paid_value = sum(payment.amount for payment in report.payments)

    @api.depends('services.disc_value')
    def _compute_total_discount(self):
        """Compute total discount from all service subdiscounts"""
        for report in self:
            report.discount_value = sum(service.disc_value for service in report.services)


    @api.depends('total_amount')
    def _compute_amount_in_words(self):
        for rec in self:
            if rec.total_amount:
                # Round to 2 decimals and split into integer/decimal parts
                integer_part = int(rec.total_amount)
                decimal_part = int(round((rec.total_amount - integer_part) * 100))

                # Convert integer part
                words = num2words(integer_part, lang='en').title()

                # Add currency text (here using Rupees / Paise, adjust if needed)
                if decimal_part > 0:
                    rec.amount_in_words = f"Rupees {words} And {num2words(decimal_part, lang='en').title()} Paise Only"
                else:
                    rec.amount_in_words = f"Rupees {words} Only"
            else:
                rec.amount_in_words = ""

class LabReportService(models.Model):
    _name = 'lab.report.service'
    _description = 'Lab Report Service'

    report_id = fields.Many2one('lab.report', string='Lab Report')
    index = fields.Integer('Index')
    # code = fields.Char('Code')
    name = fields.Char('Service Name')
    department = fields.Char('Department')
    qty = fields.Integer('Quantity')
    rate = fields.Float('Rate')
    disc_value = fields.Float('Discount Value')
    sub_total = fields.Float('Sub Total')


    @api.onchange('qty', 'rate', 'disc_value')
    def _compute_subtotal(self):
        """Compute subtotal = qty * rate - discount"""
        for line in self:
            subtotal = (line.qty * line.rate) - line.disc_value
            line.sub_total = subtotal if subtotal > 0 else 0.0

class LabReportPayment(models.Model):
    _name = 'lab.report.payment'
    _description = 'Lab Report Payment'

    index = fields.Integer('Index')
    report_id = fields.Many2one('lab.report', string='Lab Report')
    mode = fields.Char('Payment Mode')
    amount = fields.Float('Amount',compute="_compute_payment_amount",store=True)
    reference = fields.Char('Reference')

    @api.depends('report_id.total_amount')
    def _compute_payment_amount(self):
        """Distribute total amount equally across all payment lines"""
        for payment in self:
            if payment.report_id and payment.report_id.payments:
                total = payment.report_id.total_amount
                count = len(payment.report_id.payments)
                payment.amount = total / count if count else 0.0
            else:
                payment.amount = 0.0
