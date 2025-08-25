from odoo import models, fields

class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    assigned_employee_ids = fields.One2many(
        "hr.employee",
        "resource_calendar_id",   # inverse field di hr.employee
        string="Assigned Employees"
    )
