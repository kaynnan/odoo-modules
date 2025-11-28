# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnanx1@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    """Extend sale order with loyalty points calculation."""

    _inherit = "sale.order"

    loyalty_points_earned = fields.Float(
        string="Loyalty Points",
        compute="_compute_loyalty_points_earned",
        store=True,
        help="Estimated points to be added upon confirmation.",
    )

    @api.depends("amount_total")
    def _compute_loyalty_points_earned(self):
        """Calculate points based on the configured global rate."""
        rate_param = self.env["ir.config_parameter"].sudo().get_param(
            "customer_loyalty.rate", default=0.1
        )
        conversion_rate = float(rate_param)

        for order in self:
            order.loyalty_points_earned = order.amount_total * conversion_rate

    def action_confirm(self):
        """Trigger point addition upon confirmation."""
        res = super().action_confirm()

        valid_orders = self.filtered(
            lambda o: o.partner_id and o.loyalty_points_earned > 0
        )

        for order in valid_orders:
            wallet = order.partner_id._get_or_create_loyalty_wallet()
            description = _("Points from Sale Order %s") % order.name

            wallet.add_points(
                points=order.loyalty_points_earned,
                description=description,
                sale_order_id=order.id,
            )

        return res