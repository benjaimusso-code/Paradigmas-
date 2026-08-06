import PySimpleGUI as sg

from gestor import GestorSistema
from excepts import ErrorSistema

sg.theme("SystemDefaultForReal")


# ----------------------------------------------------------------------
# Helpers de tablas
# ----------------------------------------------------------------------

def filas_productos(gestor: GestorSistema):
    return [[p.codigo, p.descripcion, f"${p.precio:.2f}", p.stock]
            for p in gestor.listar_productos()]


def filas_clientes(gestor: GestorSistema):
    return [[c.dni, c.nombre, c.edad, c.email, c.tipo_cliente]
            for c in gestor.listar_clientes()]


def filas_trabajadores(gestor: GestorSistema):
    return [[t.legajo, t.dni, t.nombre, t.edad, t.cargo, f"${t.salario:.2f}"]
            for t in gestor.listar_trabajadores()]


def filas_ordenes(gestor: GestorSistema):
    return [[o.numero, o.fecha, o.dni_cliente, o.dni_trabajador,
              len(o.items), f"${o.total:.2f}"]
            for o in gestor.listar_ordenes()]


def refrescar_todo(window, gestor: GestorSistema):
    window["-TABLA_PRODUCTOS-"].update(filas_productos(gestor))
    window["-TABLA_CLIENTES-"].update(filas_clientes(gestor))
    window["-TABLA_TRABAJADORES-"].update(filas_trabajadores(gestor))
    window["-TABLA_ORDENES-"].update(filas_ordenes(gestor))
    window["-COMBO_CLIENTE-"].update(
        values=[f"{c.dni} - {c.nombre}" for c in gestor.listar_clientes()])
    window["-COMBO_TRABAJADOR-"].update(
        values=[f"{t.dni} - {t.nombre}" for t in gestor.listar_trabajadores()])


def fila_seleccionada(window, tabla_key, lista):
    """Devuelve el objeto seleccionado en una tabla, o None si no hay seleccion."""
    seleccion = window[tabla_key].get()
    indices = window[tabla_key].SelectedRows if hasattr(window[tabla_key], "SelectedRows") else []
    if not indices:
        return None
    idx = indices[0]
    if idx >= len(lista):
        return None
    return lista[idx]


# ----------------------------------------------------------------------
# Ventana: Agregar / Editar Producto
# ----------------------------------------------------------------------

def ventana_producto(gestor: GestorSistema, producto=None):
    editando = producto is not None
    titulo = "Editar Producto" if editando else "Agregar Producto"

    layout = [
        [sg.Text("Descripcion:", size=(12, 1)),
         sg.Input(producto.descripcion if editando else "", key="-DESC-")],
        [sg.Text("Precio:", size=(12, 1)),
         sg.Input(str(producto.precio) if editando else "", key="-PRECIO-")],
        [sg.Text("Stock:", size=(12, 1)),
         sg.Input(str(producto.stock) if editando else "", key="-STOCK-")],
        [sg.Push(), sg.Button("Guardar"), sg.Button("Cancelar")],
    ]
    win = sg.Window(titulo, layout, modal=True)

    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, "Cancelar"):
            break
        if event == "Guardar":
            try:
                precio = float(values["-PRECIO-"].replace(",", "."))
                stock = int(values["-STOCK-"])
                if editando:
                    gestor.editar_producto(producto.codigo, descripcion=values["-DESC-"],
                                            precio=precio, stock=stock)
                    sg.popup_ok("Producto actualizado con exito.")
                else:
                    gestor.agregar_producto(values["-DESC-"], precio, stock)
                    sg.popup_ok("Producto agregado con exito.")
                break
            except ValueError:
                sg.popup_error("Precio y Stock deben ser numeros validos.")
            except ErrorSistema as e:
                sg.popup_error(str(e))

    win.close()


def ventana_descontar_stock(gestor: GestorSistema, producto):
    layout = [
        [sg.Text(f"Producto: {producto.descripcion} (stock actual: {producto.stock})")],
        [sg.Text("Cantidad a descontar:", size=(18, 1)), sg.Input(key="-CANT-")],
        [sg.Push(), sg.Button("Confirmar"), sg.Button("Cancelar")],
    ]
    win = sg.Window("Descontar Stock", layout, modal=True)
    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, "Cancelar"):
            break
        if event == "Confirmar":
            try:
                cantidad = int(values["-CANT-"])
                gestor.descontar_stock(producto.codigo, cantidad)
                sg.popup_ok("Stock actualizado con exito.")
                break
            except ValueError:
                sg.popup_error("La cantidad debe ser un numero entero.")
            except ErrorSistema as e:
                sg.popup_error(str(e))
    win.close()


# ----------------------------------------------------------------------
# Ventana: Agregar Cliente / Trabajador
# ----------------------------------------------------------------------

def ventana_cliente(gestor: GestorSistema):
    layout = [
        [sg.Text("DNI:", size=(12, 1)), sg.Input(key="-DNI-")],
        [sg.Text("Nombre:", size=(12, 1)), sg.Input(key="-NOMBRE-")],
        [sg.Text("Edad:", size=(12, 1)), sg.Input(key="-EDAD-")],
        [sg.Text("Email:", size=(12, 1)), sg.Input(key="-EMAIL-")],
        [sg.Text("Tipo:", size=(12, 1)),
         sg.Combo(["Minorista", "Mayorista"], default_value="Minorista", key="-TIPO-",
                   readonly=True)],
        [sg.Push(), sg.Button("Guardar"), sg.Button("Cancelar")],
    ]
    win = sg.Window("Agregar Cliente", layout, modal=True)
    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, "Cancelar"):
            break
        if event == "Guardar":
            try:
                dni = int(values["-DNI-"])
                edad = int(values["-EDAD-"])
                gestor.agregar_cliente(dni, values["-NOMBRE-"], edad,
                                        values["-EMAIL-"], values["-TIPO-"])
                sg.popup_ok("Cliente registrado con exito.")
                break
            except ValueError:
                sg.popup_error("DNI y Edad deben ser numeros enteros.")
            except ErrorSistema as e:
                sg.popup_error(str(e))
    win.close()


def ventana_trabajador(gestor: GestorSistema):
    layout = [
        [sg.Text("DNI:", size=(12, 1)), sg.Input(key="-DNI-")],
        [sg.Text("Nombre:", size=(12, 1)), sg.Input(key="-NOMBRE-")],
        [sg.Text("Edad:", size=(12, 1)), sg.Input(key="-EDAD-")],
        [sg.Text("Legajo:", size=(12, 1)), sg.Input(key="-LEGAJO-")],
        [sg.Text("Cargo:", size=(12, 1)), sg.Input(key="-CARGO-")],
        [sg.Text("Salario:", size=(12, 1)), sg.Input(key="-SALARIO-")],
        [sg.Push(), sg.Button("Guardar"), sg.Button("Cancelar")],
    ]
    win = sg.Window("Agregar Trabajador", layout, modal=True)
    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, "Cancelar"):
            break
        if event == "Guardar":
            try:
                dni = int(values["-DNI-"])
                edad = int(values["-EDAD-"])
                legajo = int(values["-LEGAJO-"])
                salario = float(values["-SALARIO-"].replace(",", "."))
                gestor.agregar_trabajador(dni, values["-NOMBRE-"], edad, legajo,
                                           values["-CARGO-"], salario)
                sg.popup_ok("Trabajador registrado con exito.")
                break
            except ValueError:
                sg.popup_error("DNI, Edad, Legajo y Salario deben ser numeros validos.")
            except ErrorSistema as e:
                sg.popup_error(str(e))
    win.close()


# ----------------------------------------------------------------------
# Ventana: Generar Orden de Compra
# ----------------------------------------------------------------------

def ventana_generar_orden(gestor: GestorSistema):
    clientes = gestor.listar_clientes()
    trabajadores = gestor.listar_trabajadores()
    if not clientes:
        sg.popup_error("Primero tenes que registrar al menos un Cliente.")
        return
    if not trabajadores:
        sg.popup_error("Primero tenes que registrar al menos un Trabajador.")
        return

    items_temporales = []  # [(codigo, descripcion, precio, cantidad)]

    layout = [
        [sg.Text("Cliente:", size=(12, 1)),
         sg.Combo([f"{c.dni} - {c.nombre}" for c in clientes], key="-CLIENTE-", readonly=True)],
        [sg.Text("Trabajador:", size=(12, 1)),
         sg.Combo([f"{t.dni} - {t.nombre}" for t in trabajadores], key="-TRABAJADOR-",
                   readonly=True)],
        [sg.HorizontalSeparator()],
        [sg.Text("Codigo Producto:", size=(14, 1)), sg.Input(key="-COD_PROD-", size=(10, 1)),
         sg.Text("Cantidad:"), sg.Input(key="-CANT_PROD-", size=(6, 1)),
         sg.Button("Agregar item")],
        [sg.Table(values=[], headings=["Codigo", "Producto", "P. Unit.", "Cant.", "Subtotal"],
                   key="-TABLA_ITEMS-", auto_size_columns=False,
                   col_widths=[8, 20, 10, 6, 10], num_rows=6, justification="left")],
        [sg.Text("", key="-TOTAL-", font=("Any", 10, "bold"))],
        [sg.Push(), sg.Button("Confirmar Orden"), sg.Button("Cancelar")],
    ]
    win = sg.Window("Generar Orden de Compra", layout, modal=True)

    def refrescar_items():
        filas = [[c, d, f"${p:.2f}", ca, f"${p * ca:.2f}"] for c, d, p, ca in items_temporales]
        total = sum(p * ca for _, _, p, ca in items_temporales)
        win["-TABLA_ITEMS-"].update(filas)
        win["-TOTAL-"].update(f"Total (sin descuento): ${total:.2f}")

    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, "Cancelar"):
            break

        if event == "Agregar item":
            try:
                codigo = int(values["-COD_PROD-"])
                cantidad = int(values["-CANT_PROD-"])
                producto = gestor.buscar_producto_por_codigo(codigo)
                if cantidad <= 0:
                    raise ValueError
                # Verifica contra el stock actual menos lo ya cargado en esta orden
                ya_pedido = sum(ca for c, _, _, ca in items_temporales if c == codigo)
                if cantidad + ya_pedido > producto.stock:
                    sg.popup_error(
                        f"Stock insuficiente para '{producto.descripcion}'. "
                        f"Disponible: {producto.stock}.")
                    continue
                items_temporales.append(
                    (producto.codigo, producto.descripcion, producto.precio, cantidad))
                refrescar_items()
            except ValueError:
                sg.popup_error("Codigo y Cantidad deben ser numeros enteros validos.")
            except ErrorSistema as e:
                sg.popup_error(str(e))

        if event == "Confirmar Orden":
            if not values["-CLIENTE-"] or not values["-TRABAJADOR-"]:
                sg.popup_error("Elegi un Cliente y un Trabajador.")
                continue
            if not items_temporales:
                sg.popup_error("Agrega al menos un item a la orden.")
                continue
            try:
                dni_cliente = int(values["-CLIENTE-"].split(" - ")[0])
                dni_trabajador = int(values["-TRABAJADOR-"].split(" - ")[0])
                orden = gestor.crear_orden(dni_cliente, dni_trabajador)
                for codigo, _, _, cantidad in items_temporales:
                    gestor.agregar_item_a_orden(orden, codigo, cantidad)
                total = gestor.confirmar_orden(orden)
                sg.popup_ok(f"Orden #{orden.numero} confirmada.\nTotal a pagar: ${total:.2f}")
                break
            except ErrorSistema as e:
                sg.popup_error(str(e))

    win.close()


# ----------------------------------------------------------------------
# Ventana principal
# ----------------------------------------------------------------------

def construir_layout(gestor: GestorSistema):
    tab_productos = [
        [sg.Table(values=filas_productos(gestor),
                   headings=["Codigo", "Descripcion", "Precio", "Stock"],
                   key="-TABLA_PRODUCTOS-", auto_size_columns=False,
                   col_widths=[8, 30, 12, 8], num_rows=14, justification="left",
                   enable_events=True)],
        [sg.Button("Nuevo Producto"), sg.Button("Editar Producto"),
         sg.Button("Descontar Stock"), sg.Button("Eliminar Producto")],
    ]

    tab_clientes = [
        [sg.Table(values=filas_clientes(gestor),
                   headings=["DNI", "Nombre", "Edad", "Email", "Tipo"],
                   key="-TABLA_CLIENTES-", auto_size_columns=False,
                   col_widths=[12, 20, 6, 22, 10], num_rows=14, justification="left")],
        [sg.Button("Nuevo Cliente"), sg.Button("Eliminar Cliente")],
    ]

    tab_trabajadores = [
        [sg.Table(values=filas_trabajadores(gestor),
                   headings=["Legajo", "DNI", "Nombre", "Edad", "Cargo", "Salario"],
                   key="-TABLA_TRABAJADORES-", auto_size_columns=False,
                   col_widths=[8, 12, 20, 6, 15, 12], num_rows=14, justification="left")],
        [sg.Button("Nuevo Trabajador"), sg.Button("Eliminar Trabajador")],
    ]

    tab_ordenes = [
        [sg.Table(values=filas_ordenes(gestor),
                   headings=["Nro", "Fecha", "DNI Cliente", "DNI Trabajador", "Items", "Total"],
                   key="-TABLA_ORDENES-", auto_size_columns=False,
                   col_widths=[6, 16, 12, 14, 6, 10], num_rows=14, justification="left")],
        [sg.Button("Generar Orden")],
        [sg.Combo([], key="-COMBO_CLIENTE-", visible=False),
         sg.Combo([], key="-COMBO_TRABAJADOR-", visible=False)],
    ]

    layout = [
        [sg.TabGroup([[
            sg.Tab("Productos", tab_productos),
            sg.Tab("Clientes", tab_clientes),
            sg.Tab("Trabajadores", tab_trabajadores),
            sg.Tab("Ordenes de Compra", tab_ordenes),
        ]])],
        [sg.Button("Actualizar"), sg.Push(), sg.Button("Salir")],
    ]
    return layout


def main():
    gestor = GestorSistema()
    window = sg.Window("Sistema de Gestion - TP2 POO", construir_layout(gestor),
                        finalize=True, resizable=True)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Salir"):
            break

        elif event == "Actualizar":
            refrescar_todo(window, gestor)

        elif event == "Nuevo Producto":
            ventana_producto(gestor)
            refrescar_todo(window, gestor)

        elif event == "Editar Producto":
            producto = fila_seleccionada(window, "-TABLA_PRODUCTOS-", gestor.listar_productos())
            if producto is None:
                sg.popup_error("Selecciona un producto de la tabla primero.")
            else:
                ventana_producto(gestor, producto)
                refrescar_todo(window, gestor)

        elif event == "Descontar Stock":
            producto = fila_seleccionada(window, "-TABLA_PRODUCTOS-", gestor.listar_productos())
            if producto is None:
                sg.popup_error("Selecciona un producto de la tabla primero.")
            else:
                ventana_descontar_stock(gestor, producto)
                refrescar_todo(window, gestor)

        elif event == "Eliminar Producto":
            producto = fila_seleccionada(window, "-TABLA_PRODUCTOS-", gestor.listar_productos())
            if producto is None:
                sg.popup_error("Selecciona un producto de la tabla primero.")
            elif sg.popup_yes_no(f"Eliminar '{producto.descripcion}'?") == "Yes":
                try:
                    gestor.eliminar_producto(producto.codigo)
                    refrescar_todo(window, gestor)
                except ErrorSistema as e:
                    sg.popup_error(str(e))

        elif event == "Nuevo Cliente":
            ventana_cliente(gestor)
            refrescar_todo(window, gestor)

        elif event == "Eliminar Cliente":
            cliente = fila_seleccionada(window, "-TABLA_CLIENTES-", gestor.listar_clientes())
            if cliente is None:
                sg.popup_error("Selecciona un cliente de la tabla primero.")
            elif sg.popup_yes_no(f"Eliminar a '{cliente.nombre}'?") == "Yes":
                try:
                    gestor.eliminar_cliente(cliente.dni)
                    refrescar_todo(window, gestor)
                except ErrorSistema as e:
                    sg.popup_error(str(e))

        elif event == "Nuevo Trabajador":
            ventana_trabajador(gestor)
            refrescar_todo(window, gestor)

        elif event == "Eliminar Trabajador":
            trabajador = fila_seleccionada(window, "-TABLA_TRABAJADORES-",
                                            gestor.listar_trabajadores())
            if trabajador is None:
                sg.popup_error("Selecciona un trabajador de la tabla primero.")
            elif sg.popup_yes_no(f"Eliminar a '{trabajador.nombre}'?") == "Yes":
                try:
                    gestor.eliminar_trabajador(trabajador.dni)
                    refrescar_todo(window, gestor)
                except ErrorSistema as e:
                    sg.popup_error(str(e))

        elif event == "Generar Orden":
            ventana_generar_orden(gestor)
            refrescar_todo(window, gestor)

    window.close()


if __name__ == "__main__":
    main()