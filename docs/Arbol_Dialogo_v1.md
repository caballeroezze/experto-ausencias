# 🧭 Árbol de Decisiones / Diálogo — Sistema Experto de Ausencias

## 0) Principios

* **Legajo único** para identificar persona (no se pide DNI).
* **Lista cerrada** de motivos.
* **Slot-filling por metas**: el bot pregunta **solo lo faltante**.
* **Mensajes mínimos** (privacidad): no exponer más datos que los necesarios.
* **Explicación**: toda conclusión debe registrar **regla\_id + porqué + hechos**.

---

## 1) Intents (metas)

* **crear\_aviso**
* **adjuntar\_certificado**
* **consultar\_estado**
* **modificar\_aviso** / **cancelar\_aviso**
* **ayuda** / **menú**

Palabras disparadoras (ejemplos):

* crear\_aviso: “avisar”, “faltar”, “licencia”, “enfermedad”, “tengo fiebre”, “permiso”.
* adjuntar\_certificado: “adjunto”, “certificado”, “mando el acta”.
* consultar\_estado: “estado”, “cómo va”, “mi aviso”.
* modificar/cancelar: “cambiar fecha”, “extender”, “cancelar”.

---

## 2) Slots compartidos (por nombre exacto)

* `legajo` (obligatorio al inicio)
* `motivo` (lista cerrada)
* `fecha_inicio`
* `duracion_estimdays`
* `adjunto_certificado` (obligatorio según `motivo`)
* Derivados: `fecha_fin_estimada`, `documento_tipo`, `estado_aviso`, `estado_certificado`, `fuera_de_termino`, `id_aviso`, `notificar_a`.

---

## 3) Flujo: **CREAR AVISO**

### 3.1 Precondiciones

* Tener `legajo`. Si no viene, pedirlo primero.

### 3.2 Pasos

1. **Legajo**

   * Pregunta: “Decime tu **legajo** (solo números/letras).”
   * Validación: existe en BD → OK; si no existe → `estado_aviso = pendiente_validacion`, continuar y **notificar RRHH** (sin frenar flujo).
   * Confirmación mínima: “Hola **{empleado\_nombre}** (legajo **{legajo}**).”

2. **Motivo**

   * Pregunta: “Elegí el **motivo**: `art`, `enfermedad_inculpable`, `enfermedad_familiar`, `fallecimiento`, `matrimonio`, `nacimiento`, `paternidad`, `permiso_gremial`.”
   * Si valor ambiguo → ofrecer lista interactiva.
   * Al confirmar, derivar `documento_tipo` requerido (si aplica).

3. **Fecha de inicio**

   * Pregunta: “¿Fecha de **inicio**? (ej. `2025-08-17`, `hoy`, `mañana`).”
   * Normalización a ISO.

4. **Duración estimada (días)**

   * Pregunta: “¿Cuántos **días** estimás?” (entero ≥ 0).
   * Derivar `fecha_fin_estimada`.

5. **Requisitos documentales**

   * Si el motivo **requiere** documento:

     * Mensaje: “Para **{motivo}** se requiere **{documento\_tipo}**. Podés **adjuntarlo ahora** o dentro de **{plazo\_cert\_horas}h**.”
     * Si **adjunta ahora**: `estado_certificado = recibido` → validar legibilidad; si OK → `validado`, si no → `pendiente_revision`.
     * Si **no adjunta**: `estado_certificado = pendiente` y marcar **plazo**.

6. **Duplicados / Solapamiento**

   * Verificar si hay aviso abierto que se solapa (mismo legajo, rango de fechas).
   * Si sí → `estado_aviso = rechazado` + notificar RRHH + explicar regla.

7. **Ruteo de notificaciones**

   * Base: RRHH.
   * Enfermedad/ART: + médico\_laboral (si política)
   * Permiso\_gremial: + delegado\_gremial
   * Producción y ausencia > 2 días: + jefe\_produccion

8. **Confirmación final**

   * Resumen corto (sin PII): motivo, fecha, duración, requisitos/doc, estado.
   * “¿Confirmás el aviso?”
   * Al confirmar → asignar **`id_aviso`**, persistir, enviar notificaciones.

### 3.3 Mensajes tipo (plantillas)

* **Resumen**:
  “**ID:** {id\_aviso} · **Motivo:** {motivo} · **Inicio:** {fecha\_inicio} · **Días:** {duracion\_estimdays} · **Estado:** {estado\_aviso} {flag\_fuera\_termino?}”
* **Incompleto**:
  “Tu aviso quedó **incompleto**: falta **{campo/doc}**. Tenés **{plazo\_cert\_horas}h** para adjuntarlo.”
* **Pendiente\_validacion** (legajo desconocido):
  “Registré el aviso como **pendiente de validación** y avisé a RRHH.”
* **Rechazado duplicado**:
  “No pude crear el aviso: ya existe uno **solapado**. RRHH fue notificado.”

---

## 4) Flujo: **ADJUNTAR CERTIFICADO / DOCUMENTO**

### 4.1 Precondiciones

* Identificar el aviso: por `id_aviso` o por `legajo + fecha_inicio`.

### 4.2 Pasos

1. **Identificación de aviso**

   * Pregunta: “Decime el **ID de aviso** (o tu `legajo` y fecha de inicio).”
2. **Adjunto**

   * Aceptar pdf/jpg/png.
   * Chequear `documento_tipo` esperado según `motivo`.
   * `documento_legible` (input del usuario o validación básica): si no legible → `estado_certificado = pendiente_revision`.
3. **Plazo**

   * Comparar `fecha_recepcion` vs `fecha_inicio`.
   * Si excede `plazo_cert_horas` → `fuera_de_termino = true` + notificar RRHH.
4. **Actualizar estados**

   * Si doc correcto y legible → `estado_certificado = validado`.
   * Si todo completo → `estado_aviso = completo`.

### 4.3 Mensajes tipo

* “Documento **recibido** para {id\_aviso}. Estado del certificado: **{estado\_certificado}**.”
* “El documento llegó **fuera de término**; RRHH fue notificado.”

---

## 5) Flujo: **CONSULTAR ESTADO**

### 5.1 Entrada

* `id_aviso` **o** `legajo` (si hay varios, listar últimos 3 con paginación).

### 5.2 Salida

* `estado_aviso`, `estado_certificado`, `requisitos_pendientes`, `plazo_restante_horas` (si aplica), `notificar_a` realizado (último envío).
* Explicación breve (regla principal disparada).

### 5.3 Mensajes tipo

* “**{id\_aviso}** → **{estado\_aviso}** · Certificado: **{estado\_certificado}** {fuera\_de\_termino?}. {pendientes?}. **Acción sugerida:** {siguiente\_paso}.”

---

## 6) Flujo: **MODIFICAR / CANCELAR AVISO**

### 6.1 Identificación

* Pedir `id_aviso` o `legajo + fecha_inicio`.

### 6.2 Modificar

* Campos permitidos: `duracion_estimdays` (extensión), **antes** de `fecha_fin_estimada`.
* Cambios en `motivo` → **crear nuevo aviso** (y cerrar el anterior) salvo política contraria.

### 6.3 Cancelar

* Confirmación doble: “¿Querés **cancelar** el aviso {id\_aviso}? Escribe **CONFIRMAR**.”
* Estado final: `rechazado` (por cancelación), notificar RRHH; si había notificaciones previas, enviar actualización.

---

## 7) Reglas de validación en diálogo (resumen)

* `legajo` inexistente → continuar como `pendiente_validacion` + avisar RRHH.
* `motivo` fuera de lista → ofrecer opciones.
* `fecha_inicio` parsear “hoy/mañana/ayer” y `DD/MM/AAAA`.
* `duracion_estimdays` entero ≥ 0; si “no sé” → pedir mínimo 1 y marcar editable.
* Duplicados/solapamiento → rechazar y explicar.
* Documentos: tipo correcto según motivo; ilegible → `pendiente_revision`.
* Plazo 24/48h → marcar `fuera_de_termino` si excede.

---

## 8) Ramas especiales (edge cases)

* **Enfermedad\_familiar** sin `vinculo_familiar` → pedir `vinculo_familiar`.
* **Permiso\_gremial** sin anticipo ≥ 48h → marcar incumplimiento (incompleto) y notificar RRHH/delegado.
* **Producción** y `duracion_estimdays > 2` → notificar `jefe_produccion`.
* **ART**: sin doc inicial; habilitar notificación a médico laboral.

---

## 9) Menú / Ayuda

* “Puedo: **crear aviso**, **adjuntar certificado**, **consultar estado**, **modificar**, **cancelar**. Decime una opción o escribí ‘menú’.”

---

## 10) Cierre de cada interacción

* Siempre devolver **resumen corto** y **próximo paso** (si falta algo).
* Guardar **traza**: `regla_id`, hechos, conclusión, timestamp.

---

## 11) Criterios de aceptación (para pruebas)

* Cada meta funciona con **slot-filling** y mensajes claros.
* `id_aviso` se genera solo tras confirmación.
* Estados y notificaciones siguen las reglas de negocio.
* Casos borde cubiertos (legajo no existe, fuera de término, duplicado, ilegible).
