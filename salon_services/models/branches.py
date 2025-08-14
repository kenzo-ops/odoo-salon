from odoo import fields, models, api

class Branches(models.Model):
    _name = "salon.branches"
    _description = "Cabang Salon"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char(string="Branch Name", required=True)
    telephone_number = fields.Char(string="Phone number", required=True)
    email = fields.Char(string="Email", required=True)
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2one("res.country.state", string="Province")
    city_id = fields.Char(string="City")
    address = fields.Char(string="Address")
    status = fields.Boolean(string="Status", required=True)
    state = fields.Selection(
        selection=[
            ("inactive", "Inactive"),
            ("active", "Active"),
        ],
        string="Status",
        default="inactive"
    )
    

    manager_id = fields.Many2one(
        "hr.employee",
        string="Branch Manager",
        domain="[('job_id.name', 'ilike', 'Manager Cabang')]"
    )

    room_id = fields.One2many('salon.branch.room', 'branch_id', string="Branch Office Rooms")
    service_id = fields.One2many('salon.services', 'branch_id', string="Available Branch Services")
    service_available_id = fields.One2many('salon.booking.service', 'branch_id', string="Available Branch Services")
    branch_staff_ids = fields.One2many(
        "salon.staff", "branch_id",
        string="Branch Staff",
        domain=[('job_id.name', '=', 'Staff')]
    )
    
    working_hours_id = fields.Many2one("salon.working.hour", string="Working Hours")


    @api.onchange('status')
    def _onchange_status(self):
        for rec in self:
            rec._sync_state_with_status()

    def _sync_state_with_status(self):
        for rec in self:
            rec.state = 'active' if rec.status else 'inactive'

    @api.model
    def create(self, vals):
        vals['state'] = 'active' if vals.get('status') else 'inactive'
        return super().create(vals)

    def write(self, vals):
        if 'status' in vals:
            vals['state'] = 'active' if vals['status'] else 'inactive'
        return super().write(vals)