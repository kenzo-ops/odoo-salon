from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError
import math

class SalonBooking(models.Model):
    _name = "salon.booking"
    _description = "Salon Booking"
    _rec_name = "customer"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    booking_id = fields.Char(string="Booking Number", default="New", readonly=True)
    customer = fields.Many2one("res.partner", string="Customer")
    customer_number = fields.Char(related="customer.phone", string="Phone Number", readonly=True, default="Enter customer data first")
    customer_address = fields.Char(related="customer.street", string="Adress", readonly=True, default="Enter customer data first")
    customer_email = fields.Char(related="customer.email", string="Email", readonly=True, default="Enter customer data first")
    booking_date = fields.Datetime(string="Booking Schedule", required=True)
    end_date = fields.Datetime(string="Finish Time", compute="_compute_end_date", store=True, readonly=True)
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
    total_price = fields.Float(string="Total Price", compute="_compute_total_price", store=True, readonly=True)
    invoice_id = fields.Many2one("account.move", string="Invoice", readonly=True)

    attendee_ids = fields.Many2many(
        "res.partner",
        "salon_booking_res_partner_rel",
        "booking_id", "partner_id",
        string="Attendees"
    )

    staff_id = fields.Many2one("salon.staff", string="Assigned Staff")
    branch_id = fields.Many2one("salon.branches", string="Branch Offices")
    service_booking_id = fields.One2many("salon.booking.service", "booking_id", string="Services")
    package_booking_id = fields.One2many("salon.booking.package", "booking_id", string="Packages")
    working_hours = fields.Many2one(related='branch_id.working_hours_id', string="Working Hours")
    room_ids = fields.Many2many(
        "salon.room",
        string="Rooms",
        compute="_compute_room_ids",
        store=True,
        readonly=True
    )
    can_edit = fields.Boolean(compute="_compute_can_edit", store=False)

    # ==== Proteksi edit ====
    @api.depends("state")
    def _compute_can_edit(self):
        for rec in self:
            rec.can_edit = rec.state != "konfirmasi"

    def write(self, vals):
        """Proteksi backend"""
        for rec in self:
            if rec.state == "konfirmasi":
                if not ("state" in vals and vals["state"] == "draft"):
                    raise ValidationError(
                        "Confirmed booking data cannot be changed.\n"
                        "If you want to change it, please reset it back to Draft."
                    )
        return super(SalonBooking, self).write(vals)

    @api.onchange("customer", "booking_date", "staff_id", "branch_id", "service_booking_id", "package_booking_id")
    def _onchange_block_edit_when_confirmed(self):
        """Proteksi frontend"""
        if self.state == "konfirmasi":
            # ambil nilai lama dari record di database
            original = self.browse(self._origin.id)

            # kembalikan field ke nilai aslinya
            self.customer = original.customer
            self.booking_date = original.booking_date
            self.staff_id = original.staff_id
            self.branch_id = original.branch_id
            self.service_booking_id = original.service_booking_id
            self.package_booking_id = original.package_booking_id

            return {
                "warning": {
                    "title": "Booking Locked",
                    "message": (
                        "Confirmed booking data cannot be changed.\n"
                        "If you want to change it, please reset it back to Draft."
                    ),
                }
            }

    @api.depends("service_booking_id.service_id.room_id", "package_booking_id.package_id.room_ids")
    def _compute_room_ids(self):
        for rec in self:
            # ambil semua room dari services
            service_rooms = rec.service_booking_id.mapped("service_id.room_id")
            # ambil semua room dari packages
            package_rooms = rec.package_booking_id.mapped("package_id.room_ids")
            # gabungkan semuanya
            all_rooms = service_rooms | package_rooms
            rec.room_ids = [(6, 0, all_rooms.ids)] if all_rooms else [(5, 0, 0)]


    # ==== Onchange schedule & staff ====
    @api.onchange('staff_id', 'booking_date')
    def _onchange_staff_schedule_check(self):
        if self.staff_id and self.booking_date:
            employee = self.staff_id.branch_staff_ids
            if not employee or not employee.resource_calendar_id:
                return
            calendar = employee.resource_calendar_id
            booking_local = fields.Datetime.context_timestamp(self, self.booking_date)
            weekday = str(booking_local.weekday())
            attendances = calendar.attendance_ids.filtered(lambda a: a.dayofweek == weekday)

            if not attendances:
                return {'warning': {'title': "Not Working", 'message': f"{employee.name} not working on {booking_local.strftime('%A')}."}}

            booking_hour = booking_local.hour + booking_local.minute / 60.0
            valid = any(att.hour_from <= booking_hour <= att.hour_to for att in attendances)

            if not valid:
                hour_list = ", ".join([
                    f"{int(a.hour_from):02d}:{int((a.hour_from % 1) * 60):02d} - "
                    f"{int(a.hour_to):02d}:{int((a.hour_to % 1) * 60):02d}"
                    for a in attendances
                ])
                self.booking_date = False
                return {
                    'warning': {
                        'title': "Outside Working Hours",
                        'message': f"Booking hours must be between {hour_list} for {employee.name}."
                    }
                }

    @api.onchange('booking_date', 'branch_id')
    def _onchange_booking_date_check_hours(self):
        if self.branch_id and self.branch_id.working_hours_id and self.booking_date:
            wh = self.branch_id.working_hours_id
            booking_dt = fields.Datetime.context_timestamp(self, self.booking_date)
            booking_hour = booking_dt.hour + booking_dt.minute / 60.0
            if booking_hour < wh.working_start or booking_hour > wh.working_end:
                self.booking_date = False
                return {
                    'warning': {
                        'title': "Invalid Booking Time",
                        'message': (f"Booking must be between {int(wh.working_start):02d}:{int((wh.working_start % 1) * 60):02d} "
                                    f"and {int(wh.working_end):02d}:{int((wh.working_end % 1) * 60):02d}")
                    }
                }

    @api.onchange('staff_id', 'booking_date')
    def _onchange_staff_leave_check(self):
        if self.staff_id and self.booking_date:
            employee = self.staff_id.branch_staff_ids
            if employee:
                leave_exists = self.env['hr.leave'].search_count([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'validate'),
                    ('request_date_from', '<=', self.booking_date.date()),
                    ('request_date_to', '>=', self.booking_date.date()),
                ]) > 0
                if leave_exists:
                    self.staff_id = False
                    return {
                        'warning': {
                            'title': "Staff on Leave",
                            'message': f"Staff {employee.name} sedang cuti pada {self.booking_date.date()}."
                        }
                    }

    # ==== Compute fields ====
    @api.depends('booking_date','service_booking_id.service_duration','package_booking_id.package_duration')
    def _compute_end_date(self):
        for rec in self:
            if rec.booking_date:
                total_duration = sum(service.service_duration or 0 for service in rec.service_booking_id)
                total_duration += sum(pkg.package_duration or 0 for pkg in rec.package_booking_id)
                rec.end_date = rec.booking_date + timedelta(minutes=total_duration) if total_duration > 0 else False
            else:
                rec.end_date = False

    @api.depends('service_booking_id.service_price', 'package_booking_id.package_total_price')
    def _compute_total_price(self):
        for rec in self:
            total_services = sum(service.service_price or 0 for service in rec.service_booking_id)
            total_packages = sum(pkg.package_total_price or 0 for pkg in rec.package_booking_id)
            rec.total_price = total_services + total_packages

    # ==== State actions ====
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
        for rec in self:
            if rec.invoice_id and rec.invoice_id.state != 'draft':
                rec.invoice_id.button_draft()

    # ==== Invoice ====
    def _create_invoice(self):
        for rec in self:
            if not rec.customer:
                return {'warning': {'title': "Customer has not been selected", 'message': f"Customer has not been selected, cannot create invoice."}}

            if rec.invoice_id:
                continue

            invoice_lines = []
            for service in rec.service_booking_id:
                invoice_lines.append((0, 0, {'name': service.service_id.name or 'Service', 'quantity': 1, 'price_unit': service.service_price or 0}))
            for package in rec.package_booking_id:
                invoice_lines.append((0, 0, {'name': package.package_name or 'Package', 'quantity': 1, 'price_unit': package.package_total_price or 0}))

            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': rec.customer.id,
                'invoice_date': fields.Date.today(),
                'invoice_origin': rec.booking_id,
                'booking_id': rec.id,
                'invoice_line_ids': invoice_lines
            }
            invoice = self.env['account.move'].create(move_vals)
            invoice.action_post()
            rec.invoice_id = invoice.id

    @api.model
    def create(self, vals):
        if vals.get('booking_id', 'New') == 'New':
            vals['booking_id'] = self.env['ir.sequence'].next_by_code('salon.booking') or 'New'
        record = super(SalonBooking, self).create(vals)
        record._create_invoice()
        return record

    invoice_ids = fields.One2many("account.move", "booking_id",string="Invoices", readonly=True)
    invoice_count = fields.Integer(string="Total Invoices", compute="_compute_invoice_count", store=False)

    @api.depends("invoice_ids") 
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }