from odoo import api, fields, models

class BookingService(models.Model):
    _name = "salon.booking.service"
    _description = "Salon Booking Service"

    booking_id = fields.Many2one("salon.booking")
    service_id = fields.Many2one("salon.services")
    service_description = fields.Char(related='service_id.description', string="Description", readonly=True)
    service_duration = fields.Integer(related='service_id.duration', string="Duration", readonly=True)
    service_price = fields.Float(related='service_id.harga', string="Price", readonly=True)
    service_category = fields.Many2one(related='service_id.category', string="Category", readonly=True)
    service_sub_category = fields.Many2one(related='service_id.sub_category', string="Sub Category", readonly=True)

    @api.model
    def get_top_services(self, limit=5):
        domain = []
        # read_group mengelompokkan berdasarkan service_id dan hitung jumlahnya
        results = self.read_group(
            domain,
            fields=["service_id"],
            groupby=["service_id"],
            orderby="__count desc",
            limit=limit,
        )
        top_services = []
        for rec in results:
            service = rec.get("service_id")
            count = rec.get("__count", 0)
            top_services.append({
                "service_id": service,
                "total": int(count)
            })
        return top_services


