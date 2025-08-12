from odoo import models, fields, api

class SalonCustomerBooking(models.Model):
    _name = 'salon.customer.booking'
    _description = 'Statistik Customer Booking'
    _auto = False 
    _rec_name = 'customer_id'

    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    total_booking = fields.Integer(string='Total Bookings', readonly=True)
    total_spent = fields.Float(string='Total Expenditures', readonly=True)
    last_booking_date = fields.Datetime(string='Last Booking', readonly=True)


    def init(self):
        self._cr.execute("""
            CREATE OR REPLACE VIEW salon_customer_booking AS (
                SELECT
                    MIN(b.id) AS id,
                    b.customer AS customer_id,
                    COUNT(b.id) AS total_booking,
                    SUM(b.total_price) AS total_spent,
                    MAX(b.booking_date) AS last_booking_date
                FROM salon_booking b
                WHERE b.state != 'batal' AND b.customer IS NOT NULL
                GROUP BY b.customer
            )
        """)
