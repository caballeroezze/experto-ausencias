# 📘 Glosario de Variables (formato limpio)

### legajo

* **Descripción**: Identificador único de empleado.
* **Tipo**: string/int, regex `^[0-9A-Za-z_-]{1,20}$`.
* **Obligatorio**: ✅
* **Validación**: debe existir en la BD de empleados.
* **Ejemplo de entrada**: “1234” → `1234`.
* **Sinónimos / normalización**: n/a.

---

### empleado\_nombre

* **Descripción**: Nombre legible del empleado (solo lectura).
* **Tipo**: string libre.
* **Obligatorio**: — (se deriva).
* **Validación**: se obtiene de la BD al confirmar legajo.
* **Ejemplo**: “Juan Pérez”.
* **Sinónimos / normalización**: n/a.

---

### area

* **Descripción**: Área o sector del empleado.
* **Tipo**: string.
* **Obligatorio**: — (se deriva de la BD).
* **Dominio**: catálogo interno (ej. `producción`, `administración`, `logística`).
* **Ejemplo**: “Prod.” → `producción`.
* **Sinónimos / normalización**: “planta” → `producción`.

---

### motivo

* **Descripción**: Tipo de ausencia laboral.
* **Tipo**: enum.
* **Obligatorio**: ✅
* **Valores válidos**:

  * `art`
  * `enfermedad_inculpable`
  * `enfermedad_familiar`
  * `fallecimiento`
  * `matrimonio`
  * `nacimiento`
  * `paternidad`
  * `permiso_gremial`
* **Ejemplo**: “enfermedad” → `enfermedad_inculpable`.
* **Sinónimos**: “enf”, “licencia médica” → `enfermedad_inculpable`.

---

### fecha\_inicio

* **Descripción**: Inicio de la ausencia.
* **Tipo**: date, ISO `YYYY-MM-DD`.
* **Obligatorio**: ✅
* **Ejemplo**: “hoy” → `2025-08-17`.
* **Normalización**: palabras clave (`hoy`, `mañana`, `ayer`) y formatos `DD/MM/AAAA`.

---

### duracion\_estimdays

* **Descripción**: Días estimados de ausencia.
* **Tipo**: int ≥ 0.
* **Obligatorio**: ✅
* **Ejemplo**: “3 días” → `3`.
* **Sinónimos / normalización**: “tres”, “x3d” → `3`.

---

### fecha\_fin\_estimada

* **Descripción**: Fecha de fin estimada.
* **Tipo**: date (ISO).
* **Obligatorio**: — (se deriva).
* **Cálculo**: `fecha_inicio + duracion_estimdays`.

---

### adjunto\_certificado

* **Descripción**: Archivo de respaldo obligatorio según motivo.
* **Tipo**: file/meta.
* **Obligatorio**: ⚠️ depende del motivo.
* **Formatos válidos**: pdf, jpg, png.
* **Ejemplo**: “certificado.pdf” → adjunto OK.

---

### estado\_aviso

* **Descripción**: Estado global del aviso.
* **Tipo**: enum.
* **Valores válidos**:

  * `pendiente_validacion`
  * `incompleto`
  * `completo`
  * `rechazado`

---

### estado\_certificado

* **Descripción**: Estado del certificado/documento.
* **Tipo**: enum.
* **Valores válidos**:

  * `no_requerido`
  * `pendiente`
  * `recibido`
  * `validado`
  * `pendiente_revision`
  * `rechazado`

---

### fuera\_de\_termino

* **Descripción**: Si el certificado llegó después del plazo (24/48h).
* **Tipo**: boolean.
* **Valores**: true / false.

---

### id\_aviso

* **Descripción**: Número único de aviso.
* **Tipo**: string.
* **Formato**: `A-YYYYMMDD-####`.
* **Obligatorio**: — (se genera automáticamente).

---

### vinculo\_familiar

* **Descripción**: Parentesco en caso de enfermedad familiar.
* **Tipo**: enum.
* **Obligatorio**: ⚠️ solo si motivo = `enfermedad_familiar`.
* **Valores válidos**: `padre`, `madre`, `hijo/a`, `cónyuge`, `otro`.
* **Ejemplo**: “mi mamá” → `madre`.

---

### documento\_tipo

* **Descripción**: Tipo de documento esperado según motivo.
* **Tipo**: enum.
* **Valores**:

  * `certificado_medico`
  * `acta_defuncion`
  * `acta_matrimonio`
  * `acta_nacimiento`
  * `nota_gremial`

---

### documento\_legible

* **Descripción**: Si el documento adjunto es legible.
* **Tipo**: boolean.
* **Valores**: true / false.

---

### medico\_laboral\_interv

* **Descripción**: Indica si debe intervenir el médico laboral.
* **Tipo**: boolean.
* **Valores**: true / false.

---

### notificar\_a

* **Descripción**: Lista de destinos para notificación.
* **Tipo**: list.
* **Valores válidos**: `rrhh`, `supervisor`, `jefe_produccion`, `medico_laboral`, `delegado_gremial`.
* **Obligatorio**: — (se deriva por reglas de negocio).
