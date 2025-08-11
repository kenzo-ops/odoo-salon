from odoo import fields, models, api
from datetime import timedelta

class SalonBooking(models.Model):
    _name = "salon.booking"
    _description = "Salon Booking"
    _rec_name = "booking_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    booking_id = fields.Char(string="Nomor Booking", default="New", readonly=True)
    customer = fields.Many2one("res.partner", string="Customer")
    customer_number = fields.Char(related="customer.phone", string="Nomor Telepon", readonly=True)
    customer_address = fields.Char(related="customer.street", string="Alamat", readonly=True)
    customer_email = fields.Char(related="customer.email", string="Email", readonly=True)
    booking_date = fields.Datetime(string="Jadwal Booking")
    end_date = fields.Datetime(string="Waktu Selesai", compute="_compute_end_date", store=True, readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("konfirmasi", "Confirmed"),
            ("checkin", "Check In"),
            ("checkout", "Checkout"),
            ("batal", "Canceled")
        ],
        default="draft",
        string="Status"
    )
    total_price = fields.Float(string="Total Harga", compute="_compute_total_price", store=True, readonly=True)

    service_booking_id = fields.One2many("salon.booking.service", "booking_id", string="Services")
    package_booking_id = fields.One2many("salon.booking.package", "booking_id", string="Packages")

    @api.depends('booking_date', 'service_booking_id.service_duration')
    def _compute_end_date(self):
        for rec in self:
            if rec.booking_date and rec.service_booking_id:
                total_duration = sum(
                    service.service_duration or 0
                    for service in rec.service_booking_id
                )
                rec.end_date = rec.booking_date + timedelta(minutes=total_duration)
            else:
                rec.end_date = False

    @api.depends('service_booking_id.service_price', 'package_booking_id.package_total_price')
    def _compute_total_price(self):
        for rec in self:
            total_services = sum(service.service_price or 0 for service in rec.service_booking_id)
            total_packages = sum(pkg.package_total_price or 0 for pkg in rec.package_booking_id)
            rec.total_price = total_services + total_packages

    def action_konfirmasi(self):
        self.write({"state": "konfirmasi"})

    def action_checkin(self):
        self.write({"state": "checkin"})

    def action_checkout(self):
        self.write({"state": "checkout"})

    def action_batal(self):
        self.write({"state": "batal"})

    def action_draft(self):
        self.write({"state": "draft"})

    @api.model
    def create(self, vals):
        if vals.get('booking_id', 'New') == 'New':
            vals['booking_id'] = self.env['ir.sequence'].next_by_code('salon.booking') or 'New'
        return super(SalonBooking, self).create(vals)
