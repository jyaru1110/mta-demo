# -*- coding:utf-8 -*-

from odoo import http
from odoo.http import request
from datetime import datetime
import datetime
from dateutil import tz

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('UTC-6')

class GetSales(http.Controller):
    @http.route(['/get_sales/<int:producto_id>'],type='json',auth='public',website=True)
    
    def get_sales(self,producto_id):
        product = http.request.env['mta.producto'].sudo().search([('id','=',producto_id)])
        sales = http.request.env['sale.order.line'].sudo().search([('product_id','=',product.product_tmpl_id.id)])
        s = []
        for sale in sales:
            utc = sale.write_date
            utc = utc.replace(tzinfo=from_zone)
            cst = utc.astimezone(to_zone)
            n={
                "date" : cst,
                "qty" : sale.product_uom_qty
            }
            s.append(n)
        return s
            
        