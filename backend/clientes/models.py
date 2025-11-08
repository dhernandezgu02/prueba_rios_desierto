from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from decimal import Decimal


class TipoDocumento(models.Model):
    """
    Tipos de documento de identidad.
    Separar en tabla independiente es una buena práctica para normalización.
    """
    codigo = models.CharField(max_length=10, unique=True, help_text="CC, TI, CE, PP, etc.")
    nombre = models.CharField(max_length=50, help_text="Cédula de Ciudadanía, Tarjeta de Identidad, etc.")
    descripcion = models.TextField(blank=True, help_text="Descripción adicional del tipo de documento")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documentos"
        ordering = ['nombre']
        
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Cliente(models.Model):
    """
    Modelo principal de clientes con validaciones y campos adicionales.
    Demuestra uso de validators, choices, y relaciones FK.
    """
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decir'),
    ]
    
    # Información de documento
    tipo_documento = models.ForeignKey(
        TipoDocumento, 
        on_delete=models.PROTECT,
        help_text="Tipo de documento de identidad"
    )
    numero_documento = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Número de documento sin puntos ni espacios"
    )
    
    # Nombres y apellidos
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True, null=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True, null=True)
    
    # Información de contacto
    correo = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Ingrese un correo electrónico válido")]
    )
    
    # Validator para teléfono
    telefono_validator = RegexValidator(
        regex=r'^\+?57?[0-9]{10,12}$',
        message="Formato: '+57XXXXXXXXXX' o 'XXXXXXXXXX'"
    )
    telefono = models.CharField(
        max_length=15,
        validators=[telefono_validator],
        help_text="Número de teléfono con código de país opcional"
    )
    
    # Información adicional
    fecha_nacimiento = models.DateField(
        help_text="Fecha de nacimiento del cliente"
    )
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        blank=True,
        null=True
    )
    
    # Dirección
    direccion = models.TextField(help_text="Dirección completa de residencia")
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    
    # Control y auditoría
    activo = models.BooleanField(
        default=True,
        help_text="Cliente activo en el sistema"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de registro en el sistema"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización de datos"
    )
    
    # Campos calculados para análisis
    ultima_compra = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Fecha de la última compra realizada"
    )
    total_compras = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total acumulado de todas las compras"
    )
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['numero_documento']),
            models.Index(fields=['correo']),
            models.Index(fields=['fecha_registro']),
            models.Index(fields=['activo']),
        ]
        
    def __str__(self):
        return f"{self.numero_documento} - {self.nombre_completo}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        nombres = [self.primer_nombre]
        if self.segundo_nombre:
            nombres.append(self.segundo_nombre)
        
        apellidos = [self.primer_apellido]
        if self.segundo_apellido:
            apellidos.append(self.segundo_apellido)
            
        return f"{' '.join(nombres)} {' '.join(apellidos)}"
    
    @property
    def edad(self):
        """Calcula la edad actual del cliente"""
        from datetime import date
        today = date.today()
        edad = today.year - self.fecha_nacimiento.year
        if today < self.fecha_nacimiento.replace(year=today.year):
            edad -= 1
        return edad
    
    def actualizar_estadisticas_compras(self):
        """Actualiza las estadísticas de compras del cliente"""
        # Estados válidos para contabilizar en estadísticas
        estados_validos = ['COMPLETADA', 'PENDIENTE', 'PROCESANDO', 'ENVIADO', 'ENTREGADO']
        compras = self.compras.filter(estado__in=estados_validos)
        
        if compras.exists():
            self.ultima_compra = compras.order_by('-fecha_compra').first().fecha_compra
            self.total_compras = sum(compra.total for compra in compras)
        else:
            self.ultima_compra = None
            self.total_compras = Decimal('0.00')
        self.save(update_fields=['ultima_compra', 'total_compras'])

    def calcular_compras_ultimo_mes(self):
        """Calcula el monto total de compras del último mes"""
        from datetime import date, datetime
        from dateutil.relativedelta import relativedelta
        
        # Fecha de hace un mes
        fecha_limite = date.today() - relativedelta(months=1)
        
        # Estados válidos para contabilizar
        estados_validos = ['COMPLETADA', 'PENDIENTE', 'PROCESANDO', 'ENVIADO', 'ENTREGADO']
        
        # Filtrar compras del último mes
        compras_ultimo_mes = self.compras.filter(
            fecha_compra__gte=fecha_limite,
            estado__in=estados_validos
        )
        
        # Calcular total y cantidad
        total_mes = sum(compra.total for compra in compras_ultimo_mes)
        cantidad_mes = compras_ultimo_mes.count()
        
        return {
            'total_ultimo_mes': total_mes,
            'cantidad_ultimo_mes': cantidad_mes,
            'fecha_desde': fecha_limite,
            'compras_detalle': compras_ultimo_mes
        }

    @classmethod
    def obtener_candidatos_fidelizacion(cls, monto_minimo=Decimal('5000000')):
        """
        Obtiene clientes candidatos para fidelización.
        Criterio: compras del último mes >= monto_minimo
        """
        candidatos = []
        
        for cliente in cls.objects.filter(activo=True):
            estadisticas_mes = cliente.calcular_compras_ultimo_mes()
            
            if estadisticas_mes['total_ultimo_mes'] >= monto_minimo:
                candidatos.append({
                    'cliente': cliente,
                    'total_ultimo_mes': estadisticas_mes['total_ultimo_mes'],
                    'cantidad_compras_mes': estadisticas_mes['cantidad_ultimo_mes'],
                    'fecha_desde': estadisticas_mes['fecha_desde']
                })
        
        # Ordenar por monto de mayor a menor
        candidatos.sort(key=lambda x: x['total_ultimo_mes'], reverse=True)
        
        return candidatos


class Compra(models.Model):
    """
    Modelo de compras asociadas a cada cliente.
    Incluye campos para análisis y seguimiento detallado.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESANDO', 'Procesando'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('DEVUELTA', 'Devuelta'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('PSE', 'PSE'),
        ('NEQUI', 'Nequi'),
        ('DAVIPLATA', 'Daviplata'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
    ]
    
    CANAL_VENTA_CHOICES = [
        ('WEB', 'Página Web'),
        ('MOVIL', 'Aplicación Móvil'),
        ('TELEFONO', 'Teléfono'),
        ('TIENDA', 'Tienda Física'),
        ('WHATSAPP', 'WhatsApp'),
    ]
    
    # Relación con cliente
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,  # Proteger para no perder datos históricos
        related_name='compras',
        help_text="Cliente que realizó la compra"
    )
    
    # Identificación de la compra
    numero_orden = models.CharField(
        max_length=20,
        unique=True,
        help_text="Número único de orden de compra"
    )
    fecha_compra = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha y hora de la compra"
    )
    
    # Detalles de la compra
    descripcion_productos = models.TextField(
        help_text="Descripción de los productos comprados"
    )
    cantidad_productos = models.PositiveIntegerField(
        default=1,
        help_text="Cantidad total de productos"
    )
    
    # Montos
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Subtotal antes de descuentos e impuestos"
    )
    descuento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Descuento aplicado"
    )
    impuestos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Impuestos (IVA, etc.)"
    )
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Costo de envío"
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total final de la compra"
    )
    
    # Información de pago y entrega
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        help_text="Método de pago utilizado"
    )
    numero_cuotas = models.PositiveIntegerField(
        default=1,
        help_text="Número de cuotas (si aplica)"
    )
    
    # Canal y ubicación
    canal_venta = models.CharField(
        max_length=20,
        choices=CANAL_VENTA_CHOICES,
        default='WEB',
        help_text="Canal por el cual se realizó la venta"
    )
    direccion_entrega = models.TextField(
        help_text="Dirección de entrega de la compra"
    )
    ciudad_entrega = models.CharField(
        max_length=100,
        help_text="Ciudad de entrega"
    )
    
    # Estado y seguimiento
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        help_text="Estado actual de la compra"
    )
    fecha_entrega_estimada = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha estimada de entrega"
    )
    fecha_entrega_real = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha real de entrega"
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones adicionales sobre la compra"
    )
    codigo_seguimiento = models.CharField(
        max_length=50,
        blank=True,
        help_text="Código de seguimiento del envío"
    )
    
    # Auditoría
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización del registro"
    )
    usuario_creacion = models.CharField(
        max_length=100,
        blank=True,
        help_text="Usuario que registró la compra"
    )
    
    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha_compra']
        indexes = [
            models.Index(fields=['numero_orden']),
            models.Index(fields=['cliente', '-fecha_compra']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_compra']),
            models.Index(fields=['metodo_pago']),
            models.Index(fields=['canal_venta']),
        ]
        
    def __str__(self):
        return f"Orden {self.numero_orden} - {self.cliente.nombre_completo} - ${self.total}"
    
    def save(self, *args, **kwargs):
        """Override save para generar número de orden automáticamente"""
        if not self.numero_orden:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.numero_orden = f"ORD-{timestamp}"
        
        super().save(*args, **kwargs)
        
        # Actualizar estadísticas del cliente después de guardar
        if self.estado == 'COMPLETADA':
            self.cliente.actualizar_estadisticas_compras()
    
    @property
    def dias_desde_compra(self):
        """Calcula los días transcurridos desde la compra"""
        return (timezone.now().date() - self.fecha_compra.date()).days
    
    @property
    def margen_descuento(self):
        """Calcula el porcentaje de descuento aplicado"""
        if self.subtotal > 0:
            return (self.descuento / self.subtotal) * 100
        return 0
