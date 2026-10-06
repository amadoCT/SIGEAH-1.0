"""
Módulo principal de la aplicación SIGEAH-1.0.
Menú interactivo por consola.
"""

def mostrar_menu():
    print("\n" + "=" * 40)
    print("      SISTEMA SIGEAH-1.0 - MENÚ")
    print("=" * 40)
    print("1. Registrar emergencia")
    print("2. Consultar y filtrar emergencias")
    print("3. Actualizar estado de emergencia")
    print("4. Salir")
    print("=" * 40)

def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-4): ").strip()
        
        if opcion == "1":
            print("\n[Módulo] Registrar emergencia - En construcción")
        elif opcion == "2":
            print("\n[Módulo] Consultar y filtrar - En construcción")
        elif opcion == "3":
            print("\n[Módulo] Actualizar estado - En construcción")
        elif opcion == "4":
            print("\n¡Gracias por usar SIGEAH-1.0! Saliendo...")
            break
        else:
            print("\nOpción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()