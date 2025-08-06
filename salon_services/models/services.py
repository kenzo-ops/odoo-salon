from odoo import api, fields, models

class Services(models.Model):
    _name = "salon.services"
    _description = "Salon Services"

    name = fields.Char(string="Nama Layanan", required=True)
    description = fields.Char(string="Deskripsi Layanan", required=True)
    duration = fields.Integer(string="Durasi Layanan (Menit)", required=True)
    harga = fields.Float(string="Harga Layanan", required=True)
    category = fields.Many2one('salon.service.category', string="Kategori", required=True)
    sub_category = fields.Many2one('salon.sub.category', string="Sub Kategori", required=True)
    packages_id = fields.Many2one('salon.packages')