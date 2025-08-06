from odoo import fields, models, api 

class SalonBooking(models.Model):
    _name = "salon.booking"
    _description = "Salon Booking "

    booking_id = fields.Char(string="Nomor Booking", default="New", readonly=True)
    customer = fields.Many2one("res.partner", string="Customer")
    booking_date = fields.Datetime(string="Jadwal Booking")
    end_date = fields.Datetime(string="Waktu Selesai", readonly=True)
    services_id = fields.Many2many("salon.services", string="Layanan")

    @api.model
    def create(self, vals):
        if vals.get('booking_id', 'New') == 'New':
            vals['booking_id'] = self.env['ir.sequence'].next_by_code('salon.booking') or 'New'
        return super(SalonBooking, self).create(vals)
