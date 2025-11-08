"""
Servicios de análisis de datos con Pandas
Automatización de procesamiento de información de clientes y compras
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q
from .models import Cliente, Compra, TipoDocumento


class AnalisisClientesPandas:
    """
    Servicio de análisis automatizado de clientes usando Pandas
    Proporciona funcionalidades avanzadas de procesamiento de datos
    """
    
    def __init__(self):
        self.df_clientes = None
        self.df_compras = None
        self.df_completo = None
    
    def cargar_datos(self):
        """Carga los datos desde Django ORM a DataFrames de Pandas"""
        
        # Cargar clientes
        clientes_data = Cliente.objects.select_related('tipo_documento').values(
            'id', 'nombre', 'apellido', 'email', 'telefono', 'direccion',
            'tipo_documento__nombre', 'numero_documento', 'fecha_registro'
        )
        self.df_clientes = pd.DataFrame(list(clientes_data))
        
        # Cargar compras
        compras_data = Compra.objects.select_related('cliente').values(
            'id', 'cliente_id', 'fecha_compra', 'monto', 'estado',
            'descripcion', 'cliente__nombre', 'cliente__apellido',
            'cliente__numero_documento'
        )
        self.df_compras = pd.DataFrame(list(compras_data))
        
        # Convertir tipos de datos
        if not self.df_clientes.empty:
            self.df_clientes['fecha_registro'] = pd.to_datetime(self.df_clientes['fecha_registro'])
        
        if not self.df_compras.empty:
            self.df_compras['fecha_compra'] = pd.to_datetime(self.df_compras['fecha_compra'])
            self.df_compras['monto'] = self.df_compras['monto'].astype(float)
            
        return self
    
    def generar_dataframe_completo(self):
        """Genera un DataFrame completo con información consolidada de clientes y compras"""
        if self.df_clientes.empty or self.df_compras.empty:
            self.cargar_datos()
        
        # Merge de datos
        self.df_completo = pd.merge(
            self.df_compras,
            self.df_clientes,
            left_on='cliente_id',
            right_on='id',
            suffixes=('_compra', '_cliente')
        )
        
        return self.df_completo
    
    def analisis_fidelizacion_automatizado(self):
        """
        Análisis automatizado de fidelización usando Pandas
        Identifica clientes con compras >$5MM COP mensuales
        """
        if self.df_completo is None:
            self.generar_dataframe_completo()
        
        # Filtrar solo compras completadas
        df_completadas = self.df_completo[
            self.df_completo['estado'].isin(['COMPLETADA', 'ENTREGADA'])
        ].copy()
        
        # Agregar columna de año-mes para agrupación
        df_completadas['year_month'] = df_completadas['fecha_compra'].dt.to_period('M')
        
        # Calcular compras mensuales por cliente usando pandas
        compras_mensuales = df_completadas.groupby(['cliente_id', 'year_month']).agg({
            'monto': 'sum',
            'id_compra': 'count',
            'cliente__nombre': 'first',
            'cliente__apellido': 'first',
            'numero_documento_x': 'first',
            'email': 'first',
            'telefono': 'first'
        }).reset_index()
        
        # Renombrar columnas
        compras_mensuales.columns = [
            'cliente_id', 'mes', 'monto_total', 'cantidad_compras',
            'nombre', 'apellido', 'numero_documento', 'email', 'telefono'
        ]
        
        # Filtrar clientes con compras >$5,000,000 COP mensuales
        clientes_fidelizados = compras_mensuales[
            compras_mensuales['monto_total'] > 5000000
        ]
        
        # Estadísticas adicionales usando pandas
        if not clientes_fidelizados.empty:
            stats = {
                'total_clientes_fidelizados': len(clientes_fidelizados['cliente_id'].unique()),
                'monto_promedio_mensual': clientes_fidelizados['monto_total'].mean(),
                'monto_maximo_mensual': clientes_fidelizados['monto_total'].max(),
                'monto_minimo_mensual': clientes_fidelizados['monto_total'].min(),
                'compras_promedio_mensual': clientes_fidelizados['cantidad_compras'].mean(),
                'meses_activos': len(clientes_fidelizados['mes'].unique())
            }
            
            # Ranking de mejores clientes
            ranking = clientes_fidelizados.groupby(['cliente_id', 'nombre', 'apellido', 'numero_documento']).agg({
                'monto_total': ['sum', 'mean', 'count'],
                'cantidad_compras': 'sum'
            }).round(2)
            
            ranking.columns = ['monto_total_acumulado', 'monto_promedio_mensual', 'meses_activos', 'total_compras']
            ranking = ranking.reset_index().sort_values('monto_total_acumulado', ascending=False)
            
            return {
                'clientes_fidelizados': clientes_fidelizados.to_dict('records'),
                'estadisticas': stats,
                'ranking_clientes': ranking.to_dict('records')
            }
        
        return {
            'clientes_fidelizados': [],
            'estadisticas': {},
            'ranking_clientes': []
        }
    
    def generar_reporte_exportacion_pandas(self, formato='excel'):
        """
        Genera reportes de exportación usando pandas con análisis automatizado
        """
        if self.df_completo is None:
            self.generar_dataframe_completo()
        
        # Análisis por tipo de documento
        analisis_tipo_doc = self.df_clientes.groupby('tipo_documento__nombre').agg({
            'id': 'count',
            'fecha_registro': ['min', 'max']
        }).round(2)
        analisis_tipo_doc.columns = ['cantidad_clientes', 'primer_registro', 'ultimo_registro']
        
        # Análisis de compras por estado
        analisis_compras = self.df_compras.groupby('estado').agg({
            'monto': ['sum', 'mean', 'count'],
            'fecha_compra': ['min', 'max']
        }).round(2)
        analisis_compras.columns = ['monto_total', 'monto_promedio', 'cantidad', 'fecha_min', 'fecha_max']
        
        # Análisis temporal (compras por mes)
        self.df_compras['mes'] = self.df_compras['fecha_compra'].dt.to_period('M')
        analisis_temporal = self.df_compras.groupby('mes').agg({
            'monto': ['sum', 'mean'],
            'id': 'count'
        }).round(2)
        analisis_temporal.columns = ['monto_total', 'monto_promedio', 'cantidad_compras']
        
        # Top clientes por compras
        top_clientes = self.df_completo.groupby(['cliente_id', 'cliente__nombre', 'cliente__apellido', 'numero_documento_x']).agg({
            'monto': ['sum', 'count'],
            'fecha_compra': ['min', 'max']
        }).round(2)
        top_clientes.columns = ['monto_total', 'cantidad_compras', 'primera_compra', 'ultima_compra']
        top_clientes = top_clientes.reset_index().sort_values('monto_total', ascending=False).head(10)
        
        return {
            'resumen_tipos_documento': analisis_tipo_doc.to_dict('index'),
            'resumen_compras_estado': analisis_compras.to_dict('index'),
            'analisis_temporal': analisis_temporal.to_dict('index'),
            'top_10_clientes': top_clientes.to_dict('records'),
            'total_clientes': len(self.df_clientes),
            'total_compras': len(self.df_compras),
            'monto_total_ventas': float(self.df_compras['monto'].sum()),
            'ticket_promedio': float(self.df_compras['monto'].mean())
        }
    
    def busqueda_avanzada_pandas(self, filtros):
        """
        Búsqueda avanzada de clientes usando pandas para mejor performance
        """
        if self.df_clientes.empty:
            self.cargar_datos()
        
        df_filtrado = self.df_clientes.copy()
        
        # Aplicar filtros usando pandas
        if filtros.get('query'):
            query = filtros['query'].lower()
            mask = (
                df_filtrado['nombre'].str.lower().str.contains(query, na=False) |
                df_filtrado['apellido'].str.lower().str.contains(query, na=False) |
                df_filtrado['email'].str.lower().str.contains(query, na=False) |
                df_filtrado['numero_documento'].str.contains(query, na=False) |
                df_filtrado['telefono'].str.contains(query, na=False)
            )
            df_filtrado = df_filtrado[mask]
        
        if filtros.get('tipo_documento'):
            df_filtrado = df_filtrado[
                df_filtrado['tipo_documento__nombre'] == filtros['tipo_documento']
            ]
        
        if filtros.get('fecha_desde'):
            fecha_desde = pd.to_datetime(filtros['fecha_desde'])
            df_filtrado = df_filtrado[df_filtrado['fecha_registro'] >= fecha_desde]
        
        if filtros.get('fecha_hasta'):
            fecha_hasta = pd.to_datetime(filtros['fecha_hasta'])
            df_filtrado = df_filtrado[df_filtrado['fecha_registro'] <= fecha_hasta]
        
        # Ordenamiento
        if filtros.get('ordenar_por'):
            campo_orden = filtros['ordenar_por']
            ascending = filtros.get('orden', 'asc') == 'asc'
            df_filtrado = df_filtrado.sort_values(campo_orden, ascending=ascending)
        
        return df_filtrado.to_dict('records')
    
    def prediccion_tendencias(self):
        """
        Análisis predictivo de tendencias usando pandas
        """
        if self.df_compras.empty:
            self.cargar_datos()
        
        # Tendencia de ventas por mes
        ventas_mensuales = self.df_compras.groupby(
            self.df_compras['fecha_compra'].dt.to_period('M')
        ).agg({
            'monto': ['sum', 'mean', 'count']
        }).round(2)
        
        ventas_mensuales.columns = ['ventas_totales', 'ticket_promedio', 'cantidad_transacciones']
        
        # Calcular tendencia (crecimiento mes a mes)
        ventas_mensuales['crecimiento_ventas'] = ventas_mensuales['ventas_totales'].pct_change() * 100
        ventas_mensuales['crecimiento_transacciones'] = ventas_mensuales['cantidad_transacciones'].pct_change() * 100
        
        # Proyección simple para próximo mes (promedio últimos 3 meses)
        ultimos_meses = ventas_mensuales.tail(3)
        proyeccion = {
            'ventas_proyectadas': float(ultimos_meses['ventas_totales'].mean()),
            'ticket_proyectado': float(ultimos_meses['ticket_promedio'].mean()),
            'transacciones_proyectadas': int(ultimos_meses['cantidad_transacciones'].mean())
        }
        
        return {
            'tendencias_historicas': ventas_mensuales.to_dict('index'),
            'proyeccion_proximo_mes': proyeccion
        }


def obtener_servicio_pandas():
    """Factory function para obtener instancia del servicio de análisis"""
    return AnalisisClientesPandas()