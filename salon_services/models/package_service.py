from odoo import fields, models, api

class PackageService(models.Model):
    _name = "salon.package.service"
    _description = "Salon Package Service"

    service_id = fields.Many2one("salon.services", string="Layanan", required=True)
    service_price = fields.Float(related='service_id.harga', store=True, readonly=True)
    discount = fields.Float(string="Diskon (%)", required=True, default=0)
    quantity = fields.Integer(string="Jumlah", required=True, default=1)
    total_price = fields.Float(string="Harga Total", compute="_compute_total_price", store=True, readonly=True)
    packages_id = fields.Many2one("salon.packages")

    @api.depends('service_price', 'quantity', 'discount')
    def _compute_total_price(self):
        for rec in self:
            price = rec.service_price * rec.quantity
            rec.total_price = price * (1 - (rec.discount / 100))
