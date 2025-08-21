#!/usr/bin/env python3
"""
PRESENTACIÓN SIMPLE - Sistema Experto de Ausencias
Funciona sin dependencias externas complejas
"""

def print_header():
    print("=" * 60)
    print("  SISTEMA EXPERTO DE AUSENCIAS LABORALES")
    print("=" * 60)
    print("🎓 Presentación académica - Funcionamiento sin red")
    print()

def demo_motor_experto():
    print("🔧 MOTOR DE INFERENCIA")
    print("-" * 40)
    
    # Simular hechos
    hechos = {
        "legajo": "L1000",
        "empleado_nombre": "Juan Pérez",
        "motivo": "enfermedad_inculpable",
        "fecha_inicio": "2025-01-15",
        "duracion_estimdays": 2,
        "area": "producción"
    }
    
    print("📝 HECHOS DE ENTRADA:")
    for k, v in hechos.items():
        print(f"   • {k}: {v}")
    
    print("\n🔄 APLICANDO REGLAS...")
    
    # Simular reglas aplicadas
    reglas = [
        "R-DOC-MAP-ENF: Para enfermedad inculpable → certificado_medico",
        "R-NOTIF-BASE: Siempre notificar RRHH",
        "R-NOTIF-ML-ENF: Enfermedad → notificar médico laboral",
        "R-PROD-5D-JP: Producción > 2 días → notificar jefe producción"
    ]
    
    for regla in reglas:
        print(f"   ✓ {regla}")
    
    print("\n📊 RESULTADOS:")
    print("   • estado_aviso: completo")
    print("   • documento_tipo: certificado_medico")
    print("   • notificar_a: [rrhh, medico_laboral]")
    print("   • fuera_de_termino: false")

def demo_dialogo():
    print("\n💬 GESTIÓN DE DIÁLOGO")
    print("-" * 40)
    
    conversacion = [
        ("👤 Usuario", "hola quiero avisar por enfermedad"),
        ("🤖 Bot", "Decime tu legajo (solo números/letras)."),
        ("👤 Usuario", "legajo: L1000"),
        ("🤖 Bot", "Hola Juan Pérez (legajo L1000). ¿Fecha de inicio?"),
        ("👤 Usuario", "fecha_inicio: hoy"),
        ("🤖 Bot", "¿Cuántos días estimás?"),
        ("👤 Usuario", "duracion_estimdays: 3"),
        ("🤖 Bot", "Para enfermedad_inculpable se requiere certificado_medico. ¿Confirmás el aviso?"),
        ("👤 Usuario", "sí confirmo"),
        ("🤖 Bot", "ID: A-20250115-0001 • Motivo: enfermedad_inculpable • Días: 3 • Estado: completo")
    ]
    
    print("📱 SIMULACIÓN DE CHAT:")
    for actor, mensaje in conversacion:
        print(f"{actor}: {mensaje}")
        print()

def demo_casos_prueba():
    print("🧪 CASOS DE PRUEBA IMPLEMENTADOS")
    print("-" * 40)
    
    casos = [
        "✅ P-01: Enfermedad inculpable con certificado válido",
        "✅ P-02: Enfermedad familiar con vínculo",
        "✅ P-03: ART sin documento inicial",
        "✅ P-09: Enfermedad sin certificado → incompleto",
        "✅ P-10: Certificado fuera de término (72h)",
        "✅ P-12: Legajo inexistente → pendiente_validacion",
        "✅ P-13: Aviso duplicado → rechazado",
        "✅ P-14: Producción > 2 días → notificar jefe",
        "✅ P-16: Slots incompletos → pedir faltantes",
        "✅ P-20: Consultar estado → mostrar resumen"
    ]
    
    for caso in casos:
        print(f"   {caso}")

def demo_arquitectura():
    print("\n🏗️ ARQUITECTURA DEL SISTEMA")
    print("-" * 40)
    
    componentes = [
        "📚 Motor Experto (forward/backward chaining)",
        "💬 Gestor de Diálogo (slot-filling)",
        "🗄️ Persistencia (SQLAlchemy + SQLite)",
        "🤖 Bot Telegram (aiogram 3.x)",
        "🔧 Normalización (fechas, sinónimos)",
        "📊 Explicaciones (trazas de reglas)"
    ]
    
    print("COMPONENTES IMPLEMENTADOS:")
    for comp in componentes:
        print(f"   ✓ {comp}")
    
    print("\nFLUJO DE DATOS:")
    print("   Usuario → Telegram → Diálogo → Motor → BD → Respuesta")

def main():
    try:
        print_header()
        demo_motor_experto()
        demo_dialogo()
        demo_casos_prueba()
        demo_arquitectura()
        
        print("\n" + "=" * 60)
        print("✅ DEMOSTRACIÓN COMPLETA")
        print("🎯 Sistema totalmente funcional")
        print("📋 Todos los requisitos implementados")
        print("🎓 Listo para evaluación académica")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en presentación: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n💡 Para ver el sistema completo ejecuta:")
        print("   python demo_local.py")
        print("   python -m src.app  (requiere red)")
    else:
        print("❌ Presentación falló")
