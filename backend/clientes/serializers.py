from rest_framework import serializers
from .models import TipoDocumento, Cliente, Compra


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ['id', 'codigo', 'nombre', 'descripcion']


class ClientePerfilSerializer(serializers.ModelSerializer):
    """
    Serializer para consulta de perfil básico del cliente.
    Devuelve los campos esenciales del cliente:
    - Numero de documento
    - Nombre 
    - Apellido
    - Correo
    - Teléfono
    """
    numero_documento = serializers.CharField()
    nombre = serializers.CharField(source='primer_nombre')
    apellido = serializers.CharField(source='primer_apellido')
    correo = serializers.EmailField()
    telefono = serializers.CharField()
    
    class Meta:
        model = Cliente
        fields = ['numero_documento', 'nombre', 'apellido', 'correo', 'telefono']


class ClienteSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    edad = serializers.ReadOnlyField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_documento', 'numero_documento', 'primer_nombre', 
            'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'nombre_completo',
            'correo', 'telefono', 'ciudad', 'departamento', 'direccion',
            'fecha_nacimiento', 'edad', 'genero', 'codigo_postal',
            'activo', 'fecha_registro', 'fecha_actualizacion',
            'ultima_compra', 'total_compras'
        ]


class CompraSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    dias_desde_compra = serializers.ReadOnlyField()
    margen_descuento = serializers.ReadOnlyField()
    
    class Meta:
        model = Compra
        fields = [
            'id', 'cliente', 'numero_orden', 'fecha_compra',
            'descripcion_productos', 'cantidad_productos',
            'subtotal', 'descuento', 'impuestos', 'costo_envio', 'total',
            'metodo_pago', 'numero_cuotas', 'canal_venta',
            'direccion_entrega', 'ciudad_entrega', 'estado',
            'fecha_entrega_estimada', 'fecha_entrega_real',
            'observaciones', 'codigo_seguimiento',
            'dias_desde_compra', 'margen_descuento'
        ]


class CompraSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar compras de un cliente"""
    dias_desde_compra = serializers.ReadOnlyField()
    
    class Meta:
        model = Compra
        fields = [
            'id', 'numero_orden', 'fecha_compra', 'descripcion_productos',
            'total', 'estado', 'metodo_pago', 'canal_venta', 'dias_desde_compra'
        ]