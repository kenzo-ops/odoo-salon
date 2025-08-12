from odoo import fields, models, api

class Branches(models.Model):
    _name = "salon.branches"
    _description = "Cabang Salon"

    name = fields.Char(string="Nama Cabang", required=True)
    telephone_number = fields.Char(string="Nomor Telepon", required=True)
    email = fields.Char(string="Email", required=True)
    country_id = fields.Many2one("res.country", string="Negara")
    state_id = fields.Many2one("res.country.state", string="Provinsi")
    city_id = fields.Char(string="Kota")
    address = fields.Char(string="Alamat")
    status = fields.Boolean(string="Status", required=True)
    state = fields.Selection(
        selection=[
            ("inactive", "Tidak Aktif"),
            ("active", "Aktif"),
        ],
        string="Status",
        default="inactive"
    )    

    manager_id = fields.Many2one(
        "hr.employee",
        string="Manager Cabang",
        domain="[('job_id.name', 'ilike', 'Manager Cabang')]"
    )

    service_id = fields.One2many('salon.services', 'branch_id', string="Layanan Cabang Yang Tersedia")


    @api.onchange('status')
    def _onchange_status(self):
        for rec in self:
            rec._sync_state_with_status()

    def _sync_state_with_status(self):
        for rec in self:
            rec.state = 'active' if rec.status else 'inactive'

    @api.model
    def create(self, vals):
        vals['state'] = 'active' if vals.get('status') else 'inactive'
        return super().create(vals)

    def write(self, vals):
        if 'status' in vals:
            vals['state'] = 'active' if vals['status'] else 'inactive'
        return super().write(vals)