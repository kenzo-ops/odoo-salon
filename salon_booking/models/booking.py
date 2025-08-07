from odoo import fields, models, api 

class SalonBooking(models.Model):
    _name = "salon.booking"
    _description = "Salon Booking"
    _rec_name = "booking_id"

    booking_id = fields.Char(string="Nomor Booking", default="New", readonly=True)
    customer = fields.Many2one("res.partner", string="Customer")
    customer_number = fields.Char(related="customer.phone", string="Nomor Telepon", readonly=True)
    customer_address = fields.Char(related="customer.street", string="Alamat", readonly=True)
    customer_email = fields.Char(related="customer.email", string="Email", readonly=True)
    booking_date = fields.Datetime(string="Jadwal Booking")
    end_date = fields.Datetime(string="Waktu Selesai", readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draf"),("konfirmasi","Dikonfirmasi"),("checkin","Check In"),("checkout","Checkout"),("batal","Dibatalkan")
            ],
        default="draft",
        string="Status"
    )
    total_price = fields.Float(string="Total Harga", compute="_compute_total_price", store=True, readonly=True)


    service_id = fields.One2many("salon.service.temp", "booking_id", string="Layanan")
    package_id = fields.One2many("salon.package.temp", "booking_id", string="Paket Layanan")

    @api.depends('service_id.service_harga', 'package_id.package_harga')
    def _compute_total_price(self):
        for rec in self:
            total_services = sum(rec.service_id.mapped('service_harga'))
            total_packages = sum(rec.package_id.mapped('package_harga'))
            rec.total_price = total_services + total_packages

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
