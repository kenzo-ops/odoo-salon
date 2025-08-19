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
    customer_number = fields.Char(related="customer.phone", string="Phone Number", readonly=True)
    customer_address = fields.Char(related="customer.street", string="Adress", readonly=True)
    customer_email = fields.Char(related="customer.email", string="Email", readonly=True)
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


    staff_id = fields.Many2one("salon.staff", string="Assigned Staff")
    branch_id = fields.Many2one("salon.branches", string="Branch Offices")
    service_booking_id = fields.One2many("salon.booking.service", "booking_id", string="Services")
    package_booking_id = fields.One2many("salon.booking.package", "booking_id", string="Packages")

    working_hours = fields.Many2one(related='branch_id.working_hours_id', string="Working Hours")

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
                return {
                    'warning': {
                        'title': "Not Working",
                        'message': f"{employee.name} not working on {booking_local.strftime('%A')}."
                    }
                }

            booking_hour = booking_local.hour + booking_local.minute / 60.0
            valid = False
            for att in attendances:
                if att.hour_from <= booking_hour <= att.hour_to:
                    valid = True
                    break

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
        """Cek booking sesuai jam operasional cabang."""
        if self.branch_id and self.branch_id.working_hours_id and self.booking_date:
            wh = self.branch_id.working_hours_id
            booking_dt = fields.Datetime.context_timestamp(self, self.booking_date)
            booking_hour = booking_dt.hour + booking_dt.minute / 60.0
            if booking_hour < wh.working_start or booking_hour > wh.working_end:
                self.booking_date = False
                return {
                    'warning': {
                        'title': "Invalid Booking Time",
                        'message': (f"Booking must be between {int(wh.working_start):02d}:"
                                    f"{int((wh.working_start % 1) * 60):02d} and "
                                    f"{int(wh.working_end):02d}:"
                                    f"{int((wh.working_end % 1) * 60):02d}")
                    }
                }

    @api.onchange('staff_id', 'booking_date')
    def _onchange_staff_leave_check(self):
        """Cek apakah staff sedang cuti di tanggal booking."""
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

    @api.depends('booking_date','service_booking_id.service_duration','package_booking_id.package_duration')
    def _compute_end_date(self):
        for rec in self:
            if rec.booking_date:
                total_duration = 0

                # Tambahkan total durasi service
                if rec.service_booking_id:
                    total_duration += sum(service.service_duration or 0 for service in rec.service_booking_id)

                # Tambahkan total durasi package
                if rec.package_booking_id:
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

    def _create_invoice(self):
        """Buat invoice otomatis dari layanan & paket booking."""
        for rec in self:
            if not rec.customer:
                return {
                        'warning': {
                            'title': "Customer has not been selected",
                            'message': f"Customer has not been selected, cannot create invoice."
                        }
                    }

            if rec.invoice_id:
                continue  # sudah ada invoice, skip

            invoice_lines = []

            # Tambah services
            for service in rec.service_booking_id:
                invoice_lines.append((0, 0, {
                    'name': service.service_id.name or 'Service',
                    'quantity': 1,
                    'price_unit': service.service_price or 0,
                }))

            # Tambah packages
            for package in rec.package_booking_id:
                invoice_lines.append((0, 0, {
                    'name': package.package_name or 'Package',
                    'quantity': 1,
                    'price_unit': package.package_total_price or 0,
                }))

            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': rec.customer.id,
                'invoice_date': fields.Date.today(),
                'invoice_origin': rec.booking_id,
                'booking_id': rec.id,
                'invoice_line_ids': invoice_lines
            }
            invoice = self.env['account.move'].create(move_vals)
            invoice.action_post()  # langsung posting
            rec.invoice_id = invoice.id

    @api.model
    def create(self, vals):
        # Generate booking number
        if vals.get('booking_id', 'New') == 'New':
            vals['booking_id'] = self.env['ir.sequence'].next_by_code('salon.booking') or 'New'
        record = super(SalonBooking, self).create(vals)

        # Buat invoice langsung setelah booking dibuat
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
    
    @api.constrains('staff_id', 'booking_date')
    def _check_staff_on_leave(self):
        for rec in self:
            if rec.staff_id and rec.booking_date:
                employee = rec.staff_id.branch_staff_ids  # hr.employee
                if not employee:
                    continue

                # Cari cuti yang statusnya sudah divalidasi
                leave_exists = self.env['hr.leave'].search_count([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'validate'),
                    ('request_date_from', '<=', rec.booking_date.date()),
                    ('request_date_to', '>=', rec.booking_date.date()),
                ]) > 0

                if leave_exists:
                    return {
                        'warning': {
                            'title': "Staff is on leave",
                            'message': f"Staff {employee.name} is on leave on {rec.booking_date.date()}"
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
                            'title': "Staff is on leave",
                            'message': f"Staff {employee.name} is on leave on {self.booking_date.date()}."
                        }
                    }