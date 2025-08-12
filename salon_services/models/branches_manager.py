from odoo import models, fields

class SalonBranchManager(models.Model):
    _name = 'salon.branch.manager'
    _description = 'Manager Cabang Salon'

    employee_id = fields.Many2one('hr.employee', string="Manager", required=True, ondelete='cascade')
    branch_id = fields.Many2one('salon.branches', string="Branch", required=True)

    _sql_constraints = [
        ('unique_branch', 'unique(branch_id)', 'Each branch may only have one manager.')
    ]
