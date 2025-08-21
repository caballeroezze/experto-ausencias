# Reglas_BC_v1

## Identidad
- **R-IDENT-01**: SI `legajo` existe en BD → `estado_aviso = pendiente_completo` (identidad confirmada).
- **R-IDENT-02**: SI `legajo` NO existe → `estado_aviso = pendiente_validacion`, notificar `rrhh`.
- **R-IDENT-03**: SI existe aviso **solapado** (mismo legajo y rango) → `estado_aviso = rechazado`, notificar `rrhh`.

## Motivo y documentación (lista cerrada)
Motivos: `art`, `enfermedad_inculpable`, `enfermedad_familiar`, `fallecimiento`, `matrimonio`, `nacimiento`, `paternidad`, `permiso_gremial`.

- **R-MOTIVO-01**: `enfermedad_inculpable` → doc = `certificado_medico` (obligatorio).
- **R-MOTIVO-02**: `enfermedad_familiar` → doc = `certificado_medico` + `vinculo_familiar` (obligatorio).
- **R-MOTIVO-03**: `art` → sin doc inicial; posible `medico_laboral`.
- **R-MOTIVO-04**: `fallecimiento` → doc = `acta_defuncion`.
- **R-MOTIVO-05**: `matrimonio` → doc = `acta_matrimonio`.
- **R-MOTIVO-06**: `nacimiento` → doc = `acta_nacimiento`.
- **R-MOTIVO-07**: `paternidad` → doc = `acta_nacimiento` (+ filiación implícita).
- **R-MOTIVO-08**: `permiso_gremial` → doc = `nota_gremial` y anticipo ≥ 48h.

## Plazos documento
- **R-CERT-01**: Si motivo requiere doc y NO adjunta → `estado_certificado = pendiente`, `estado_aviso = incompleto`.
- **R-CERT-02**: Doc recibido ≤ `plazo_cert_horas` (24/48) → `estado_certificado = validado`.
- **R-CERT-03**: Doc recibido > `plazo_cert_horas` → `fuera_de_termino = true` + notificar `rrhh`.
- **R-CERT-04**: Doc ilegible → `estado_certificado = pendiente_revision` + notificar `rrhh`.

## Estados y número único
- **R-EST-01**: Al confirmar creación → generar `id_aviso = A-YYYYMMDD-####`.
- **R-EST-02 (COMPLETAR)**: Aviso pasa a **`completo`** SI:
  - no hay duplicado/solape **y**
  - (doc **no requerido**) **o** (doc **requerido** y `estado_certificado in {validado}`).
  En otro caso → `incompleto` o `pendiente_validacion` según corresponda.

## Médico laboral
- **R-MED-01**: `enfermedad_inculpable` → notificar `medico_laboral` (si política).
- **R-MED-02**: `art` → coordinar auditoría médica.

## Notificaciones
- **R-NOTI-01**: Todo aviso → `rrhh`.
- **R-NOTI-02**: Enfermedad / ART → `medico_laboral`.
- **R-NOTI-03**: `permiso_gremial` → `delegado_gremial`.
- **R-NOTI-04**: `area = producción` y `duracion_estimdays > 2` → `jefe_produccion`.
