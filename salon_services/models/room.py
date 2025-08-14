from odoo import fields, api, models

class Room(models.Model): 
    _name = "salon.room"
    _description = "Clinic Rooms"

    name = fields.Char(string="Room Name", required=True)
    branch_id = fields.One2many("salon.branch.room", "room_id")