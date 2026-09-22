from gestor import GestorSistema
from excepts import ErrorSistema, ErrorValidacion


def leer_entero(mensaje: str) -> int:
    while True:
        entrada = input(mensaje)
        try:
            return int(entrada)
        except ValueError:
            print("Entrada invalida. Ingrese un numero entero.")

def leer_real(mensaje: str) -> float:
    while True:
        entrada = input(mensaje).replace(",", ".")
        try:
            return float(entrada)
        except ValueError:
            print("Entrada invalida. Ingrese un numero.")

def pausar():
    input("Presione Enter para continuar...")

def linea():
    print("-" * 60)


def menu_agregar_producto(gestor: GestorSistema):
    linea()
    print("=== Agregar Producto ===")
    try:
        descripcion = input("Descripcion: ")
        precio = leer_real("Precio: ")
        stock = leer_entero("Stock: ")
        producto = gestor.agregar_producto(descripcion, precio, stock)
        print(f"Producto agregado correctamente. Codigo asignado: {producto.codigo}")
    except ErrorSistema as e:
        print(f"Error: {e}")
    pausar()


def menu_buscar_producto(gestor: GestorSistema):
    linea()
    print("=== Buscar Producto ===")
    print("1. Buscar por codigo")
    print("2. Buscar por descripcion")
    opcion = leer_entero("Opcion: ")
    try:
        if opcion == 1:
            codigo = leer_entero("Codigo a buscar: ")
            producto = gestor.buscar_producto_por_codigo(codigo)
        elif opcion == 2:
            texto = input("Descripcion a buscar: ")
            producto = gestor.buscar_producto_por_descripcion(texto)
        else:
            print("Opcion invalida.")
            pausar()
            return
        print(producto)
    except ErrorSistema as e:
        print(f"Error: {e}")
    pausar()


def menu_listar_productos(gestor: GestorSistema):
    linea()
    print("=== Inventario ===")
    productos = gestor.listar_productos()
    if not productos:
        print("No hay productos cargados en el inventario.")
    for producto in productos:
        print(producto)
    pausar()


def menu_editar_producto(gestor: GestorSistema):
    linea()
    print("=== Editar Producto ===")
    try:
        codigo = leer_entero("Codigo del producto a editar: ")
        producto = gestor.buscar_producto_por_codigo(codigo)
        print(producto)
        print("1. Descripcion  2. Precio  3. Stock  0. Cancelar")
        op = leer_entero("Que desea editar? ")
        if op == 1:
            gestor.editar_producto(codigo, descripcion=input("Nueva descripcion: "))
        elif op == 2:
            gestor.editar_producto(codigo, precio=leer_real("Nuevo precio: "))
        elif op == 3:
            gestor.editar_producto(codigo, stock=leer_entero("Nuevo stock: "))
        elif op == 0:
            print("Edicion cancelada.")
            pausar()
            return
        else:
            print("Opcion invalida.")
            pausar()
            return
        print("Producto actualizado con exito.")
    except ErrorSistema as e:
        print(f"Error: {e}")
    pausar()


def menu_descontar_stock(gestor: GestorSistema):
    linea()
    print("=== Descontar Stock ===")
    try:
        codigo = leer_entero("Codigo del producto: ")
        cantidad = leer_entero("Cantidad a descontar: ")
        producto = gestor.descontar_stock(codigo, cantidad)
        print(f"Stock actualizado. Nuevo stock de '{producto.descripcion}': {producto.stock}")
    except ErrorSistema as e:
        print(f"Error: {e}")
    pausar()


def menu_agregar_cliente(gestor: GestorSistema):
    linea()
    print("=== Agregar Cliente ===")
    try:
        dni = leer_entero("DNI: ")
        nombre = input("Nombre: ")
        edad = leer_entero("Edad: ")
        email = input("Email: ")
        print("1. Minorista  2. Mayorista")
        tipo = "Mayorista" if leer_entero("Tipo de cliente: ") == 2 else "Minorista"
        cliente = gestor.agregar_cliente(dni, nombre, edad, email, tipo)
        print(f"Cliente registrado: {cliente}")
    except ErrorSistema as e:
        print(f"Error: {e}")
    pausar()


def menu_agregar_trabajador(gestor: GestorSistema):
    linea()
    print("=== Agregar Trabajador ===")
    try:
        dni = leer_entero("DNI: ")
        nombre = input("Nombre: ")
        edad = leer_entero("Edad: ")
        legajo = leer_entero("Legajo: ")
        cargo = input("Cargo: ")
        salario = leer_real("Salario: ")
        trabajador = gestor.agregar_trabajador(dni, nombre, edad, legajo, cargo, salario)
        print(f"Trabajador registrado: {trabajador}")
    except ErrorSistema as e:
        print(f"Error: {e}")
    pausar()


def menu_listar_personas(gestor: GestorSistema):
    linea()
    print("=== Personas registradas ===")
    personas = gestor.listar_clientes() + gestor.listar_trabajadores()
    if not personas:
        print("No hay personas registradas.")
    # Polimorfismo: no importa si es Cliente o Trabajador, a todas se les
    # puede pedir .descripcion() y cada una responde distinto.
    for persona in personas:
        print(persona.descripcion())
    pausar()


def menu_generar_orden(gestor: GestorSistema):
    linea()
    print("=== Generar Orden de Compra ===")
    try:
        dni_cliente = leer_entero("DNI del cliente: ")
        dni_trabajador = leer_entero("DNI del trabajador que atiende: ")
        orden = gestor.crear_orden(dni_cliente, dni_trabajador)

        while True:
            codigo = leer_entero("Codigo de producto a agregar (0 para terminar): ")
            if codigo == 0:
                break
            cantidad = leer_entero("Cantidad: ")
            try:
                gestor.agregar_item_a_orden(orden, codigo, cantidad)
                print("Item agregado a la orden.")
            except ErrorSistema as e:
                print(f"Error: {e}")

        total = gestor.confirmar_orden(orden)
        linea()
        print(f"Orden #{orden.numero} confirmada. Total a pagar: ${total:.2f}")
    except ErrorSistema as e:
        print(f"Error: {e}")
    pausar()


def menu_listar_ordenes(gestor: GestorSistema):
    linea()
    print("=== Ordenes de Compra ===")
    ordenes = gestor.listar_ordenes()
    if not ordenes:
        print("No hay ordenes registradas.")
    for orden in ordenes:
        print(f"Orden #{orden.numero} | {orden.fecha} | Total: ${orden.total:.2f}")
    pausar()


def menu_principal():
    gestor = GestorSistema()
    opcion = -1
    while opcion != 0:
        linea()
        print("-------- Menu de Opciones --------")
        print("1. Agregar Producto")
        print("2. Buscar Producto")
        print("3. Listar Productos")
        print("4. Descontar Stock")
        print("5. Editar Producto")
        print("6. Agregar Cliente")
        print("7. Agregar Trabajador")
        print("8. Listar Personas")
        print("9. Generar Orden de Compra")
        print("10. Listar Ordenes de Compra")
        print("0. Salir")
        opcion = leer_entero("Opcion: ")

        acciones = {
            1: menu_agregar_producto,
            2: menu_buscar_producto,
            3: menu_listar_productos,
            4: menu_descontar_stock,
            5: menu_editar_producto,
            6: menu_agregar_cliente,
            7: menu_agregar_trabajador,
            8: menu_listar_personas,
            9: menu_generar_orden,
            10: menu_listar_ordenes,
        }

        if opcion == 0:
            print("Fin del programa.")
        elif opcion in acciones:
            acciones[opcion](gestor)
        else:
            print("Opcion invalida.")
            pausar()


if __name__ == "__main__":
    menu_principal()