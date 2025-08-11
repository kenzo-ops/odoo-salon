from odoo import api, fields, models

class Services(models.Model):
    _name = "salon.services"
    _description = "Salon Services"

    name = fields.Char(string="Nama Layanan", required=True)
    description = fields.Char(string="Deskripsi Layanan", required=True)
    duration = fields.Integer(string="Durasi Layanan (Menit)", required=True)
    harga = fields.Float(string="Harga Layanan", required=True)
    category = fields.Many2one('salon.service.category', string="Kategori", required=True)
    sub_category = fields.Many2one('salon.sub.category', string="Sub Kategori", required=True)
    
    product_id = fields.Many2one('product.template', string="Produk Terkait", readonly=True)
    packages_id = fields.Many2one('salon.packages') 
    branch_id = fields.Many2one("salon.branches", string="Cabang")
    booking_id = fields.Many2one("salon.booking")


    @api.model
    def create(self, vals):
        name = vals.get('name')
        harga = vals.get('harga', 0.0)
        description = vals.get('description', '')
        sub_category_id = vals.get('sub_category')

        sub_category = self.env['salon.sub.category'].browse(sub_category_id) if sub_category_id else None
        product_category = sub_category.product_sub_category_id if sub_category and sub_category.product_sub_category_id else None

        if not product_category or not product_category.id:
            product_category = self.env['product.category'].search([('name', '=', 'Jasa Salon')], limit=1)
            if not product_category or not product_category.id:
                product_category = self.env['product.category'].create({'name': 'Jasa Salon'})

        product = self.env['product.template'].create({
            'name': name,
            'list_price': harga,
            'type': 'service',
            'categ_id': product_category.id,
            'description_sale': description,
        })

        vals['product_id'] = product.id

        return super().create(vals)