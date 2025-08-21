# 🧪 Casos de Prueba — Sistema Experto de Ausencias

---

## ⚡ Nominales (uno por cada motivo)

**P-01 — Enfermedad inculpable con certificado válido**

* Entrada: legajo válido, motivo = `enfermedad_inculpable`, fecha\_inicio = hoy, duración = 2 días, adjunto certificado válido dentro de plazo.
* Resultado: `estado_aviso = completo`, `estado_certificado = validado`.
* Notificaciones: RRHH + médico laboral.

**P-02 — Enfermedad familiar con certificado y vínculo**

* Entrada: legajo válido, motivo = `enfermedad_familiar`, certificado médico válido, vínculo = madre.
* Resultado: `estado_aviso = completo`.
* Notificaciones: RRHH.

**P-03 — ART (sin doc inicial)**

* Entrada: legajo válido, motivo = `art`, sin adjunto inicial.
* Resultado: `estado_aviso = incompleto`, `estado_certificado = no_requerido`.
* Notificaciones: RRHH + médico laboral.

**P-04 — Fallecimiento con acta defunción**

* Entrada: legajo válido, motivo = `fallecimiento`, acta defunción legible.
* Resultado: `estado_aviso = completo`.
* Notificaciones: RRHH + supervisor.

**P-05 — Matrimonio con acta matrimonio**

* Entrada: legajo válido, motivo = `matrimonio`, acta matrimonio válida.
* Resultado: `estado_aviso = completo`.
* Notificaciones: RRHH.

**P-06 — Nacimiento con acta nacimiento**

* Entrada: legajo válido, motivo = `nacimiento`, acta nacimiento válida.
* Resultado: `estado_aviso = completo`.
* Notificaciones: RRHH.

**P-07 — Paternidad con acta nacimiento**

* Entrada: legajo válido, motivo = `paternidad`, acta nacimiento válida.
* Resultado: `estado_aviso = completo`.
* Notificaciones: RRHH.

**P-08 — Permiso gremial con nota anticipada ≥ 48h**

* Entrada: legajo válido, motivo = `permiso_gremial`, nota gremial con firma y 72h de anticipo.
* Resultado: `estado_aviso = completo`.
* Notificaciones: RRHH + delegado gremial.

---

## 🛑 Casos Borde — Documentación y Plazos

**P-09 — Enfermedad sin certificado**

* Entrada: legajo válido, motivo = `enfermedad_inculpable`, sin adjunto.
* Resultado: `estado_aviso = incompleto`, `estado_certificado = pendiente`.
* Notificaciones: RRHH.

**P-10 — Enfermedad con certificado fuera de plazo (72h)**

* Entrada: fecha\_inicio = lunes, certificado recibido viernes.
* Resultado: `fuera_de_termino = true`, `estado_certificado = validado`.
* Notificaciones: RRHH.

**P-11 — Documento ilegible**

* Entrada: enfermedad con certificado jpg ilegible.
* Resultado: `estado_certificado = pendiente_revision`.
* Notificaciones: RRHH.

---

## 🔒 Casos de Identidad y Duplicados

**P-12 — Legajo inexistente**

* Entrada: legajo = “9999” (no existe en BD).
* Resultado: `estado_aviso = pendiente_validacion`.
* Notificaciones: RRHH.

**P-13 — Aviso duplicado (solapado)**

* Entrada: empleado ya tiene aviso abierto del mismo período.
* Resultado: `estado_aviso = rechazado`.
* Notificaciones: RRHH.

---

## 🏭 Casos de Producción y Ruteo

**P-14 — Producción con ausencia > 2 días**

* Entrada: legajo de área producción, duración 5 días, motivo enfermedad.
* Resultado: `estado_aviso = completo`.
* Notificaciones: RRHH + jefe\_produccion (+ médico laboral).

**P-15 — Producción ausencia corta (1 día)**

* Entrada: legajo producción, duración 1 día.
* Resultado: `estado_aviso = completo`.
* Notificaciones: solo RRHH (+ médico laboral si enfermedad).

---

## 🔄 Casos de Flujo de Chat

**P-16 — Crear aviso con slots incompletos**

* Entrada: legajo y motivo, pero sin fecha ni duración.
* Resultado: bot pregunta lo faltante → al completar, genera aviso.

**P-17 — Adjuntar certificado luego**

* Entrada: aviso creado incompleto, certificado adjunto dentro de plazo.
* Resultado: `estado_aviso` pasa de `incompleto` a `completo`.

**P-18 — Cancelar aviso**

* Entrada: usuario pide cancelar un aviso activo.
* Resultado: `estado_aviso = rechazado` (cancelado), notificación RRHH.

**P-19 — Extender aviso**

* Entrada: modificar duración de 2 a 5 días (antes de fin estimado).
* Resultado: `duracion_estimdays = 5`, `fecha_fin_estimada` recalculada.

**P-20 — Consultar estado**

* Entrada: legajo válido con aviso activo.
* Resultado: bot devuelve resumen con `estado_aviso`, `estado_certificado`, pendientes y notificaciones hechas.

---

## 📌 Cobertura asegurada

* Todos los **motivos** (8).
* Estados (`pendiente_validacion`, `incompleto`, `completo`, `rechazado`).
* Certificados (`validado`, `pendiente`, `fuera_de_termino`, `pendiente_revision`).
* Ruteo (RRHH, supervisor, médico laboral, delegado, jefe\_produccion).
* Flujos (crear, adjuntar, consultar, modificar, cancelar).
* Casos límite (legajo inexistente, duplicado, ilegible, fuera de término).
