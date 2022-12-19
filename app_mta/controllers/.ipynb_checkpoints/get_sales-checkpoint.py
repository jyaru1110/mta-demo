# -*- coding:utf-8 -*-

from odoo import http
from odoo.http import request
from datetime import datetime
import datetime
from dateutil import tz

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('UTC-6')

class GetSales(http.Controller):
    @http.route(['/get_sales/<int:product_id>'],type='json',auth='public',website=True)
    
    def get_sales(self,product_id):
        product = http.request.env['mta.producto'].sudo().search([('product_tmpl_id','=',product_id)])
        sales = http.request.env['sale.order.line'].sudo().search([('product_id','=',product.id)])
        bc = []
        for sale in sales:
            utc = sales.__last_update
            utc = utc.replace(tzinfo=from_zone)
            cst = utc.astimezone(to_zone)
            n={
                "id" : sale.product_id,
                "date" : cst,
                "qty" : sale.product_uom_qty
            }
            bc.append(n)
        return bc
            
        