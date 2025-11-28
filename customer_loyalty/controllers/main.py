from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerLoyaltyPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "loyalty_count" in counters:
            partner = request.env.user.partner_id
            values['loyalty_count'] = int(partner.total_loyalty_points)
        return values

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        
        values['loyalty_level'] = partner.loyalty_level_id 
        values['page_name'] = 'loyalty'
        values['total_points'] = partner.total_loyalty_points
        return values

    @http.route(
        ['/my/loyalty'],
        type='http',
        auth='user',
        website=True
    )
    def portal_my_loyalty(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        all_levels = request.env['loyalty.level'].sudo().search(
            [],
            order='min_points asc'
        )

        products = request.env['product.product'].sudo().search([
            ('sale_ok', '=', True),
            ('list_price', '>', 0),
        ], limit=20)

        wallet_ids = partner.loyalty_wallet_ids.ids
        wallet_lines = request.env['loyalty.wallet.line'].search([
            ('wallet_id', 'in', wallet_ids)
        ], order='create_date desc', limit=50)

        values.update({
            'partner': partner,
            'all_levels': all_levels,
            'wallets': partner.loyalty_wallet_ids,
            'wallet_lines': wallet_lines,
            'products': products,
        })
        
        return request.render('customer_loyalty.portal_my_loyalty', values)

    @http.route(
        ['/my/loyalty/redeem'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True
    )
    def portal_loyalty_redeem(self, product_id, **kw):
        partner = request.env.user.partner_id
        product = request.env['product.product'].sudo().browse(int(product_id))

        if not product.exists():
            return request.redirect('/my/loyalty?error=product_not_found')

        points_required = product.list_price
        if partner.total_loyalty_points < points_required:
            return request.redirect('/my/loyalty?error=insufficient_points')

        partner.action_redeem_points(product.id)

        return request.redirect('/my/loyalty?success=redeemed')