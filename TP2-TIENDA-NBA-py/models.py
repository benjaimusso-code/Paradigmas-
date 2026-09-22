from abc import ABC, abstractmethod
from datetime import datetime
from excepts import ErrorValidacion, OrdenSinItems

class Serializable(ABC):
    """Interfaz que obliga a toda clase persistible a saber convertirse
    a diccionario (para guardar en JSON) y reconstruirse desde uno."""

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        pass

class Persona(Serializable):
    def __init__(self, dni: int, nombre: str, edad: int):
        self.dni = dni
        self.nombre = nombre
        self.edad = edad

    @property
    def dni(self) -> int:
        return self._dni

    @dni.setter
    def dni(self, value):
        if type(value) != int:
            raise ErrorValidacion("El DNI debe ser un numero entero.")
        if not (1000000 < value < 99999999):
            raise ErrorValidacion("El DNI debe estar entre 1.000.000 y 99.999.999.")
        self._dni = value

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        if type(value) != str:
            raise ErrorValidacion("El nombre debe ser texto.")
        if len(value.strip()) < 2:
            raise ErrorValidacion("El nombre debe tener mas de 2 caracteres.")
        self._nombre = value.strip()

    @property
    def edad(self) -> int:
        return self._edad

    @edad.setter
    def edad(self, value):
        if type(value) != int:
            raise ErrorValidacion("La edad debe ser un numero entero.")
        if value <= 0:
            raise ErrorValidacion("La edad debe ser un numero positivo.")
        self._edad = value

    @abstractmethod
    def descripcion(self) -> str:
        pass

    def __str__(self):
        return self.descripcion()


class Trabajador(Persona):
    def __init__(self, dni: int, nombre: str, edad: int, legajo: int,
                 cargo: str, salario: float):
        super().__init__(dni, nombre, edad)
        self.legajo = legajo
        self.cargo = cargo
        self.salario = salario

    @property
    def legajo(self) -> int:
        return self._legajo

    @legajo.setter
    def legajo(self, value):
        if type(value) != int:
            raise ErrorValidacion("El legajo debe ser un numero entero.")
        if value <= 0:
            raise ErrorValidacion("El legajo debe ser un numero positivo.")
        self._legajo = value

    @property
    def cargo(self) -> str:
        return self._cargo

    @cargo.setter
    def cargo(self, value):
        if type(value) != str:
            raise ErrorValidacion("El cargo debe ser texto.")
        if value.strip() == "":
            raise ErrorValidacion("El cargo no puede estar vacio.")
        self._cargo = value.strip()

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, value):
        if type(value) != int and type(value) != float:
            raise ErrorValidacion("El salario debe ser un numero.")
        if value <= 0:
            raise ErrorValidacion("El salario debe ser un numero positivo.")
        self._salario = float(value)

    def descripcion(self) -> str:
        return (f"[Trabajador] Legajo {self._legajo} - {self._nombre} "
                f"({self._cargo}) - DNI {self._dni}")

    def to_dict(self) -> dict:
        return {
            "tipo": "Trabajador",
            "dni": self._dni,
            "nombre": self._nombre,
            "edad": self._edad,
            "legajo": self._legajo,
            "cargo": self._cargo,
            "salario": self._salario,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["dni"], data["nombre"], data["edad"],
                    data["legajo"], data["cargo"], data["salario"])


class Cliente(Persona):
    TIPOS_VALIDOS = ("Minorista", "Mayorista")

    def __init__(self, dni: int, nombre: str, edad: int, email: str,
                 tipo_cliente: str = "Minorista"):
        super().__init__(dni, nombre, edad)
        self.email = email
        self.tipo_cliente = tipo_cliente

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value):
        if type(value) != str:
            raise ErrorValidacion("El email debe ser texto.")
        if "@" not in value or "." not in value:
            raise ErrorValidacion("El email ingresado no es valido.")
        self._email = value.strip()

    @property
    def tipo_cliente(self) -> str:
        return self._tipo_cliente

    @tipo_cliente.setter
    def tipo_cliente(self, value):
        if type(value) != str:
            raise ErrorValidacion("El tipo de cliente debe ser texto.")
        if value not in self.TIPOS_VALIDOS:
            raise ErrorValidacion(
                f"Tipo de cliente invalido. Debe ser uno de: {self.TIPOS_VALIDOS}")
        self._tipo_cliente = value

    @property
    def descuento(self) -> float:
        """Los mayoristas tienen un descuento fijo del 15%."""
        return 0.15 if self._tipo_cliente == "Mayorista" else 0.0

    def descripcion(self) -> str:
        return (f"[Cliente {self._tipo_cliente}] {self._nombre} - DNI {self._dni} "
                f"- {self._email}")

    def to_dict(self) -> dict:
        return {
            "tipo": "Cliente",
            "dni": self._dni,
            "nombre": self._nombre,
            "edad": self._edad,
            "email": self._email,
            "tipo_cliente": self._tipo_cliente,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["dni"], data["nombre"], data["edad"],
                    data["email"], data["tipo_cliente"])


class Producto(Serializable):
    def __init__(self, codigo: int, descripcion: str, precio: float, stock: int):
        self.codigo = codigo
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock

    @property
    def codigo(self) -> int:
        return self._codigo

    @codigo.setter
    def codigo(self, value):
        if type(value) != int:
            raise ErrorValidacion("El codigo debe ser un numero entero.")
        if value <= 0:
            raise ErrorValidacion("El codigo debe ser un numero positivo.")
        self._codigo = value

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, value):
        if type(value) != str:
            raise ErrorValidacion("La descripcion debe ser texto.")
        if value.strip() == "":
            raise ErrorValidacion("La descripcion no puede estar vacia o ser solo espacios.")
        self._descripcion = value.strip()

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, value):
        if type(value) != int and type(value) != float:
            raise ErrorValidacion("El precio debe ser un numero.")
        if value <= 0:
            raise ErrorValidacion("El precio debe ser un numero positivo.")
        self._precio = float(value)

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, value):
        if type(value) != int:
            raise ErrorValidacion("El stock debe ser un numero entero.")
        if value < 0:
            raise ErrorValidacion("El stock debe ser un numero entero mayor o igual a 0.")
        self._stock = value

    def descontar_stock(self, cantidad: int):
        if type(cantidad) != int:
            raise ErrorValidacion("La cantidad a descontar debe ser un entero.")
        if cantidad <= 0:
            raise ErrorValidacion("La cantidad a descontar debe ser un entero positivo.")
        from excepts import StockInsuficiente
        if cantidad > self._stock:
            raise StockInsuficiente(
                f"Stock insuficiente para '{self._descripcion}'. "
                f"Disponible: {self._stock}, solicitado: {cantidad}.")
        self._stock -= cantidad

    def __str__(self):
        return (f"Codigo: {self._codigo} | {self._descripcion} | "
                f"${self._precio:.2f} | Stock: {self._stock}")

    def to_dict(self) -> dict:
        return {
            "codigo": self._codigo,
            "descripcion": self._descripcion,
            "precio": self._precio,
            "stock": self._stock,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["codigo"], data["descripcion"], data["precio"], data["stock"])


class ItemOrden:
    """Representa una linea de la orden: un producto y la cantidad pedida."""

    def __init__(self, codigo_producto: int, descripcion: str,
                 precio_unitario: float, cantidad: int):
        self.codigo_producto = codigo_producto
        self.descripcion = descripcion
        self.precio_unitario = precio_unitario
        self.cantidad = cantidad

    @property
    def subtotal(self) -> float:
        return self.precio_unitario * self.cantidad

    def to_dict(self) -> dict:
        return {
            "codigo_producto": self.codigo_producto,
            "descripcion": self.descripcion,
            "precio_unitario": self.precio_unitario,
            "cantidad": self.cantidad,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["codigo_producto"], data["descripcion"],
                    data["precio_unitario"], data["cantidad"])


class OrdenCompra(Serializable):
    def __init__(self, numero: int, dni_cliente: int, dni_trabajador: int,
                 fecha: str = None, items=None):
        self.numero = numero
        self.dni_cliente = dni_cliente
        self.dni_trabajador = dni_trabajador
        self.fecha = fecha or datetime.now().strftime("%d/%m/%Y %H:%M")
        self._items = list(items) if items else []

    @property
    def numero(self) -> int:
        return self._numero

    @numero.setter
    def numero(self, value):
        if type(value) != int:
            raise ErrorValidacion("El numero de orden debe ser un entero.")
        if value <= 0:
            raise ErrorValidacion("El numero de orden debe ser un entero positivo.")
        self._numero = value

    @property
    def items(self):
        return list(self._items)

    def agregar_item(self, item: ItemOrden):
        self._items.append(item)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self._items)

    def calcular_total_con_descuento(self, descuento: float) -> float:
        return self.total * (1 - descuento)

    def validar_no_vacia(self):
        if not self._items:
            raise OrdenSinItems("La orden de compra no tiene items cargados.")

    def to_dict(self) -> dict:
        return {
            "numero": self._numero,
            "dni_cliente": self.dni_cliente,
            "dni_trabajador": self.dni_trabajador,
            "fecha": self.fecha,
            "items": [item.to_dict() for item in self._items],
        }

    @classmethod
    def from_dict(cls, data: dict):
        items = [ItemOrden.from_dict(i) for i in data.get("items", [])]
        return cls(data["numero"], data["dni_cliente"], data["dni_trabajador"],
                    data["fecha"], items)