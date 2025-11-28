# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnanx1@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    loyalty_rate = fields.Float(
        string="Loyalty Rate",
        config_parameter="customer_loyalty.rate",
        default=0.1,
    )