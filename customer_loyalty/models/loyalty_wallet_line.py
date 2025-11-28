# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnanx1@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LoyaltyWalletLine(models.Model):
    """Loyalty wallet point transaction history."""

    _name = "loyalty.wallet.line"
    _description = "Customer Loyalty Wallet Transaction"
    _order = "create_date desc"

    wallet_id = fields.Many2one(
        comodel_name="loyalty.wallet",
        required=True,
        ondelete="cascade",
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="wallet_id.partner_id",
        store=True,
        readonly=True,
    )
    points = fields.Float(
        required=True,
        help="Positive for points earned, negative for points spent",
    )
    description = fields.Text(required=True)
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        ondelete="set null",
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Validate manual point changes.
        Only Managers can create lines without a linked Sale Order.
        """

        if self.env.su:
            return super().create(vals_list)

        group_xml_id = "customer_loyalty.group_loyalty_card_manager"
        is_manager = self.env.user.has_group(group_xml_id)

        if not is_manager:
            for vals in vals_list:
                if not vals.get("sale_order_id"):
                    raise ValidationError(_(
                        "Only Loyalty Card Managers can manually change "
                        "points without a sale order."
                    ))
        return super().create(vals_list)