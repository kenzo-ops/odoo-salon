from odoo import fields, api, models

class SubCategory(models.Model):
    _name = "salon.sub.category"
    _description = " Salon Sub Category"

    name = fields.Char(string="Nama", required=True)
    category_id = fields.Many2one("salon.service.category",string="Kategori Utama")
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