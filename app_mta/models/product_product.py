# -*- coding utf-8 -*- 
from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    dbm_v = fields.Integer(string="Condicion demasiado verde",default=5)
    dbm_r = fields.Integer(string="Condicion demasiado rojo",default=1)
    be_mta_mon = fields.Boolean(string="Es monitoreado por MTA", default=True)
    lt = fields.Integer(string="Tiempo de respuesta del proveedor")
    loteOptimo = fields.Integer(string="Lote óptimo")
    qty_transit = fields.Integer(string="# transito")
    buffer_size = fields.Integer(string="Buffer Size",default=1)
    contador_v = fields.Integer(string="Contador de verde")
    contador_r = fields.Integer(string="Contador de rojo")
    
    @api.model
    def create(self,values):
        override_create = super(ProductProduct,self).create(values)
        self.env['mta.producto'].create({'product_tmpl_id':override_create.id})
        return override_create
    
    def write(self,values):
        # your logic goes here
        print('aki si entre jiji')
        actual_buffer_size = self._origin.buffer_size
        actual_qty_available = self._origin.qty_available
        if 'buffer_size' in values:
            if(values['buffer_size']!=actual_buffer_size):
                print("sí setee contadores a 0 jiji")
                values['contador_v'] = 0
                values['contador_r'] = 0
                producto_mta = self.env['mta.producto'].search([('product_tmpl_id','=',self._origin.id)])
                if producto_mta:
                    self.env['changes.time'].create({'product_id':producto_mta.id,'buffer_size':values['buffer_size'],'qty_available':actual_qty_available,'type':'buffer'})
        if 'qty_available' in values:
            if values['qty_available']!=actual_qty_available:
                print('sí entro a crear changes in time')
                producto_mta = self.env['mta.producto'].search([('product_tmpl_id','=',self._origin.id)])
                if producto_mta:
                    self.env['changes.time'].create({'product_id':producto_mta.id,'qty_available':values['qty_available'],'buffer_size':actual_buffer_size,'type':'available'})
    
        override_write = super(ProductProduct,self).write(values)

        return override_write