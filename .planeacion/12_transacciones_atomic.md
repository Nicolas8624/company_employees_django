# Transacciones

Se debe usar:

from django.db import transaction

Ejemplo conceptual:

with transaction.atomic():
    crear_compania()
    crear_empleados()

Si falla un empleado:
- rollback total
- no se guarda nadav