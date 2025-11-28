# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnanx1@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Customer Loyalty",
    "summary": "Loyalty program management with points, levels and rewards",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    "author": "Kaynnan Lemes",
    "website": "https://github.com/kaynnan",
    "depends": [
        "sale",
        "mail",
        "portal",
    ],
    "data": [
        "security/customer_loyalty_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "data/ir_cron.xml",
        "demo/demo.xml",
        "views/loyalty_level_views.xml",
        "views/loyalty_wallet_views.xml",
        "views/res_config.xml",
        "views/partner_views.xml",
        "views/sale_order_views.xml",
        "views/portal.xml",
        "views/menus.xml",
        "reports/reports.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "customer_loyalty/static/src/**/*",
        ],
        "web.assets_backend": [
            "customer_loyalty/static/src/**/*",
        ],
    },
    "installable": True,
    "application": True,
}