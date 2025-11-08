from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum
from django.http import HttpResponse
from decimal import Decimal
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from datetime import date
import pandas as pd
import json
from .models import TipoDocumento, Cliente, Compra
from .serializers import (
    TipoDocumentoSerializer, 
    ClienteSerializer, 
    ClientePerfilSerializer,  # Serializer para consulta de perfil completo
    CompraSerializer,
    CompraSimpleSerializer
)
from .services_pandas import obtener_servicio_pandas


@api_view(['GET'])
def consultar_cliente_por_documento(request, numero_documento):
    """
    API que consulta por número de documento la información básica del cliente.
    
    Devuelve los campos esenciales del perfil:
    - Numero de documento
    - Nombre
    - Apellido  
    - Correo
    - Teléfono
    
    La consulta se hace directamente en la base de datos SQLite.
    
    URL: /api/clientes/consulta/{numero_documento}/
    """
    try:
        # Buscar cliente activo por número de documento
        cliente = Cliente.objects.get(
            numero_documento=numero_documento.strip(),
            activo=True
        )
        
        # Usar el serializer específico para consulta de perfil
        serializer = ClientePerfilSerializer(cliente)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Cliente encontrado exitosamente'
        }, status=status.HTTP_200_OK)
        
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': f'No se encontró ningún cliente con número de documento: {numero_documento}'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'success': False,
            'data': None,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def buscar_cliente(request):
    """
    Busca un cliente por tipo de documento y número de documento.
    
    Parámetros requeridos:
    - tipo_documento: Código del tipo de documento (CC, NIT, CE, PP, TI)
    - numero_documento: Número de documento del cliente
    """
    tipo_documento_codigo = request.GET.get('tipo_documento')
    numero_documento = request.GET.get('numero_documento')
    
    if not tipo_documento_codigo or not numero_documento:
        return Response({
            'error': 'Se requieren los parámetros tipo_documento y numero_documento'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Buscar tipo de documento
        tipo_documento = TipoDocumento.objects.get(
            codigo=tipo_documento_codigo.upper(),
            activo=True
        )
        
        # Buscar cliente
        cliente = Cliente.objects.get(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento.strip(),
            activo=True
        )
        
        serializer = ClienteSerializer(cliente)
        return Response(serializer.data)
        
    except TipoDocumento.DoesNotExist:
        return Response({
            'error': f'Tipo de documento "{tipo_documento_codigo}" no válido'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Cliente.DoesNotExist:
        return Response({
            'error': 'Cliente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def compras_cliente(request, cliente_id):
    """
    Obtiene todas las compras de un cliente específico.
    """
    cliente = get_object_or_404(Cliente, id=cliente_id, activo=True)
    
    compras = Compra.objects.filter(
        cliente=cliente
    ).order_by('-fecha_compra')
    
    # Aplicar filtros opcionales
    estado = request.GET.get('estado')
    if estado:
        compras = compras.filter(estado=estado)
    
    # Paginación
    page_size = int(request.GET.get('page_size', 10))
    page = int(request.GET.get('page', 1))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    compras_page = compras[start:end]
    total_count = compras.count()
    
    serializer = CompraSimpleSerializer(compras_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size
    })


class TipoDocumentoListView(generics.ListAPIView):
    """
    Lista todos los tipos de documento activos.
    """
    queryset = TipoDocumento.objects.filter(activo=True)
    serializer_class = TipoDocumentoSerializer


class ClienteListView(generics.ListAPIView):
    """
    Lista todos los clientes con filtros opcionales.
    """
    queryset = Cliente.objects.filter(activo=True)
    serializer_class = ClienteSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales
        ciudad = self.request.GET.get('ciudad')
        if ciudad:
            queryset = queryset.filter(ciudad__icontains=ciudad)
        
        departamento = self.request.GET.get('departamento')
        if departamento:
            queryset = queryset.filter(departamento__icontains=departamento)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(primer_nombre__icontains=search) |
                Q(primer_apellido__icontains=search) |
                Q(numero_documento__icontains=search) |
                Q(correo__icontains=search)
            )
        
        return queryset.order_by('-fecha_registro')


class ClienteDetailView(generics.RetrieveAPIView):
    """
    Detalle de un cliente específico.
    """
    queryset = Cliente.objects.filter(activo=True)
    serializer_class = ClienteSerializer


class CompraListView(generics.ListAPIView):
    """
    Lista todas las compras con filtros opcionales.
    """
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        metodo_pago = self.request.GET.get('metodo_pago')
        if metodo_pago:
            queryset = queryset.filter(metodo_pago=metodo_pago)
        
        return queryset.order_by('-fecha_compra')


class CompraDetailView(generics.RetrieveAPIView):
    """
    Detalle de una compra específica.
    """
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer


@api_view(['GET'])
def estadisticas_cliente(request, cliente_id):
    """
    Obtiene estadísticas de un cliente específico.
    """
    cliente = get_object_or_404(Cliente, id=cliente_id, activo=True)
    
    compras = cliente.compras.all()
    
    estadisticas = {
        'cliente': ClienteSerializer(cliente).data,
        'total_compras': compras.count(),
        'compras_completadas': compras.filter(estado='COMPLETADA').count(),
        'compras_pendientes': compras.filter(estado='PENDIENTE').count(),
        'monto_total': float(cliente.total_compras),
        'compra_mas_reciente': None,
        'compra_mas_antigua': None,
    }
    
    if compras.exists():
        compra_reciente = compras.order_by('-fecha_compra').first()
        compra_antigua = compras.order_by('fecha_compra').first()
        
        estadisticas['compra_mas_reciente'] = CompraSimpleSerializer(compra_reciente).data
        estadisticas['compra_mas_antigua'] = CompraSimpleSerializer(compra_antigua).data
    
    return Response(estadisticas)


@api_view(['GET'])
def reporte_fidelizacion_excel(request):
    """
    Genera un reporte Excel con clientes candidatos para fidelización usando Pandas.
    
    Criterios:
    - Clientes con compras del último mes >= $5,000,000 COP
    - Datos básicos del cliente + monto total último mes
    - Ordenados por monto de mayor a menor
    - AUTOMATIZADO CON PANDAS para mejor performance y análisis
    
    URL: /api/clientes/reporte/fidelizacion/
    """
    try:
        from datetime import datetime, timedelta
        
        # Obtener parámetro opcional de monto mínimo
        monto_minimo_param = request.GET.get('monto_minimo', '5000000')
        try:
            monto_minimo = Decimal(monto_minimo_param)
        except (ValueError, TypeError):
            monto_minimo = Decimal('5000000')  # Default: 5 millones
        
        # === PROCESAMIENTO CON PANDAS ===
        
        # Calcular fecha del último mes (últimos 30 días)
        fecha_limite = datetime.now() - timedelta(days=30)
        
        # Obtener datos de clientes y compras
        clientes_data = Cliente.objects.select_related('tipo_documento').values(
            'id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 
            'correo', 'telefono', 'direccion', 'ciudad', 'departamento', 
            'tipo_documento__nombre', 'numero_documento', 'fecha_registro', 'activo'
        )
        
        # Filtrar compras del último mes
        compras_data = Compra.objects.filter(
            estado__in=['COMPLETADA', 'ENTREGADA'],
            fecha_compra__gte=fecha_limite
        ).select_related('cliente').values(
            'cliente_id', 'total', 'fecha_compra', 'estado'
        )
        
        # Convertir a DataFrames de pandas
        df_clientes = pd.DataFrame(list(clientes_data))
        df_compras = pd.DataFrame(list(compras_data))
        
        if df_clientes.empty:
            return Response({
                'success': False,
                'message': f'No se encontraron clientes en el sistema'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if df_compras.empty:
            return Response({
                'success': False,
                'message': f'No se encontraron compras del último mes'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Procesar con pandas - Agrupar compras por cliente del último mes
        df_compras['total'] = df_compras['total'].astype(float)
        compras_mes = df_compras.groupby('cliente_id').agg({
            'total': ['sum', 'count'],
            'fecha_compra': 'max'
        }).round(2)
        
        # Aplanar columnas multinivel
        compras_mes.columns = ['total_ultimo_mes', 'cantidad_compras_mes', 'ultima_compra']
        compras_mes = compras_mes.reset_index()
        
        # Filtrar por monto mínimo usando pandas
        candidatos_df = compras_mes[compras_mes['total_ultimo_mes'] >= float(monto_minimo)]
        
        if candidatos_df.empty:
            return Response({
                'success': False,
                'message': f'No se encontraron clientes con compras del último mes >= ${monto_minimo:,.0f} COP'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Combinar con datos de clientes usando pandas merge
        reporte_df = pd.merge(candidatos_df, df_clientes, left_on='cliente_id', right_on='id')
        
        # Crear columna de nombre completo
        reporte_df['nombre_completo'] = (
            reporte_df['primer_nombre'].fillna('') + ' ' + 
            reporte_df['segundo_nombre'].fillna('') + ' ' +
            reporte_df['primer_apellido'].fillna('') + ' ' +
            reporte_df['segundo_apellido'].fillna('')
        ).str.replace('  ', ' ').str.strip()
        
        # Ordenar por monto del último mes (mayor a menor)
        reporte_final = reporte_df.sort_values('total_ultimo_mes', ascending=False)
        
        # === GENERAR EXCEL SIMPLIFICADO ===
        
        # Preparar DataFrame para exportación
        df_exportar = reporte_final[[
            'cliente_id', 'tipo_documento__nombre', 'numero_documento',
            'nombre_completo', 'correo', 'telefono', 'ciudad', 'departamento',
            'total_ultimo_mes', 'cantidad_compras_mes', 'ultima_compra'
        ]].copy()
        
        # Renombrar columnas
        df_exportar.columns = [
            'ID Cliente', 'Tipo Documento', 'Número Documento',
            'Nombre Completo', 'Email', 'Teléfono', 'Ciudad', 'Departamento',
            'Total Último Mes (COP)', 'Cantidad Compras', 'Última Compra'
        ]
        
        # Formatear fechas y montos
        df_exportar['Última Compra'] = pd.to_datetime(df_exportar['Última Compra']).dt.strftime('%d/%m/%Y')
        df_exportar['Total Último Mes (COP)'] = df_exportar['Total Último Mes (COP)'].apply(lambda x: f"${x:,.0f}")
        
        # Crear respuesta HTTP para Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        timestamp = date.today().strftime('%Y%m%d')
        filename = f'reporte_fidelizacion_pandas_{timestamp}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Usar pandas ExcelWriter para generar el archivo
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            # Escribir datos principales
            df_exportar.to_excel(writer, sheet_name='Reporte Fidelización', index=False)
            
            # Obtener worksheet para agregar información adicional
            worksheet = writer.sheets['Reporte Fidelización']
            
            # Agregar información del reporte al final
            info_row = len(df_exportar) + 3
            worksheet[f'A{info_row}'] = f"Reporte generado: {date.today().strftime('%d/%m/%Y')}"
            worksheet[f'A{info_row + 1}'] = f"Criterio mínimo: ${monto_minimo:,.0f} COP"
            worksheet[f'A{info_row + 2}'] = f"Total candidatos: {len(df_exportar)}"
            worksheet[f'A{info_row + 3}'] = "Procesado automáticamente con Pandas"
            
            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return response
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error generando reporte con Pandas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === FUNCIONES DE EXPORTACIÓN CON PANDAS ===

@api_view(['GET'])
def exportar_clientes_csv_pandas(request):
    """
    Exporta todos los clientes a CSV usando Pandas para automatización.
    Incluye análisis automático y estadísticas.
    """
    try:
        # Obtener datos usando pandas
        clientes_data = Cliente.objects.select_related('tipo_documento').values(
            'id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'correo', 'telefono', 'direccion', 'ciudad', 'departamento', 
            'tipo_documento__nombre', 'numero_documento', 'fecha_registro', 'activo'
        )
        
        # Convertir a DataFrame de pandas
        df_clientes = pd.DataFrame(list(clientes_data))
        
        if df_clientes.empty:
            return Response({
                'success': False,
                'message': 'No hay clientes para exportar'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Formatear datos con pandas
        df_clientes['nombre_completo'] = (
            df_clientes['primer_nombre'].fillna('') + ' ' + 
            df_clientes['segundo_nombre'].fillna('') + ' ' +
            df_clientes['primer_apellido'].fillna('') + ' ' +
            df_clientes['segundo_apellido'].fillna('')
        ).str.replace('  ', ' ').str.strip()
        df_clientes['fecha_registro'] = pd.to_datetime(df_clientes['fecha_registro']).dt.strftime('%d/%m/%Y')
        df_clientes['estado'] = df_clientes['activo'].map({True: 'Activo', False: 'Inactivo'})
        
        # Seleccionar columnas para exportación
        columnas_export = [
            'id', 'tipo_documento__nombre', 'numero_documento', 
            'nombre_completo', 'correo', 'telefono', 'direccion',
            'ciudad', 'departamento', 'fecha_registro', 'estado'
        ]
        
        df_export = df_clientes[columnas_export].copy()
        
        # Renombrar columnas
        df_export.columns = [
            'ID', 'Tipo Documento', 'Número Documento',
            'Nombre Completo', 'Email', 'Teléfono', 'Dirección',
            'Ciudad', 'Departamento', 'Fecha Registro', 'Estado'
        ]
        
        # Crear respuesta CSV con pandas
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        timestamp = date.today().strftime('%Y%m%d')
        filename = f'clientes_pandas_export_{timestamp}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Exportar a CSV usando pandas
        df_export.to_csv(response, index=False, encoding='utf-8')
        
        return response
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error exportando CSV con Pandas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def exportar_clientes_excel_pandas(request):
    """
    Exporta clientes a Excel con múltiples hojas usando Pandas.
    Incluye análisis automático, estadísticas y gráficos.
    """
    try:
        # Obtener datos
        clientes_data = Cliente.objects.select_related('tipo_documento').values(
            'id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'correo', 'telefono', 'direccion', 'ciudad', 'departamento', 
            'tipo_documento__nombre', 'numero_documento', 'fecha_registro', 'activo'
        )
        
        compras_data = Compra.objects.select_related('cliente').values(
            'cliente_id', 'total', 'fecha_compra', 'estado'
        )
        
        # Convertir a DataFrames
        df_clientes = pd.DataFrame(list(clientes_data))
        df_compras = pd.DataFrame(list(compras_data))
        
        if df_clientes.empty:
            return Response({
                'success': False,
                'message': 'No hay datos para exportar'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Preparar respuesta Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        timestamp = date.today().strftime('%Y%m%d')
        filename = f'reporte_completo_pandas_{timestamp}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Crear Excel con múltiples hojas usando pandas
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            
            # === HOJA 1: CLIENTES ===
            df_clientes_formatted = df_clientes.copy()
            df_clientes_formatted['nombre_completo'] = (
                df_clientes_formatted['primer_nombre'].fillna('') + ' ' + 
                df_clientes_formatted['segundo_nombre'].fillna('') + ' ' +
                df_clientes_formatted['primer_apellido'].fillna('') + ' ' +
                df_clientes_formatted['segundo_apellido'].fillna('')
            ).str.replace('  ', ' ').str.strip()
            # Convertir fecha a naive datetime sin timezone
            df_clientes_formatted['fecha_registro'] = pd.to_datetime(df_clientes_formatted['fecha_registro']).dt.tz_localize(None).dt.strftime('%d/%m/%Y')
            df_clientes_formatted['estado'] = df_clientes_formatted['activo'].map({True: 'Activo', False: 'Inactivo'})
            
            # Seleccionar columnas
            clientes_export = df_clientes_formatted[[
                'id', 'tipo_documento__nombre', 'numero_documento',
                'nombre_completo', 'correo', 'telefono', 'ciudad',
                'departamento', 'fecha_registro', 'estado'
            ]].copy()
            
            clientes_export.columns = [
                'ID', 'Tipo Documento', 'Número Documento',
                'Nombre Completo', 'Email', 'Teléfono', 'Ciudad',
                'Departamento', 'Fecha Registro', 'Estado'
            ]
            
            clientes_export.to_excel(writer, sheet_name='Clientes', index=False)
            
            # === HOJA 2: ANÁLISIS POR TIPO DOCUMENTO ===
            if not df_clientes.empty:
                # Usar copia original para análisis de fechas
                df_clientes_analisis = df_clientes.copy()
                df_clientes_analisis['fecha_registro'] = pd.to_datetime(df_clientes_analisis['fecha_registro']).dt.tz_localize(None)
                
                analisis_tipos = df_clientes_analisis.groupby('tipo_documento__nombre').agg({
                    'id': 'count',
                    'fecha_registro': ['min', 'max'],
                    'activo': lambda x: (x == True).sum()
                }).round(2)
                
                analisis_tipos.columns = ['Cantidad_Total', 'Primer_Registro', 'Último_Registro', 'Clientes_Activos']
                analisis_tipos = analisis_tipos.reset_index()
                analisis_tipos.columns = ['Tipo Documento', 'Cantidad Total', 'Primer Registro', 'Último Registro', 'Clientes Activos']
                
                analisis_tipos.to_excel(writer, sheet_name='Análisis Tipos Doc', index=False)
            
            # === HOJA 3: ANÁLISIS DE COMPRAS ===
            if not df_compras.empty:
                df_compras['total'] = df_compras['total'].astype(float)
                # Convertir fecha a naive datetime sin timezone
                df_compras['fecha_compra'] = pd.to_datetime(df_compras['fecha_compra']).dt.tz_localize(None)
                
                # Análisis por estado
                analisis_estados = df_compras.groupby('estado').agg({
                    'total': ['sum', 'mean', 'count'],
                    'fecha_compra': ['min', 'max']
                }).round(2)
                
                analisis_estados.columns = ['Monto_Total', 'Monto_Promedio', 'Cantidad', 'Fecha_Min', 'Fecha_Max']
                analisis_estados = analisis_estados.reset_index()
                analisis_estados.to_excel(writer, sheet_name='Análisis Compras', index=False)
                
                # Top clientes
                top_clientes = df_compras.groupby('cliente_id').agg({
                    'total': ['sum', 'count'],
                    'fecha_compra': ['min', 'max']
                }).round(2)
                
                top_clientes.columns = ['Monto_Total', 'Cantidad_Compras', 'Primera_Compra', 'Última_Compra']
                top_clientes = top_clientes.reset_index().sort_values('Monto_Total', ascending=False).head(20)
                top_clientes.to_excel(writer, sheet_name='Top 20 Clientes', index=False)
            
            # === HOJA 4: ESTADÍSTICAS GENERALES ===
            estadisticas = {
                'Métrica': [
                    'Total Clientes',
                    'Clientes Activos',
                    'Clientes Inactivos',
                    'Tipos de Documento',
                    'Ciudades Diferentes',
                    'Departamentos Diferentes'
                ],
                'Valor': [
                    len(df_clientes),
                    len(df_clientes[df_clientes['activo'] == True]),
                    len(df_clientes[df_clientes['activo'] == False]),
                    df_clientes['tipo_documento__nombre'].nunique(),
                    df_clientes['ciudad'].nunique(),
                    df_clientes['departamento'].nunique()
                ]
            }
            
            if not df_compras.empty:
                estadisticas['Métrica'].extend([
                    'Total Compras',
                    'Monto Total Ventas',
                    'Ticket Promedio',
                    'Cliente Más Activo (Compras)'
                ])
                estadisticas['Valor'].extend([
                    len(df_compras),
                    f"${df_compras['total'].sum():,.0f}",
                    f"${df_compras['total'].mean():,.0f}",
                    df_compras['cliente_id'].mode().iloc[0] if not df_compras['cliente_id'].mode().empty else 'N/A'
                ])
            
            df_stats = pd.DataFrame(estadisticas)
            df_stats.to_excel(writer, sheet_name='Estadísticas', index=False)
            
            # Ajustar anchos de columnas
            for sheet_name, sheet in writer.sheets.items():
                for column in sheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    sheet.column_dimensions[column_letter].width = adjusted_width
        
        return response
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error exportando Excel con Pandas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def exportar_clientes_txt_pandas(request):
    """
    Exporta clientes a archivo TXT con formato estructurado usando Pandas.
    """
    try:
        # Obtener datos
        clientes_data = Cliente.objects.select_related('tipo_documento').values(
            'id', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'correo', 'telefono', 'direccion', 'ciudad', 'departamento', 
            'tipo_documento__nombre', 'numero_documento', 'fecha_registro', 'activo'
        )
        
        # Convertir a DataFrame
        df_clientes = pd.DataFrame(list(clientes_data))
        
        if df_clientes.empty:
            return Response({
                'success': False,
                'message': 'No hay clientes para exportar'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Crear respuesta TXT
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        timestamp = date.today().strftime('%Y%m%d')
        filename = f'clientes_reporte_{timestamp}.txt'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Generar contenido del archivo usando pandas
        contenido = []
        contenido.append("=" * 80)
        contenido.append("REPORTE DE CLIENTES - RÍOS DEL DESIERTO")
        contenido.append(f"Generado automáticamente con Pandas - {date.today().strftime('%d/%m/%Y')}")
        contenido.append("=" * 80)
        contenido.append()
        
        # Estadísticas generales
        contenido.append("ESTADÍSTICAS GENERALES:")
        contenido.append("-" * 30)
        contenido.append(f"Total de clientes: {len(df_clientes)}")
        contenido.append(f"Clientes activos: {len(df_clientes[df_clientes['activo'] == True])}")
        contenido.append(f"Clientes inactivos: {len(df_clientes[df_clientes['activo'] == False])}")
        contenido.append(f"Tipos de documento: {df_clientes['tipo_documento__nombre'].nunique()}")
        contenido.append(f"Ciudades diferentes: {df_clientes['ciudad'].nunique()}")
        contenido.append()
        
        # Análisis por tipo de documento
        contenido.append("ANÁLISIS POR TIPO DE DOCUMENTO:")
        contenido.append("-" * 40)
        tipos_analisis = df_clientes.groupby('tipo_documento__nombre').size()
        for tipo, cantidad in tipos_analisis.items():
            contenido.append(f"{tipo}: {cantidad} clientes")
        contenido.append()
        
        # Listado de clientes
        contenido.append("LISTADO DETALLADO DE CLIENTES:")
        contenido.append("-" * 50)
        
        # Formatear fechas
        df_clientes['fecha_registro'] = pd.to_datetime(df_clientes['fecha_registro']).dt.strftime('%d/%m/%Y')
        
        # Crear nombre completo
        df_clientes['nombre_completo'] = (
            df_clientes['primer_nombre'].fillna('') + ' ' + 
            df_clientes['segundo_nombre'].fillna('') + ' ' +
            df_clientes['primer_apellido'].fillna('') + ' ' +
            df_clientes['segundo_apellido'].fillna('')
        ).str.replace('  ', ' ').str.strip()
        
        for _, cliente in df_clientes.iterrows():
            contenido.append(f"ID: {cliente['id']}")
            contenido.append(f"Nombre: {cliente['nombre_completo']}")
            contenido.append(f"Documento: {cliente['tipo_documento__nombre']} {cliente['numero_documento']}")
            contenido.append(f"Email: {cliente['correo']}")
            contenido.append(f"Teléfono: {cliente['telefono']}")
            contenido.append(f"Dirección: {cliente['direccion']}")
            contenido.append(f"Ciudad: {cliente['ciudad']}, {cliente['departamento']}")
            contenido.append(f"Registro: {cliente['fecha_registro']}")
            contenido.append(f"Estado: {'Activo' if cliente['activo'] else 'Inactivo'}")
            contenido.append("-" * 50)
        
        contenido.append()
        contenido.append("Reporte generado automáticamente con Pandas")
        contenido.append("Sistema de Gestión de Clientes - Ríos del Desierto")
        
        # Escribir contenido
        response.write('\n'.join(contenido))
        
        return response
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error exportando TXT con Pandas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
