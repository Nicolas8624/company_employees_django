# Parte II - Guia para Antigravity

Esta carpeta contiene el contexto y las instrucciones para que una IA como Antigravity continue el proyecto anterior de Django sin romper la arquitectura Onion.

Proyecto base revisado:

- API REST de companias y empleados.
- Stack: Python, Django, Django REST Framework, SQLite.
- Arquitectura actual: `domain`, `application`, `infrastructure`, `api`.
- Patrones usados: Repository Pattern y Unit of Work.
- Flujo obligatorio existente:

```text
Controller -> Service -> UnitOfWork -> Repository -> Django ORM -> Database
```

La Parte II NO debe crear un proyecto desde cero. Debe ampliar el proyecto anterior.

Archivos recomendados para usar en Antigravity:

1. `01_PROMPT_MAESTRO_ANTIGRAVITY.md`
2. `02_REQUISITOS_PARTE_II.md`
3. `03_PLAN_IMPLEMENTACION_DJANGO.md`
4. `04_ARQUITECTURA_OBJETIVO.md`
5. `05_PROMPTS_OBLIGATORIOS_IA.md`
6. `06_CHECKLIST_ENTREGA.md`
7. `07_README_PARTE_II_PLANTILLA.md`
8. `08_PREGUNTAS_SUSTENTACION.md`

Forma sugerida de uso:

1. Abre el proyecto Django anterior en Antigravity.
2. Adjunta o pega primero `01_PROMPT_MAESTRO_ANTIGRAVITY.md`.
3. Luego adjunta `02_REQUISITOS_PARTE_II.md` y `03_PLAN_IMPLEMENTACION_DJANGO.md`.
4. Pide a Antigravity que implemente modulo por modulo, verificando pruebas al final de cada modulo.

Importante:

- No permitir que los controllers accedan directamente al ORM.
- No permitir que los repositorios hagan commit por su cuenta.
- No guardar contrasenas en texto plano.
- No escribir la clave JWT directamente en el codigo.
- Mantener las validaciones y reglas de negocio fuera del controller.
