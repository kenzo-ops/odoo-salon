from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"

    booking_id = fields.Many2one("salon.booking", string="Booking")
