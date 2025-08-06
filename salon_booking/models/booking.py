from odoo import fields, models, api 

class SalonBooking(models.Model):
    _name = "salon.booking"
    _description = "Salon Booking"
    _rec_name = "booking_id"

    booking_id = fields.Char(string="Nomor Booking", default="New", readonly=True)
    customer = fields.Many2one("res.partner", string="Customer")
    booking_date = fields.Datetime(string="Jadwal Booking")
    end_date = fields.Datetime(string="Waktu Selesai", readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draf"),("konfirmasi","Dikonfirmasi"),("checkin","Check In"),("checkout","Checkout"),("batal","Dibatalkan")
            ],
        default="draft",
        string="Status"
    )

    service_id = fields.One2many("salon.service.temp", "booking_id", string="Layanan")
    package_id = fields.One2many("salon.package.temp", "booking_id", string="Paket Layanan")

    def action_konfirmasi(self):
        return self.write({"state": "konfirmasi"})
    def action_checkin(self):
        return self.write({"state": "checkin"})
    def action_checkout(self):
        return self.write({"state": "checkout"})
    def action_batal(self):
        return self.write({"state": "batal"})
    def action_draft(self):
        return self.write({"state": "draft"})   

    @api.model
    def create(self, vals):
        if vals.get('booking_id', 'New') == 'New':
            vals['booking_id'] = self.env['ir.sequence'].next_by_code('salon.booking') or 'New'
        return super(SalonBooking, self).create(vals)
