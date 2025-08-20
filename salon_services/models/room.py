from odoo import fields, api, models

class Room(models.Model): 
    _name = "salon.room"
    _description = "Clinic Rooms"

    name = fields.Char(string="Room Name", required=True)
    branch_id = fields.One2many("salon.branch.room", "room_id")
    status = fields.Boolean(string="Status", required=True)
    state = fields.Selection(
        selection=[
            ("inactive", "Inactive"),
            ("active", "Active"),
        ],
        string="Status",
        default="active"
    )

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