from odoo import fields, api, models

class ServiceTemp(models.Model):
    _name = "salon.package.temp"
    _description = "Salon Package Temp"

    booking_id = fields.Many2one("salon.booking")
    package_id = fields.Many2one("salon.packages", string="Paket")
    package_name = fields.Char(related='package_id.name', string="Nama Paket", store=True)
    package_description = fields.Char(related='package_id.description', string="Deskripsi Paket", store=True)
    package_state = fields.Selection(related='package_id.state', string="Status", store=True)
    package_harga = fields.Float(related='package_id.total_price', string="Harga Paket", store=True)
    package_start_date = fields.Date(related='package_id.start_date', string="Tanggal Berlaku", store=True)
    package_end_date = fields.Date(related='package_id.end_date', string="Tanggal Kadaluarsa", store=True)
