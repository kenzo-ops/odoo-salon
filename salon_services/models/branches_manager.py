from odoo import models, fields

class SalonBranchManager(models.Model):
    _name = 'salon.branch.manager'
    _description = 'Manager Cabang Salon'

    employee_id = fields.Many2one('hr.employee', string="Manajer", required=True, ondelete='cascade')
    branch_id = fields.Many2one('salon.branches', string="Cabang", required=True)

    _sql_constraints = [
        ('unique_branch', 'unique(branch_id)', 'Setiap cabang hanya boleh punya satu manajer.')
    ]
