# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnanx1@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    loyalty_wallet_ids = fields.One2many(
        comodel_name="loyalty.wallet",
        inverse_name="partner_id",
        string="Loyalty Wallets",
    )

    loyalty_level_id = fields.Many2one(
        comodel_name="loyalty.level",
        string="Loyalty Level",
        readonly=True,
        tracking=True,
        ondelete="set null",
    )

    total_loyalty_points = fields.Float(
        compute="_compute_total_loyalty_points",
        store=True,
    )

    @api.depends("loyalty_wallet_ids.points")
    def _compute_total_loyalty_points(self):
        """
        Calculate total points from all wallets.
        Standard ORM method is sufficient here
        as wallet count per partner is low.
        """
        for partner in self:
            partner.total_loyalty_points = sum(
                partner.loyalty_wallet_ids.mapped("points")
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Create partners and their main wallets in batch."""
        partners = super().create(vals_list)

        default_wallet_name = _("Main Wallet")
        wallet_vals_list = []

        for partner in partners:
            if not partner.is_company or partner.parent_id:
                wallet_vals_list.append({
                    "name": default_wallet_name,
                    "partner_id": partner.id,
                })

        if wallet_vals_list:
            self.env["loyalty.wallet"].create(wallet_vals_list)

        return partners
    
    def upgrade_level(self):
        """Dynamically calculate level based on points."""
        levels = self.env["loyalty.level"].search([], order="min_points desc")
        levels_data = [(l, l.min_points) for l in levels]

        for partner in self:
            current_points = partner.total_loyalty_points
            found_level = self.env["loyalty.level"]

            for level, min_points in levels_data:
                if current_points >= min_points:
                    found_level = level
                    break

            if partner.loyalty_level_id != found_level:
                partner.loyalty_level_id = found_level

    @api.model
    def send_weekly_level_emails(self):
        """Generic scheduled action using Mail Queue."""
        levels = self.env["loyalty.level"].search([
            ("email_template_id", "!=", False)
        ])

        for level in levels:
            template = level.email_template_id
            domain = [
                ("loyalty_level_id", "=", level.id),
                ("email", "!=", False),
                ("email", "!=", ""),
            ]
            customers = self.search(domain)
            for customer in customers:
                template.send_mail(customer.id, force_send=False)

    def _get_or_create_loyalty_wallet(self):
        """Helper method to retrieve or create the default wallet."""
        self.ensure_one()
        wallet = self.loyalty_wallet_ids[:1]
        if not wallet:
            wallet = self.env["loyalty.wallet"].create({
                "name": _("Main Wallet"),
                "partner_id": self.id,
            })
        return wallet

    def action_redeem_points(self, product_id):
        """
        Execute redemption logic:
        1. Create a Sales Order with 100% discount.
        2. Deduct points from wallet.
        """
        self.ensure_one()
        product = self.env["product.product"].browse(product_id)

        if not product.exists():
            raise ValidationError(_("Product not found."))

        points_required = product.list_price

        if self.total_loyalty_points < points_required:
            raise ValidationError(_("Insufficient points."))

        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.id,
            'state': 'draft',
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': product.list_price,
                'discount': 100.0,
                'name': f"{product.name} (Loyalty Reward)",
            })]
        })

        wallet = self._get_or_create_loyalty_wallet()
        description = _("Redeemed for reward: %s (Order %s)") % (product.name, sale_order.name)

        return wallet.sudo().remove_points(
            points_required,
            description=description,
            sale_order_id=sale_order.id,
        )

    def action_view_loyalty_details(self):
        """Smart button action to view wallets/history."""
        self.ensure_one()
        return {
            "name": _("Loyalty Wallets"),
            "type": "ir.actions.act_window",
            "res_model": "loyalty.wallet",
            "view_mode": "list,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }

    def _get_loyalty_report_filename(self):
        """Generate a translatable filename for the loyalty report."""
        self.ensure_one()
        prefix = _("Loyalty_Summary")
        safe_name = self.name.replace(" ", "_")
        return f"{prefix}_{safe_name}"