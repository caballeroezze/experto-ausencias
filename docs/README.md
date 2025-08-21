# 1) Arquitectura (todo Python)

**Capas**

1. **Motor experto** (reglas + inferencia + explicación).
2. **Gestor de diálogo** (slot-filling según el Árbol de Decisiones).
3. **Adaptador Telegram** (aiogram 3.x).
4. **Persistencia** (SQLAlchemy + SQLite/Postgres).
5. **Notificaciones** (email/Telegram interno como necesites).
6. **Validación/normalización** (fechas, sinónimos, legibilidad de adjuntos).
7. **Telemetría** (logs + trazas por `regla_id`).
8. **CLI** y **tests** (pytest) + **semillas** (empleados dummy).

---

# 2) Estructura del repo

```
experto-ausencias/
├─ docs/                         # (ya los tenemos)
├─ src/
│  ├─ app.py                     # entrypoint (polling)
│  ├─ config.py                  # .env, constantes, policies
│  ├─ engine/                    # motor experto
│  │  ├─ __init__.py
│  │  ├─ kb_loader.py            # carga rules.json / glossary.json
│  │  ├─ inference.py            # forward/backward, explicación
│  │  └─ explain.py              # formato de trazas
│  ├─ dialogue/
│  │  ├─ __init__.py
│  │  ├─ manager.py              # slot-filling por metas
│  │  └─ prompts.py              # plantillas de mensajes
│  ├─ telegram/
│  │  ├─ __init__.py
│  │  └─ bot.py                  # aiogram handlers
│  ├─ persistence/
│  │  ├─ __init__.py
│  │  ├─ models.py               # SQLAlchemy
│  │  ├─ dao.py                  # repositorios/queries
│  │  └─ seed.py                 # empleados demo
│  ├─ notify/
│  │  ├─ __init__.py
│  │  └─ router.py               # RRHH, médico, etc.
│  ├─ utils/
│  │  ├─ normalize.py            # sinónimos/fechas/números
│  │  └─ files.py                # validaciones de adjuntos
│  └─ knowledge/
│     ├─ rules.json              # 25–40 reglas
│     └─ glossary.json           # dominios/sinónimos/policies
├─ tests/
│  ├─ test_engine.py
│  ├─ test_dialogue.py
│  ├─ test_persistence.py
│  └─ cases/                     # P-01..P-20 en JSON/CSV
├─ .env.example
├─ requirements.txt
├─ pyproject.toml / setup.cfg    # formato/lint/pytest
├─ Dockerfile
└─ README.md
```

**Librerías sugeridas**

* `aiogram==3.*`, `SQLAlchemy==2.*`, `pydantic==2.*`, `python-dotenv`, `python-dateutil`, `rapidfuzz`, `alembic` (si usás migraciones), `pytest`.

---

# 3) Contratos internos (sin código)

## 3.1 Motor (I/O interno)

* **Entrada**: `facts: dict` (legajo, motivo, fecha\_inicio, duracion\_estimdays, …) + `policies` (plazo, ruteo) + `session_id`.
* **Salida**:

  * `status`: `need_info | concluded | rejected`
  * `ask`: lista de slots faltantes (si aplica)
  * `id_aviso?`, `estado_aviso`, `estado_certificado`, `flags`
  * `acciones`: `["persistir","notificar_rrhh",...]`
  * `notificar_a`: `[rrhh, medico_laboral, ...]`
  * `explicacion`: \[{regla\_id, porque, hechos}]
  * `resumen`: string corto

## 3.2 Diálogo

* **Entrada**: texto/archivo → `normalize` → `facts_delta`
* **Salida**: siguiente **pregunta** (si `need_info`) o **resumen/confirmación**.

## 3.3 Persistencia

* Modelos: Empleado, Aviso, Certificado, Notificación, Auditoría.
* Reglas: unicidad `id_aviso`; no solape (legajo, rango fechas).
* Funciones: `create_aviso()`, `update_certificado()`, `find_solape()`, `historial_empleado()`.

## 3.4 Telegram

* Handlers: `/start`, `/help`, texto, documento/imagen.
* Mapea cada mensaje a: **update facts → infer → responder / pedir slot**.

---

# 4) Prompts para Cursor (ensamblado total en Python)

> **Modelos**:
>
> * **Razonador** = *GPT-5 Thinking* (arquitectura/lógica).
> * **Rápido** = modelo económico (boilerplate, plantillas).

### Paso A — Crear scaffold y dependencias (Razonador)

```
Objetivo: generar el scaffold Python del proyecto “experto-ausencias” según esta estructura (copiar la estructura exacta indicada). Crea archivos con encabezados y TODOs; NO incluyas código de negocio todavía.

Incluye:
- requirements.txt con aiogram 3.x, SQLAlchemy 2.x, pydantic 2.x, python-dotenv, rapidfuzz, dateutil, pytest.
- .env.example con TELEGRAM_TOKEN, DATABASE_URL, LOG_LEVEL.
- README: comandos “make run”, “make test” (o instrucciones python -m).
```

### Paso B — Motor experto (interfaces + tests) (Razonador)

```
Implementa en src/engine/:
- kb_loader.py: carga y valida rules.json/glossary.json (schemas).
- inference.py: funciones forward/backward chaining, operadores (==, !=, in, >=, <=), top-3, explicación.
- explain.py: helpers para formar trazas (regla_id, hechos, porque).

Genera tests en tests/test_engine.py que cubran:
- disparo de cada grupo de reglas,
- combinación de certezas,
- backward: “need_info” con slots del Arbol_Dialogo_v1.md,
- casos P-09..P-11 (doc ausente, fuera de término, ilegible).
Usa docs/Reglas_BC_v1.md, Glosario_Ontologia_v1.md y Casos_Prueba_P01-P20.md como fuente de verdad. No inventes reglas ni dominios.
```

### Paso C — Normalización/validación (Razonador)

```
En src/utils/normalize.py, implementa:
- parseo de fechas (“hoy/mañana/ayer”, DD/MM/AAAA → ISO),
- normalización de motivo (sinónimos → dominio fijo),
- extracción de “var: valor” y frases libres (“me caso” → motivo=matrimonio).
Crea tests test_normalize en tests/.
```

### Paso D — Persistencia (Razonador)

```
En src/persistence/:
- models.py (SQLAlchemy): Empleado, Aviso, Certificado, Notificacion, Auditoria.
- dao.py: create_aviso, update_certificado, find_solape, historial_empleado.
- seed.py: carga 10 empleados demo y 2 áreas.

Tests:
- inserción de aviso, certificado; verificación de solape; historial.
No mezclar lógica de reglas aquí.
```

### Paso E — Gestor de diálogo (Razonador)

```
En src/dialogue/manager.py:
- Implementa slot-filling por metas (crear_aviso, adjuntar_certificado, consultar_estado, modificar/cancelar).
- Interfaz: process_message(session_id, text|file) → {reply_text, ask?, facts_delta?, next_action?}
- Usa prompts de docs/Arbol_Dialogo_v1.md (agregar ./dialogue/prompts.py).
Tests: P-16..P-20 (flujos de chat).
```

### Paso F — Adaptador Telegram (Rápido)

```
En src/telegram/bot.py:
- aiogram 3.x: /start, /help, handler de texto y documentos.
- Cada mensaje: llama a dialogue.manager.process_message → responde; maneja adjuntos.
- Logging básico y manejo de errores (mensajes claros).
Entry src/app.py que levante el polling con el token de .env.
```

### Paso G — Notificaciones (Rápido)

```
En src/notify/router.py:
- Función route(notificar_a, payload) que por ahora hace logging/print (hookeable a email/telegram interno).
- Integrar con diálogo después de inferencia concluida.
```

### Paso H — Semillas + script de smoke test (Rápido)

```
- persistence/seed.py crea empleados demo.
- Script cli “python -m src.app” que:
  1) migra/crea tablas,
  2) ejecuta seed,
  3) inicia el bot en polling.
```

### Paso I — Suite P-01..P-20 (Razonador)

```
Genera tests parametrizados desde tests/cases/ con inputs conversacionales y outputs esperados (estado_aviso, estado_certificado, notificar_a). Asegura cobertura de todas las reglas y flujos.
```

### Paso J — Docker + Makefile (Rápido)

```
Dockerfile slim + objetivos make: install, run, test, seed, lint.
```

*(Con esos 10 prompts, Cursor te arma todo el esqueleto y la implementación paso a paso.)*

---

# 5) Configuración y ejecución local

**.env**

* `TELEGRAM_TOKEN=...`
* `DATABASE_URL=sqlite:///./ausencias.db` (o Postgres)
* `LOG_LEVEL=INFO`

**Pasos**

1. Instalar deps.
2. Crear BD y correr `seed`.
3. Levantar `src/app.py` (polling).
4. Probar P-01 nominal en Telegram.
5. Correr `pytest` (engine, dialogue, persistence, P-01..P-20).

---

# 6) Definición de Hecho (para el motor)

* `legajo` (string/int)
* `motivo` (enum cerrado)
* `fecha_inicio` (ISO)
* `duracion_estimdays` (int)
* `adjunto_certificado` (bool/meta)
* Derivados: `fecha_fin_estimada`, `documento_tipo`, `estado_aviso`, `estado_certificado`, `fuera_de_termino`, `id_aviso`, `notificar_a`.

*(Idénticos a tu Glosario/Ontología.)*

---

# 7) Criterios de “listo” (DoD)

* Motor dispara **todas** las reglas de Reglas\_BC\_v1 (≥25).
* Diálogo hace **slot-filling** estrictamente según Árbol.
* P-01..P-20 **verdes**.
* Persistencia registra **id\_aviso** único + historial sin solapes.
* Telegram responde < **5 s** en flujo nominal local.
* Logs guardan trazas por `regla_id`.
