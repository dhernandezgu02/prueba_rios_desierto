from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Endpoint para consulta directa por número de documento
    path('consulta/<str:numero_documento>/', views.consultar_cliente_por_documento, name='consultar_cliente_por_documento'),
    
    # Endpoint para buscar clientes con parámetros
    path('buscar/', views.buscar_cliente, name='buscar_cliente'),
    
    # Compras de un cliente específico
    path('<int:cliente_id>/compras/', views.compras_cliente, name='compras_cliente'),
    
    # Estadísticas de un cliente
    path('<int:cliente_id>/estadisticas/', views.estadisticas_cliente, name='estadisticas_cliente'),
    
    # Reportes y exportaciones con Pandas
    path('reporte/fidelizacion/', views.reporte_fidelizacion_excel, name='reporte_fidelizacion'),
    path('exportar/csv/', views.exportar_clientes_csv_pandas, name='exportar_csv'),
    path('exportar/excel/', views.exportar_clientes_excel_pandas, name='exportar_excel'),
    path('exportar/txt/', views.exportar_clientes_txt_pandas, name='exportar_txt'),
    
    # CRUD básico para clientes
    path('', views.ClienteListView.as_view(), name='cliente_list'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    
    # Tipos de documento
    path('tipos-documento/', views.TipoDocumentoListView.as_view(), name='tipos_documento'),
    
    # Compras
    path('compras/', views.CompraListView.as_view(), name='compra_list'),
    path('compras/<int:pk>/', views.CompraDetailView.as_view(), name='compra_detail'),
]