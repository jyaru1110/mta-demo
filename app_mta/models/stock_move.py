# -*- coding utf-8 -*- 
from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.model
    def create(self,values):
        override_create = super(StockMove,self).create(values)
        if(override_create.reference[0:6]=='WH/IN/'):
            producto = self.env['mta.producto'].search([('product_tmpl_id','=',values['product_id'])])
            oc_actual = producto.oc
            producto.oc = oc_actual + values['product_uom_qty']
            
        return override_create
    
    def write(self,values):
        override_write = super(StockMove,self).write(values)
        if self._origin.state=="done" and self._origin.reference[0:6]=='WH/IN/':
            producto = self.env['mta.producto'].search([('product_tmpl_id','=',self._origin.product_id.id)])
            oc_actual = producto.oc
            if oc_actual - self._origin.product_uom_qty < 0:
                producto.oc = 0
            else:
                producto.oc = oc_actual - self._origin.product_uom_qty
        return override_write