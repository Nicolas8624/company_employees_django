"""
Comando de Django para poblar la base de datos con datos de prueba.

Uso:
    python manage.py seed

Crea compañías y empleados de ejemplo para demostración.
"""
import logging

from django.core.management.base import BaseCommand

from infrastructure.database.models import CompaniaModel, EmpleadoModel, UsuarioModel

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para poblar la base de datos con datos de prueba."""

    help = "Poblar la base de datos con datos de prueba (seed data)"

    def handle(self, *args, **options):
        """Ejecutar el seed de datos."""
        self.stdout.write("Iniciando seed de datos...")
        logger.info("=== Iniciando seed de datos ===")

        # Verificar si ya existen datos
        if CompaniaModel.objects.exists():
            self.stdout.write(
                self.style.WARNING("Ya existen datos. Limpiando tablas...")
            )
            EmpleadoModel.objects.all().delete()
            UsuarioModel.objects.all().delete()
            CompaniaModel.objects.all().delete()


        # Crear compañías
        companias_data = [
            {
                "nombre": "TechCorp Colombia",
                "direccion": "Calle 100 #15-20, Bogotá",
                "telefono": "+57 601 555-0100",
            },
            {
                "nombre": "Innovación Digital SAS",
                "direccion": "Carrera 43A #1-50, Medellín",
                "telefono": "+57 604 555-0200",
            },
            {
                "nombre": "SoftDev Solutions",
                "direccion": "Av. 6N #25-120, Cali",
                "telefono": "+57 602 555-0300",
            },
        ]

        companias = []
        for data in companias_data:
            compania = CompaniaModel.objects.create(**data)
            companias.append(compania)
            logger.info("Seed: Compañía creada — %s (ID=%s)", compania.nombre, compania.pk)
            self.stdout.write(f"  [OK] Compania creada: {compania.nombre}")

        # Crear empleados
        empleados_data = [
            # TechCorp Colombia
            {"nombre": "Carlos", "apellido": "García", "correo": "carlos.garcia@techcorp.co",
             "cargo": "Desarrollador Senior", "salario": 8500000, "compania": companias[0]},
            {"nombre": "María", "apellido": "López", "correo": "maria.lopez@techcorp.co",
             "cargo": "Analista de Datos", "salario": 7200000, "compania": companias[0]},
            {"nombre": "Andrés", "apellido": "Martínez", "correo": "andres.martinez@techcorp.co",
             "cargo": "DevOps Engineer", "salario": 9000000, "compania": companias[0]},
            # Innovación Digital SAS
            {"nombre": "Laura", "apellido": "Rodríguez", "correo": "laura.rodriguez@innovacion.co",
             "cargo": "Product Manager", "salario": 9500000, "compania": companias[1]},
            {"nombre": "Juan", "apellido": "Hernández", "correo": "juan.hernandez@innovacion.co",
             "cargo": "Frontend Developer", "salario": 7000000, "compania": companias[1]},
            # SoftDev Solutions
            {"nombre": "Diana", "apellido": "Torres", "correo": "diana.torres@softdev.co",
             "cargo": "QA Lead", "salario": 7800000, "compania": companias[2]},
            {"nombre": "Felipe", "apellido": "Vargas", "correo": "felipe.vargas@softdev.co",
             "cargo": "Backend Developer", "salario": 8200000, "compania": companias[2]},
            {"nombre": "Sofía", "apellido": "Ramírez", "correo": "sofia.ramirez@softdev.co",
             "cargo": "UX Designer", "salario": 6800000, "compania": companias[2]},
        ]

        for data in empleados_data:
            empleado = EmpleadoModel.objects.create(**data)
            logger.info("Seed: Empleado creado — %s %s (ID=%s)",
                        empleado.nombre, empleado.apellido, empleado.pk)
            self.stdout.write(
                f"  [OK] Empleado creado: {empleado.nombre} {empleado.apellido} -> {data['compania'].nombre}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n[SUCCESS] Seed completado: {len(companias)} companias y {len(empleados_data)} empleados"
            )
        )
        logger.info("=== Seed completado exitosamente ===")

        # ============================================================
        # Crear usuario ADMIN inicial (obligatorio según guía)
        # ============================================================
        from django.contrib.auth.hashers import make_password

        # Admin tradicional (Medellín) para compatibilidad de tests
        admin_correo = "admin@sena.edu.co"
        if not UsuarioModel.objects.filter(correo=admin_correo).exists():
            UsuarioModel.objects.create(
                correo=admin_correo,
                password_hash=make_password("Admin123!"),
                rol="ADMIN",
                ciudad="Medellín",
                compania=None,
            )
            self.stdout.write(self.style.SUCCESS(f"  [OK] Usuario ADMIN creado: {admin_correo}"))
            logger.info("Seed: Usuario ADMIN creado — %s", admin_correo)
        else:
            self.stdout.write(self.style.WARNING(f"  [SKIP] Usuario ADMIN ya existe: {admin_correo}"))

        # Admin Medellín explícito
        admin_med_correo = "admin_medellin@sena.edu.co"
        if not UsuarioModel.objects.filter(correo=admin_med_correo).exists():
            UsuarioModel.objects.create(
                correo=admin_med_correo,
                password_hash=make_password("Admin123!"),
                rol="ADMIN",
                ciudad="Medellín",
                compania=None,
            )
            self.stdout.write(self.style.SUCCESS(f"  [OK] Usuario ADMIN Medellín creado: {admin_med_correo}"))
            logger.info("Seed: Usuario ADMIN Medellín creado — %s", admin_med_correo)

        # Admin Bogotá explícito
        admin_bog_correo = "admin_bogota@sena.edu.co"
        if not UsuarioModel.objects.filter(correo=admin_bog_correo).exists():
            UsuarioModel.objects.create(
                correo=admin_bog_correo,
                password_hash=make_password("Admin123!"),
                rol="ADMIN",
                ciudad="Bogotá",
                compania=None,
            )
            self.stdout.write(self.style.SUCCESS(f"  [OK] Usuario ADMIN Bogotá creado: {admin_bog_correo}"))
            logger.info("Seed: Usuario ADMIN Bogotá creado — %s", admin_bog_correo)

        # Crear usuario USUARIO (asociado a TechCorp)
        usuario_correo = "usuario@techcorp.co"
        if not UsuarioModel.objects.filter(correo=usuario_correo).exists():
            UsuarioModel.objects.create(
                correo=usuario_correo,
                password_hash=make_password("Usuario123!"),
                rol="USUARIO",
                ciudad="Medellín",
                compania=companias[0],
            )
            self.stdout.write(self.style.SUCCESS(f"  [OK] Usuario USUARIO creado: {usuario_correo}"))
            logger.info("Seed: Usuario USUARIO creado — %s", usuario_correo)

