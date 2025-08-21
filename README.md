# Sistema Experto Ausencias

Proyecto generado con el template `cookiecutter-experto-ausencias`.

## Requisitos
- Python 3.10+
- Sin Docker

## Configuración rápida (local)

1. Crear entorno virtual:
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\\Scripts\\Activate.ps1
     ```
   - Linux/macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Variables de entorno:
   - Copia `.env.example` (o `env.example`) a `.env` y ajusta valores según corresponda.
   - Valores por defecto:
     - `TELEGRAM_TOKEN=` (si usas bot de Telegram)
     - `DATABASE_URL=sqlite:///./ausencias.db`
     - `LOG_LEVEL=INFO`

4. Inicializar base y datos demo:
   ```bash
   python -m src.persistence.seed
   ```

5. Ejecutar aplicación (bot de Telegram):
   ```bash
   python -m src.app
   ```

6. Ejecutar tests:
   ```bash
   pytest
   ```

## Notas
- El proyecto incluye stubs/TO-DOs para la lógica de negocio en `src/`. Implementa gradualmente los módulos.
- Telegram (y) y Power BI (y) son opcionales.
- DB engine: sqlite (ajustable via `.env`).
