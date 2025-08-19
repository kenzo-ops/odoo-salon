from odoo import fields, models, api

class BranchRooms(models.Model):
    _name = "salon.branch.room"
    _description = "Branch Office Rooms"
    _rec_name = "branch_id"

    branch_id = fields.Many2one("salon.branches", string="Branch Office Name", required=True)
    room_id = fields.Many2one("salon.room", string="Room Name", domain=[('state', '=', 'active')])
    state = fields.Selection(related='room_id.state', readonly=True)

    @api.constrains('room_id')
    def _check_room_state(self):
        for rec in self:
            if rec.room_id and rec.room_id.state != 'active':
                raise ValidationError(f"Room {rec.room_id.name} is inactive and cannot be used.")