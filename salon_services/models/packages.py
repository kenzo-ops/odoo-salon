from odoo import fields, models, api


class Packages(models.Model):
    _name = "salon.packages"
    _description = "Salon Packages"

    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
    status = fields.Boolean(string="Status", required=True)
    state = fields.Selection(
        selection=[
            ("inactive", "Inactive"),
            ("active", "Active"),
        ],
        string="Status",
        default="inactive",
    )
    start_date = fields.Date(string="Effective date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    total_price = fields.Float(
        string="Total Package Price",
        compute="_compute_total_package_price",
        store=True,
        readonly=True,
    )
    total_duration = fields.Integer(
        string="Total Duration (minutes)",
        compute="_compute_total_duration",
        store=True,
        readonly=True,
    )

    booking_id = fields.Many2one("salon.booking")
    package_service_id = fields.One2many(
        "salon.package.service", "packages_id", string="Service", required=True
    )

    @api.depends("package_service_id.service_duration", "package_service_id.quantity")
    def _compute_total_duration(self):
        for rec in self:
            rec.total_duration = sum(
                line.service_duration * line.quantity for line in rec.package_service_id
            )

    @api.depends("package_service_id.total_price")
    def _compute_total_package_price(self):
        for rec in self:
            rec.total_price = sum(line.total_price for line in rec.package_service_id)

    @api.onchange("status")
    def _onchange_status(self):
        self._sync_state_with_status()

    @api.model
    def create(self, vals):
        vals["state"] = "active" if vals.get("status") else "inactive"
        return super().create(vals)

    def write(self, vals):
        if "status" in vals:
            vals["state"] = "active" if vals["status"] else "inactive"
        return super().write(vals)

    def _sync_state_with_status(self):
        for rec in self:
            rec.state = "active" if rec.status else "inactive"
