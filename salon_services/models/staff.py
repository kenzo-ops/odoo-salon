from odoo import fields, models, api

class Staff(models.Model):
    _name = "salon.staff"
    _description = "Salon Staff"
    _rec_name = "branch_staff_ids"

    branch_staff_ids = fields.Many2one(
        "hr.employee",
        string="Name",
        domain=[('job_id.name', '=', 'Staff')]
    )
    job_id = fields.Many2one(related='branch_staff_ids.job_id')
    branch_id = fields.Many2one("salon.branches")