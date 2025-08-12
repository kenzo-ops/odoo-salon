from odoo import models, fields, api

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    is_branch_manager = fields.Boolean(string='Manager Cabang', compute='_compute_is_branch_manager', store=True)
    branch_manager_ids = fields.Many2one('salon.branches', string="Cabang yang Dikelola")

    @api.depends('job_id.name')
    def _compute_is_branch_manager(self):
        for rec in self:
            rec.is_branch_manager = rec.job_id.name == "Manager Cabang"
