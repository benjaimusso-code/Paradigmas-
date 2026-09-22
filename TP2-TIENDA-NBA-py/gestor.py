import json
import os

from models import Producto, Cliente, Trabajador, OrdenCompra, ItemOrden
from excepts import (
    ProductoNoEncontrado, StockInsuficiente, LimiteProductosAlcanzado,
    PersonaNoEncontrada, PersonaDuplicada, ErrorPersistencia, ErrorValidacion,
)

MAX_PRODUCTOS = 100

ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_CLIENTES = "clientes.json"
ARCHIVO_TRABAJADORES = "trabajadores.json"
ARCHIVO_ORDENES = "ordenes.json"


class GestorSistema:
    def __init__(self, directorio_datos: str = "."):
        self.directorio_datos = directorio_datos
        self.productos: dict[int, Producto] = {}
        self.clientes: dict[int, Cliente] = {}
        self.trabajadores: dict[int, Trabajador] = {}
        self.ordenes: dict[int, OrdenCompra] = {}
        self.cargar_todo()

    def _ruta(self, nombre_archivo: str) -> str:
        return os.path.join(self.directorio_datos, nombre_archivo)

    def _guardar_coleccion(self, nombre_archivo: str, coleccion: dict):
        try:
            datos = [obj.to_dict() for obj in coleccion.values()]
            with open(self._ruta(nombre_archivo), "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise ErrorPersistencia(f"No se pudo guardar '{nombre_archivo}': {e}")

    def _cargar_coleccion(self, nombre_archivo: str, clase) -> dict:
        ruta = self._ruta(nombre_archivo)
        if not os.path.exists(ruta):
            return {}
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise ErrorPersistencia(f"No se pudo leer '{nombre_archivo}': {e}")

        resultado = {}
        for item in datos:
            obj = clase.from_dict(item)
            clave = obj.codigo if clase is Producto else (
                obj.numero if clase is OrdenCompra else obj.dni)
            resultado[clave] = obj
        return resultado

    def guardar_productos(self):
        self._guardar_coleccion(ARCHIVO_PRODUCTOS, self.productos)

    def guardar_clientes(self):
        self._guardar_coleccion(ARCHIVO_CLIENTES, self.clientes)

    def guardar_trabajadores(self):
        self._guardar_coleccion(ARCHIVO_TRABAJADORES, self.trabajadores)

    def guardar_ordenes(self):
        self._guardar_coleccion(ARCHIVO_ORDENES, self.ordenes)

    def cargar_todo(self):
        self.productos = self._cargar_coleccion(ARCHIVO_PRODUCTOS, Producto)
        self.clientes = self._cargar_coleccion(ARCHIVO_CLIENTES, Cliente)
        self.trabajadores = self._cargar_coleccion(ARCHIVO_TRABAJADORES, Trabajador)
        self.ordenes = self._cargar_coleccion(ARCHIVO_ORDENES, OrdenCompra)

    def _proximo_codigo_producto(self) -> int:
        return max(self.productos.keys(), default=0) + 1

    def agregar_producto(self, descripcion: str, precio: float, stock: int) -> Producto:
        if len(self.productos) >= MAX_PRODUCTOS:
            raise LimiteProductosAlcanzado(
                f"Se alcanzo el limite maximo de productos ({MAX_PRODUCTOS}).")
        codigo = self._proximo_codigo_producto()
        producto = Producto(codigo, descripcion, precio, stock)
        self.productos[codigo] = producto
        self.guardar_productos()
        return producto

    def buscar_producto_por_codigo(self, codigo: int) -> Producto:
        producto = self.productos.get(codigo)
        if producto is None:
            raise ProductoNoEncontrado(f"No existe un producto con codigo {codigo}.")
        return producto

    def buscar_producto_por_descripcion(self, texto: str) -> Producto:
        texto_norm = texto.strip().lower()
        for producto in self.productos.values():
            if producto.descripcion.lower() == texto_norm:
                return producto
        raise ProductoNoEncontrado(f"No se encontro ningun producto llamado '{texto}'.")

    def listar_productos(self) -> list[Producto]:
        return sorted(self.productos.values(), key=lambda p: p.codigo)

    def editar_producto(self, codigo: int, *, descripcion=None, precio=None, stock=None) -> Producto:
        producto = self.buscar_producto_por_codigo(codigo)
        if descripcion is not None:
            producto.descripcion = descripcion
        if precio is not None:
            producto.precio = precio
        if stock is not None:
            producto.stock = stock
        self.guardar_productos()
        return producto

    def descontar_stock(self, codigo: int, cantidad: int) -> Producto:
        producto = self.buscar_producto_por_codigo(codigo)
        producto.descontar_stock(cantidad)  # puede lanzar StockInsuficiente
        self.guardar_productos()
        return producto

    def eliminar_producto(self, codigo: int):
        if codigo not in self.productos:
            raise ProductoNoEncontrado(f"No existe un producto con codigo {codigo}.")
        del self.productos[codigo]
        self.guardar_productos()

    def agregar_cliente(self, dni: int, nombre: str, edad: int, email: str,
                         tipo_cliente: str = "Minorista") -> Cliente:
        if dni in self.clientes:
            raise PersonaDuplicada(f"Ya existe un cliente con DNI {dni}.")
        cliente = Cliente(dni, nombre, edad, email, tipo_cliente)
        self.clientes[dni] = cliente
        self.guardar_clientes()
        return cliente

    def buscar_cliente(self, dni: int) -> Cliente:
        cliente = self.clientes.get(dni)
        if cliente is None:
            raise PersonaNoEncontrada(f"No existe un cliente con DNI {dni}.")
        return cliente

    def listar_clientes(self) -> list[Cliente]:
        return sorted(self.clientes.values(), key=lambda c: c.nombre)

    def eliminar_cliente(self, dni: int):
        if dni not in self.clientes:
            raise PersonaNoEncontrada(f"No existe un cliente con DNI {dni}.")
        del self.clientes[dni]
        self.guardar_clientes()

    def agregar_trabajador(self, dni: int, nombre: str, edad: int, legajo: int,
                            cargo: str, salario: float) -> Trabajador:
        if dni in self.trabajadores:
            raise PersonaDuplicada(f"Ya existe un trabajador con DNI {dni}.")
        trabajador = Trabajador(dni, nombre, edad, legajo, cargo, salario)
        self.trabajadores[dni] = trabajador
        self.guardar_trabajadores()
        return trabajador

    def buscar_trabajador(self, dni: int) -> Trabajador:
        trabajador = self.trabajadores.get(dni)
        if trabajador is None:
            raise PersonaNoEncontrada(f"No existe un trabajador con DNI {dni}.")
        return trabajador

    def listar_trabajadores(self) -> list[Trabajador]:
        return sorted(self.trabajadores.values(), key=lambda t: t.legajo)

    def eliminar_trabajador(self, dni: int):
        if dni not in self.trabajadores:
            raise PersonaNoEncontrada(f"No existe un trabajador con DNI {dni}.")
        del self.trabajadores[dni]
        self.guardar_trabajadores()

    def _proximo_numero_orden(self) -> int:
        return max(self.ordenes.keys(), default=0) + 1

    def crear_orden(self, dni_cliente: int, dni_trabajador: int) -> OrdenCompra:
        # Verifica que existan (lanza PersonaNoEncontrada si no)
        self.buscar_cliente(dni_cliente)
        self.buscar_trabajador(dni_trabajador)
        numero = self._proximo_numero_orden()
        orden = OrdenCompra(numero, dni_cliente, dni_trabajador)
        self.ordenes[numero] = orden
        return orden

    def agregar_item_a_orden(self, orden: OrdenCompra, codigo_producto: int, cantidad: int):
        producto = self.buscar_producto_por_codigo(codigo_producto)
        if cantidad > producto.stock:
            raise StockInsuficiente(
                f"Stock insuficiente para '{producto.descripcion}'. "
                f"Disponible: {producto.stock}, solicitado: {cantidad}.")
        item = ItemOrden(producto.codigo, producto.descripcion, producto.precio, cantidad)
        orden.agregar_item(item)

    def confirmar_orden(self, orden: OrdenCompra) -> float:
        """Valida que tenga items, descuenta stock de cada producto,
        calcula el total (con descuento si el cliente es Mayorista) y
        persiste todo."""
        orden.validar_no_vacia()
        cliente = self.buscar_cliente(orden.dni_cliente)

        for item in orden.items:
            self.descontar_stock(item.codigo_producto, item.cantidad)

        total = orden.calcular_total_con_descuento(cliente.descuento)
        self.guardar_ordenes()
        return total

    def buscar_orden(self, numero: int) -> OrdenCompra:
        orden = self.ordenes.get(numero)
        if orden is None:
            from excepts import OrdenNoEncontrada
            raise OrdenNoEncontrada(f"No existe una orden con numero {numero}.")
        return orden

    def listar_ordenes(self) -> list[OrdenCompra]:
        return sorted(self.ordenes.values(), key=lambda o: o.numero)