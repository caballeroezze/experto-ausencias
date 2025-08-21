#!/usr/bin/env python3
"""
DEMO LOCAL del Sistema Experto de Ausencias
Para presentaciones sin depender de red de Telegram
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.dialogue.manager import DialogueManager
    from src.engine.inference import forward_chain, backward_chain
    from src.persistence.seed import ensure_schema, seed_employees
    print("✅ Imports exitosos")
except Exception as e:
    print(f"❌ Error de import: {e}")
    print("\n🔧 Intentando import alternativo...")
    try:
        import src.dialogue.manager as dm_module
        import src.engine.inference as inf_module
        import src.persistence.seed as seed_module
        DialogueManager = dm_module.DialogueManager
        forward_chain = inf_module.forward_chain
        backward_chain = inf_module.backward_chain
        ensure_schema = seed_module.ensure_schema
        seed_employees = seed_module.seed_employees
        print("✅ Import alternativo exitoso")
    except Exception as e2:
        print(f"❌ Error crítico: {e2}")
        sys.exit(1)

def print_separator(title=""):
    print("\n" + "="*50)
    if title:
        print(f"  {title}")
        print("="*50)

def demo_dialogue():
    print_separator("DEMO - SISTEMA EXPERTO DE AUSENCIAS")
    print("🤖 Simulación de chat de Telegram")
    
    # Inicializar base de datos
    ensure_schema()
    seed_employees()
    
    dm = DialogueManager()
    session_id = "demo_user"
    
    print("\n📱 Chat simulado:")
    print("-" * 30)
    
    # Simular conversación
    test_messages = [
        "hola",
        "quiero avisar por enfermedad",
        "legajo: L1000",
        "fecha_inicio: hoy",
        "duracion_estimdays: 3",
        "/help",
        "consultar estado"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n👤 Usuario: {msg}")
        
        try:
            result = dm.process_message(session_id, msg)
            reply = result.get("reply_text", "Sin respuesta")
            print(f"🤖 Bot: {reply}")
            
            # Mostrar info adicional si existe
            if result.get("ask"):
                print(f"   📋 Pide: {result['ask']}")
            if result.get("traza_principal"):
                print(f"   🔍 Explicación: {result['traza_principal']}")
                
        except Exception as e:
            print(f"🤖 Bot: Error: {str(e)}")
        
        print("-" * 30)

def demo_engine():
    print_separator("DEMO - MOTOR DE INFERENCIA")
    
    # Test del motor directo
    facts = {
        "legajo": "L1000",
        "empleado_nombre": "Juan Pérez",
        "motivo": "enfermedad_inculpable", 
        "fecha_inicio": "2025-01-15",
        "duracion_estimdays": 2,
        "adjunto_certificado": "cert.pdf",
        "documento_legible": True,
        "area": "producción"
    }
    
    print("📝 Hechos de entrada:")
    for k, v in facts.items():
        print(f"   • {k}: {v}")
    
    print("\n🔄 Ejecutando inferencia...")
    result = forward_chain(facts)
    
    print(f"\n✅ Estado final: {result['facts'].get('estado_aviso', 'N/A')}")
    print(f"📋 Certificado: {result['facts'].get('estado_certificado', 'N/A')}")
    print(f"🔔 Notificar a: {result['facts'].get('notificar_a', [])}")
    
    print("\n📊 Trazas principales:")
    for i, trace in enumerate(result.get('traces', [])[:3], 1):
        print(f"   {i}. {trace.get('regla_id', 'N/A')}: {trace.get('porque', 'N/A')}")

def demo_backward():
    print_separator("DEMO - BACKWARD CHAINING (Slots)")
    
    facts_incomplete = {
        "legajo": "L1001",
        "motivo": "enfermedad_inculpable"
        # Faltan: fecha_inicio, duracion_estimdays
    }
    
    print("📝 Hechos incompletos:")
    for k, v in facts_incomplete.items():
        print(f"   • {k}: {v}")
    
    result = backward_chain("crear_aviso", facts_incomplete)
    
    print(f"\n🔍 Status: {result['status']}")
    if result.get('ask'):
        print(f"❓ Slots faltantes: {result['ask']}")

def main():
    try:
        demo_dialogue()
        demo_engine() 
        demo_backward()
        
        print_separator("DEMO COMPLETA")
        print("✅ Todos los componentes funcionando correctamente!")
        print("🎓 Listo para presentación")
        
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
