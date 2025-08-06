from odoo import fields, api, models

class ServiceCategory(models.Model):
    _name = "salon.service.category"
    _description = "Salon Service Category"

    name = fields.Char(string="Nama Kategori", required=True)
    sub_category_id = fields.One2many("salon.sub.category", "category_id", string="Sub Kategori", readonly=True)
    status = fields.Boolean(string="Status", required=True)
    state = fields.Selection(
        selection = [
            ("inactive", "Tidak Aktif"),
            ("active", "Aktif"),
        ],
        string="Status",
        default = "inactive"
        )

    @api.onchange('status')
    def _onchange_status(self):
        self._sync_state_with_status()

    @api.model
    def create(self, vals):
        vals['state'] = 'active' if vals.get('status') else 'inactive'
        return super().create(vals)

    def write(self, vals):
        if 'status' in vals:
            vals['state'] = 'active' if vals['status'] else 'inactive'
        return super().write(vals)

    def _sync_state_with_status(self):
        for rec in self:
            rec.state = 'active' if rec.status else 'inactive'
