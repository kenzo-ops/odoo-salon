from odoo import fields, api, models, _
import logging

_logger = logging.getLogger(__name__)

class SubCategory(models.Model):
    _name = "salon.sub.category"
    _description = "Salon Sub Category"

    name = fields.Char(string="Nama", required=True)
    category_id = fields.Many2one("salon.service.category", string="Kategori Utama", required=True)
    status = fields.Boolean(string="Status", required=True)
    
    state = fields.Selection(
        selection=[
            ("inactive", "Inactive"),
            ("active", "Active"),
        ],
        string="Status",
        default="inactive"
    )

    product_sub_category_id = fields.Many2one(
        'product.category',
        string="Sub Kategori Produk Terkait",
        readonly=True
    )

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
        category = self.env['salon.service.category'].browse(vals.get('category_id'))

        if category and category.product_category_id:
            product_sub = self.env['product.category'].create({
                'name': vals.get('name', 'Tanpa Nama'),
                'parent_id': category.product_category_id.id,
            })
            vals['product_sub_category_id'] = product_sub.id
        else:
            _logger.warning("Kategori utama tidak memiliki product_category_id. Sub kategori produk tidak dibuat.")

        return super().create(vals)

    def write(self, vals):
        if 'status' in vals:
            vals['state'] = 'active' if vals['status'] else 'inactive'

        for rec in self:
            if not rec.product_sub_category_id:
                name = vals.get('name', rec.name)
                category = rec.category_id
                if 'category_id' in vals:
                    category = self.env['salon.service.category'].browse(vals['category_id'])

                if category and category.product_category_id:
                    product_sub = self.env['product.category'].create({
                        'name': name,
                        'parent_id': category.product_category_id.id,
                    })
                    vals['product_sub_category_id'] = product_sub.id
                else:
                    _logger.warning("Kategori utama tidak memiliki product_category_id saat update.")

        return super().write(vals)