from odoo import fields, models, api

class Packages(models.Model):
    _name = "salon.packages"
    _description = "Salon Packages"

    name = fields.Char(string="Nama", required=True)
    description = fields.Char(string="Deskripsi")
    status = fields.Boolean(string="Status", required=True)
    state = fields.Selection(
        selection = [
            ("inactive", "Tidak Aktif"),
            ("active", "Aktif"),
        ],
        string="Status",
        default = "inactive"
        )
    start_date = fields.Date(string="Tanggal Berlaku", required=True)
    end_date = fields.Date(string="Tanggal Berakhir", required=True)
    total_price = fields.Float(string="Total Harga Paket", compute="_compute_total_package_price", store=True, readonly=True)

    booking_id = fields.Many2one("salon.booking")
    package_service_id = fields.One2many('salon.package.service','packages_id',string="Layanan",required=True)

    @api.depends('package_service_id.total_price')
    def _compute_total_package_price(self):
        for rec in self:
            rec.total_price = sum(line.total_price for line in rec.package_service_id)

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
