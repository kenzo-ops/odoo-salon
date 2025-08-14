from odoo import fields, models, api

class WorkingHours(models.Model):
    _name = "salon.working.hour"
    _description = "Working Hours"

    name = fields.Char(string="Working Hours Name", required=True)      
    working_start = fields.Float(string="Start Time", required=True)
    working_end = fields.Float(string="Finish Time", required=True)


