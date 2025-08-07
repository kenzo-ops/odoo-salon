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
    product_category_id = fields.Many2one(
        'product.category',
        string='Kategori Produk Terkait',
        readonly=True,
        help="Kategori Produk yang dibuat otomatis"
    )

    @api.onchange('status')
    def _onchange_status(self):
        self._sync_state_with_status()

    @api.model
    def create(self, vals):
        # Buat product.category terlebih dahulu
        product_category = self.env['product.category'].create({
            'name': vals.get('name', 'Tanpa Nama')
        })
        # Simpan ID-nya ke field relasi
        vals['product_category_id'] = product_category.id

        # Sinkronkan state dari status
        vals['state'] = 'active' if vals.get('status') else 'inactive'
        return super().create(vals)

    def write(self, vals):
        for rec in self:
            # Sync state jika status berubah
            if 'status' in vals:
                vals['state'] = 'active' if vals['status'] else 'inactive'

            # Jika product_category_id masih kosong, buat baru
            if not rec.product_category_id:
                name = vals.get('name', rec.name)
                product_category = self.env['product.category'].create({
                    'name': name
                })
                vals['product_category_id'] = product_category.id

        return super().write(vals)

    def _sync_state_with_status(self):
        for rec in self:
            rec.state = 'active' if rec.status else 'inactive'