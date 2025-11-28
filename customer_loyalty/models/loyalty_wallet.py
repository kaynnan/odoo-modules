# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnanx1@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class LoyaltyWallet(models.Model):
    """Customer loyalty point wallet management."""

    _name = "loyalty.wallet"
    _description = "Customer Loyalty Wallet"
    _order = "create_date desc"

    name = fields.Char(
        required=True,
        default=lambda self: _("Main Wallet"),
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
        index=True,
    )
    points = fields.Float(
        compute="_compute_points",
        store=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        comodel_name="loyalty.wallet.line",
        inverse_name="wallet_id",
    )
    active = fields.Boolean(default=True)

    @api.depends("line_ids.points")
    def _compute_points(self):
        """
        Calculate total points using SQL
        for performance on large history.
        """
        stored_wallets = self.filtered(lambda w: isinstance(w.id, int))
        new_wallets = self - stored_wallets
        
        if stored_wallets:
            data = self.env["loyalty.wallet.line"].read_group(
                domain=[("wallet_id", "in", stored_wallets.ids)],
                fields=["wallet_id", "points"],
                groupby=["wallet_id"],
            )
            points_map = {d["wallet_id"][0]: d["points"] for d in data}
            
            for wallet in stored_wallets:
                wallet.points = points_map.get(wallet.id, 0.0)

        for wallet in new_wallets:
            wallet.points = sum(wallet.line_ids.mapped("points"))

    def _create_transaction(self, points, description, sale_order_id=False):
        """
        Internal helper.
        Returns the created line so the caller can use it.
        """
        self.ensure_one()
        line = self.env["loyalty.wallet.line"].create({
            "wallet_id": self.id,
            "points": points,
            "description": description,
            "sale_order_id": sale_order_id,
        })
        self.partner_id.upgrade_level()
        return line

    def add_points(self, points, description=None, sale_order_id=False):
        """Add points and return the transaction line."""
        desc = description or _("Points added: %s") % points
        return self._create_transaction(points, desc, sale_order_id)

    def remove_points(self, points, description=None, sale_order_id=False):
        """Remove points and return the transaction line."""
        desc = description or _("Points removed: %s") % points
        return self._create_transaction(-abs(points), desc, sale_order_id)