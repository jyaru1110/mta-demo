/** @odoo-module **/
import AbstractField from 'web.AbstractField';
import fieldRegistry from 'web.field_registry';
var ChartWidget = AbstractField.extend({
    template: "ChartWidget",
    start: function(){
        this._super.apply(this, arguments);
        if (this.recordData[this.nodeOptions.currentValue]){
            this.value = this.recordData[this.nodeOptions.currentValue]
        }
    },
    _render: function() {
        var self = this;
        var value = this.value;
        var ajax = require('web.ajax');
        var timeFormat = 'DD/MM/YYYY';
        var data_v =[];
        var data_a =[];
        var data_r = [];
        var data_q = [];
        var data_s = [];
        var canvas = this.$('.canvas')[0]
        var ctx = canvas.getContext("2d");
        localStorage.product_id = value;
        var enlace = "/get_buffer_changes/"+value.toString();
        var enlace_sale  = "/get_sales/"+value.toString();
        console.log(enlace_sale,'no')
        ajax.jsonRpc(enlace_sale,'call',{},{
            'async':false
        }).then(function (data) {
            data.forEach(element=>{
                const fecha = new Date(element.date);
                data_s.push({x:fecha,y:element.qty});
                console.log(element);
            })
        }
        )
        
        ajax.jsonRpc(enlace, 'call', {}, {
            'async': false
        }).then(function (data) {
            data.forEach(element=>{
                const fecha = new Date(element.create_date);
                if(element.type=='buffer'){
                    data_v.push({x:fecha,y:element.buffer_size});
                    data_a.push({x:fecha,y:2*element.buffer_size/3});
                    data_r.push({x:fecha,y:element.buffer_size/3});
                }else{
                    if(element.type=='available'){
                        data_q.push({x:fecha,y:element.qty_available})
                    }
                }
            })
            const tiempoTranscurrido = Date.now();
            const hoy = new Date(tiempoTranscurrido);
            data_v.push({x:hoy,y:data[data.length-1].buffer_size});
            data_a.push({x:hoy,y:2*data[data.length-1].buffer_size/3});
            data_r.push({x:hoy,y:data[data.length-1].buffer_size/3});
            data_q.push({x:hoy,y:data[data.length-1].qty_available});
            localStorage.buffer_size = data[data.length-1].buffer_size;
            
            
            const myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        //labels: labels,
                        datasets:[
                        {
                            stepped: true,
                            label:'Quantity On Hand',
                            data:data_q,
                            borderColor:'black',
                            tension:0.1,
                        },
                        {
                            stepped: true,
                            label:'Sales',
                            data:data_s,
                            borderColor:'blue',
                            tension:0.1,
                        },
                        {
                            fill:true,
                            data:data_r,
                            stepped: true,
                            backgroundColor:'rgba(241,64,64,0.4)',
                            borderColor:'rgba(241,64,64,1)',
                        },
                        {
                            fill:true,
                            data:data_a,
                            stepped: true,
                            backgroundColor:'rgba(235,194,50,0.4)',
                            borderColor:'rgba(235,194,50,1)',
                        },
                        {
                            label:'Buffer size',
                            fill:true,
                            data:data_v,
                            stepped: true,
                            backgroundColor:'rgba(53,200,85,0.4)',
                            borderColor:'rgba(53,200,85,1)',
                        },
                        ]
                    },
                    options: {
                        responsive:true,
                        scales: {
                            y: {
                                beginAtZero: true,
                            },
                            x: {
                                type: 'time',
                                time: {
                                    displayFormats: {
                                        quarter: 'MMM YYYY'
                                    },
                                },
                                title: {
                                    display: true,
                                    text: 'Fecha'
                                }
                            },
                            
                        },
                        plugins:{
                           legend: {
                                display: false
                           },
                            title: {
                                display: true,
                                text: 'Comportamiento historico del buffer'
                            },
                        },
                        tooltips: {
                            mode: 'nearest',
                            intersect: false
                        }
                    }
            });
        });
        
    },
})
fieldRegistry.add('chart_widget', ChartWidget);