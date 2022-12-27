# -*- coding utf-8 -*- 
from odoo import models, fields, api
from datetime import datetime

class MtaProducto(models.Model):
    _inherits = {'product.product': 'product_tmpl_id'}
    _name = 'mta.producto'
    _description = 'Product MTA'
   
    changes = fields.One2many(comodel_name='changes.time',
                                  inverse_name = 'product_id',
                                  string = 'Cambios en buffer o qty available')
    #product.template relation:
    product_tmpl_id = fields.Many2one('product.product', 'Product Product', required=True, ondelete='cascade')
   
    estado = fields.Integer(string="1. Verde 2. Amarillo 3. Rojo", compute='_compute_estado')
    
    
    oc = fields.Integer(string="# OC", default=0)
    bp_solicitud = fields.Integer(string="%BP en solicitadas",
                                compute='_compute_bp_solicitud')
    bp_transito = fields.Integer(string="%BP en transito"
                               , compute='_compute_bp_transito')
    bp_sitio = fields.Integer(string="%BP en sitio",
                               compute='_compute_bp_sitio')
    
    
    @api.model
    def create(self,values):
        override_create = super(MtaProducto,self).create(values)
        self.env['changes.time'].create({'product_id':override_create.id,'buffer_size':override_create.buffer_size,'qty_available':override_create.qty_available,'type':'buffer'})
        self.env['changes.time'].create({'product_id':override_create.id,'buffer_size':override_create.buffer_size,'qty_available':override_create.qty_available,'type':'available'})
        
        return override_create
        
    @api.depends('buffer_size','qty_transit','qty_available', 'estado', 'contador_v', 'contador_r','alerta')
    def _compute_bp_transito(self):
       for record in self:
            record.bp_transito = ((record.buffer_size-record.qty_available-record.qty_transit)/(record.buffer_size))*100
    def _compute_bp_solicitud(self):
        for record in self:
            record.bp_solicitud = ((record.buffer_size-record.oc-record.qty_available-record.qty_transit)/(record.buffer_size))*100
    def _compute_bp_sitio(self):
        for record in self:
            record.bp_sitio = ((record.buffer_size-record.qty_available)/(record.buffer_size))*100
    def _compute_estado(self):
        for record in self:
            if(record.qty_available>=2*record.buffer_size/3):
                record.estado = 1
                record.contador_r = 0
            elif record.qty_available >=record.buffer_size/3:
                record.estado = 2
                record.contador_v = 0
                record.contador_r = 0
            else:
                record.estado = 3
                record.contador_v = 0
            if (record.contador_r == 0 and record.contador_v == 0):
                record.alerta = 'N/A'
    
        
        
        
    def daily(self):
        productos = self.env['mta.producto'].search([('buffer_size','!=',0)])
        
        for producto in productos:
            contador = False
            product = self.env['mta.producto'].browse(producto['id'])
            if producto.estado == 1:
                product.contador_v =product.contador_v + (producto.qty_available-2*producto.buffer_size/3)/(producto.buffer_size/3)
                product.contador_r = 0
                   
            elif producto.estado == 3:
                product.contador_r =product.contador_r + 1-(producto.qty_available)/(producto.buffer_size/3)
                product.contador_v = 0
                
            if(product.contador_v>=product.dbm_v):
                product.alerta = 'DV'
                contador = True
            if(product.contador_r>=product.dbm_r):
                product.alerta = 'DR'
                contador = True
            if( not contador):
                product.alerta = 'N/A'
            
            
            if (product.alerta == 'DV'):
                if(product.changes):
                    now = datetime.utcnow()
                    last_buffer_size_update = product.changes[len(product.changes)-1].create_date
                    delta_time = now - last_buffer_size_update
                    if(delta_time.days>=product.lt and product.lt!=0):
                        product.recomendacion = 'dbs'
                
            if (product.alerta == 'DR'):
                if(product.changes):
                    now = datetime.utcnow()
                    last_buffer_size_update = product.changes[len(product.changes)-1].create_date
                    delta_time = now - last_buffer_size_update
                    if(delta_time.days>=product.lt and product.lt!=0):
                        product.recomendacion = 'ibs'