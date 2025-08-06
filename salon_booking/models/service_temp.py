from odoo import fields, api, models

class ServiceTemp(models.Model):
    _name = "salon.service.temp"
    _description = "Salon Service Temp"

    booking_id = fields.Many2one("salon.booking")
    services_id = fields.Many2one("salon.services", string="Layanan")
    service_name = fields.Char(related='services_id.name', string="Nama Layanan", store=True)
    service_description = fields.Char(related='services_id.description', string="Deskripsi Layanan", store=True)
    service_duration = fields.Integer(related='services_id.duration', string="Durasi Layanan", store=True)
    service_harga = fields.Float(related='services_id.harga', string="Harga Layanan", store=True)
    service_category = fields.Many2one(related='services_id.category', string="Kategori Layanan", store=True)
    service_sub_category = fields.Many2one(related='services_id.sub_category', string="Sub Kategori Layanan", store=True)
