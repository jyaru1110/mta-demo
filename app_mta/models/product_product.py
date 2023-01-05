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
    contador_v = fields.Float(string="Contador de verde")
    contador_r = fields.Float(string="Contador de rojo")
    recomendacion = fields.Selection(string="Recomendación",default="nr", selection=[('ibs','Incrementar buffer size'),('dbs','Reducir buffer_size'),('nr','Buffer no requiere ser ajustado')], compute='_compute_recomendacion')
    alerta = fields.Selection(string="Status del buffer",selection=[('DV','DV'),('DR','DR'),('N/A','N/A')], default="N/A")
    
    @api.depends('recomendacion')
    def _compute_recomendacion(self):
        for record in self:
            if(record.qty_available>=2*record.buffer_size/3 and record.recomendacion == 'dbs'):
                record.recomendacion = 'nr'
            elif record.qty_available >=record.buffer_size/3:
                record.recomendacion = 'nr'
            elif record.qty_available <=record.buffer_size/3 and record.recomendacion == 'ibs':
                record.recomendacion = 'nr'
    
    
    @api.model
    def create(self,values):
        override_create = super(ProductProduct,self).create(values)
        self.env['mta.producto'].create({'product_tmpl_id':override_create.id})
        return override_create
    
    def write(self,values):
        # your logic goes here
        actual_buffer_size = self._origin.buffer_size
        actual_qty_available = self._origin.qty_available
        if 'buffer_size' in values:
            if(values['buffer_size']!=actual_buffer_size):
                values['contador_v'] = 0
                values['contador_r'] = 0
                values['alerta'] = 'N/A'
                values['recomendacion'] = 'nr'
                producto_mta = self.env['mta.producto'].search([('product_tmpl_id','=',self._origin.id)])
                if producto_mta:
                    self.env['changes.time'].create({'product_id':producto_mta.id,'buffer_size':values['buffer_size'],'qty_available':actual_qty_available,'type':'buffer'})
        if 'qty_available' in values:
            if values['qty_available']!=actual_qty_available:
                producto_mta = self.env['mta.producto'].search([('product_tmpl_id','=',self._origin.id)])
                if producto_mta:
                    self.env['changes.time'].create({'product_id':producto_mta.id,'qty_available':values['qty_available'],'buffer_size':actual_buffer_size,'type':'available'})
    
        override_write = super(ProductProduct,self).write(values)

        return override_write