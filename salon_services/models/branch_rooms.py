from odoo import fields, models, api

class BranchRooms(models.Model):
    _name = "salon.branch.room"
    _description = "Branch Office Rooms"
    _rec_name = "branch_id"

    branch_id = fields.Many2one("salon.branches", string="Branch Office Name")
    room_id = fields.Many2one("salon.room", string="Room Name")