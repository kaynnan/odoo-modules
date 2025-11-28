# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnanx1@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LoyaltyLevel(models.Model):
    _name = "loyalty.level"
    _description = "Loyalty Program Level"
    _order = "min_points asc"

    name = fields.Char(
        required=True,
        translate=True,
        help="Level name displayed to the customer (e.g., Bronze, Gold)."
    )
    min_points = fields.Float(
        required=True,
        default=0.0,
        help="The minimum point threshold to acquire this level."
    )
    email_template_id = fields.Many2one(
        comodel_name="mail.template",
        domain=[("model", "=", "res.partner")],
        string="Welcome Email Template",
        help="Email sent automatically when a customer reaches this level."
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "The level name must be unique."
        ),
        (
            "min_points_uniq",
            "unique (min_points)",
            "The point threshold must be unique per level."
        ),
        (
            "min_points_positive",
            "check(min_points >= 0)",
            "Minimum points cannot be negative."
        ),
    ]