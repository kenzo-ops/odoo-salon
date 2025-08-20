from odoo import api, fields, models

class BookingPackage(models.Model):
    _name = "salon.booking.package"
    _description = "Salon Booking Package"

    booking_id = fields.Many2one("salon.booking", ondelete="cascade",)
    package_id = fields.Many2one("salon.packages", string="Package", required=True)
    package_description = fields.Char(related='package_id.description', string="Description")
    package_state = fields.Selection(related='package_id.state', string="Status")
    package_total_price = fields.Float(related='package_id.total_price', string="Total Price")
    package_start_date = fields.Date(related='package_id.start_date', string="Start Date")
    package_end_date = fields.Date(related='package_id.end_date', string="End Date")
    package_duration = fields.Integer(related='package_id.duration', string="Duration (Minutes)")