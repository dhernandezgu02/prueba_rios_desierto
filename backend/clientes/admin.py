from django.contrib import admin
from .models import TipoDocumento, Cliente, Compra


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('codigo', 'nombre')
    readonly_fields = ('fecha_creacion',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'numero_documento', 'nombre_completo', 'correo', 'telefono', 
        'ciudad', 'activo', 'fecha_registro'
    )
    list_filter = (
        'activo', 'tipo_documento', 'genero', 'ciudad', 
        'departamento', 'fecha_registro'
    )
    search_fields = (
        'numero_documento', 'primer_nombre', 'primer_apellido', 
        'correo', 'telefono'
    )
    readonly_fields = (
        'fecha_registro', 'fecha_actualizacion', 'ultima_compra', 
        'total_compras', 'edad'
    )
    date_hierarchy = 'fecha_registro'
    
    fieldsets = (
        ('Información del Documento', {
            'fields': ('tipo_documento', 'numero_documento')
        }),
        ('Información Personal', {
            'fields': (
                'primer_nombre', 'segundo_nombre', 'primer_apellido', 
                'segundo_apellido', 'fecha_nacimiento', 'genero'
            )
        }),
        ('Información de Contacto', {
            'fields': ('correo', 'telefono')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'departamento', 'codigo_postal')
        }),
        ('Estado y Control', {
            'fields': ('activo',)
        }),
        ('Información del Sistema', {
            'fields': (
                'fecha_registro', 'fecha_actualizacion', 'ultima_compra', 
                'total_compras', 'edad'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_completo(self, obj):
        return obj.nombre_completo
    nombre_completo.short_description = 'Nombre Completo'


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        'numero_orden', 'cliente_nombre', 'fecha_compra', 'total', 
        'estado', 'metodo_pago', 'canal_venta'
    )
    list_filter = (
        'estado', 'metodo_pago', 'canal_venta', 'fecha_compra', 
        'ciudad_entrega'
    )
    search_fields = (
        'numero_orden', 'cliente__numero_documento', 
        'cliente__primer_nombre', 'cliente__primer_apellido',
        'codigo_seguimiento'
    )
    readonly_fields = (
        'numero_orden', 'fecha_compra', 'fecha_actualizacion',
        'dias_desde_compra', 'margen_descuento'
    )
    date_hierarchy = 'fecha_compra'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_orden', 'cliente', 'fecha_compra', 'estado')
        }),
        ('Productos y Descripción', {
            'fields': ('descripcion_productos', 'cantidad_productos')
        }),
        ('Montos', {
            'fields': (
                'subtotal', 'descuento', 'impuestos', 
                'costo_envio', 'total'
            )
        }),
        ('Pago', {
            'fields': ('metodo_pago', 'numero_cuotas')
        }),
        ('Entrega', {
            'fields': (
                'direccion_entrega', 'ciudad_entrega', 
                'fecha_entrega_estimada', 'fecha_entrega_real',
                'codigo_seguimiento'
            )
        }),
        ('Canal y Control', {
            'fields': ('canal_venta', 'usuario_creacion', 'observaciones')
        }),
        ('Información del Sistema', {
            'fields': (
                'fecha_actualizacion', 'dias_desde_compra', 'margen_descuento'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def cliente_nombre(self, obj):
        return obj.cliente.nombre_completo
    cliente_nombre.short_description = 'Cliente'
    cliente_nombre.admin_order_field = 'cliente__primer_nombre'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Solo para nuevas compras
            obj.usuario_creacion = request.user.username
        super().save_model(request, obj, form, change)
