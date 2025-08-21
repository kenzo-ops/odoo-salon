from odoo import models, fields, api

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    is_branch_manager = fields.Boolean(string='Branch Manager', compute='_compute_is_branch_manager', store=True)
    is_staff = fields.Boolean(string='Staff', compute='_compute_is_branch_manager', store=True)
    is_doctor = fields.Boolean(string='Docter', compute='_compute_is_branch_manager', store=True)
    branch_manager_ids = fields.Many2one('salon.branches', string="Managed Branches")
    calendar_id = fields.Many2one(
        "resource.calendar",
        string="Work Schedule",
    )
    related_contact_id = fields.Many2one(
        'res.partner',
        string="Related Contact",
        compute="_compute_related_contact",
        store=False
    )

    @api.depends('work_contact_id', 'address_id')
    def _compute_related_contact(self):
        """
        Cari partner yang terkait employee:
        - kalau ada work_contact_id (Odoo 16+)
        - kalau ada address_id (versi lama, alamat kantor/privat)
        """
        for rec in self:
            partner = False
            # cek apakah field ada di model
            if 'work_contact_id' in rec._fields and rec.work_contact_id:
                partner = rec.work_contact_id
            elif 'address_id' in rec._fields and rec.address_id:
                partner = rec.address_id
            rec.related_contact_id = partner

    @api.depends('job_id.name')
    def _compute_is_branch_manager(self):
        for rec in self:
            rec.is_branch_manager = rec.job_id.name == "Branch Manager"
            rec.is_staff = rec.job_id.name == "Staff"
            rec.is_doctor = rec.job_id.name == "Doctor"

                                                               