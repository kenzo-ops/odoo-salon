from odoo import api, fields, models

class BookingService(models.Model):
    _name = "salon.booking.service"
    _description = "Salon Booking Service"

    branch_id = fields.Many2one("salon.branches")
    booking_id = fields.Many2one("salon.booking")
    service_id = fields.Many2one("salon.services")
    service_description = fields.Char(related='service_id.description', string="Description", readonly=True)
    service_duration = fields.Integer(related='service_id.duration', string="Duration", readonly=True)
    service_price = fields.Float(related='service_id.harga', string="Price", readonly=True)
    service_category = fields.Many2one(related='service_id.category', string="Category", readonly=True)
    service_sub_category = fields.Many2one(related='service_id.sub_category', string="Sub Category", readonly=True)