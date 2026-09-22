# TP2 POO — Explicación línea a línea y arquitectura

Sistema de gestión de inventario (NBA merchandise store) para la materia
Paradigmas de Programación. Está armado en 5 archivos, cada uno con una
responsabilidad bien separada:

```
models.py   -> Qué SON las cosas (Producto, Cliente, Trabajador, Orden) y sus reglas
excepts.py  -> Qué errores propios puede tirar el sistema
gestor.py   -> La lógica de negocio: crear, buscar, editar, eliminar, persistir en JSON
main.py     -> Interfaz de consola (input/print) que usa el gestor
gui.py      -> Interfaz gráfica (PySimpleGUI) que usa el mismo gestor
```

**Idea central del diseño:** `main.py` y `gui.py` son dos "caras" completamente
distintas del mismo sistema, pero ninguna de las dos tiene lógica de negocio
propia — las dos llaman a los mismos métodos de `GestorSistema`. Esto es
justamente lo que se busca en POO: separar la lógica de la presentación,
para poder cambiar cómo se muestra el programa sin tocar cómo funciona.

```
   main.py (consola)  ─┐
                        ├──►  gestor.py (GestorSistema)  ──►  models.py (clases)
   gui.py (ventanas)  ─┘              │                            │
                                       │                            │
                                       ▼                            ▼
                              productos.json, etc.          excepts.py (errores)
                              (persistencia en disco)        usados en ambos lados
```

---

## 1. excepts.py — Excepciones personalizadas

Define los tipos de error propios del dominio del sistema. Ninguna clase acá
tiene lógica: solo existen para poder distinguir *qué salió mal* en cualquier
punto del programa.

```python
class ErrorSistema(Exception):
    pass
```

- Hereda de `Exception`, la clase base de todos los errores en Python.
- Es la **raíz** de toda la jerarquía: todas las demás excepciones de este
  archivo heredan de ella (directa o indirectamente). Esto permite en
  cualquier parte del código escribir `except ErrorSistema` y atrapar
  **cualquiera** de tus errores custom con un solo bloque, sin tener que
  poner un `except` distinto por cada tipo específico.
- `pass`: no necesita agregar nada propio, con heredar de `Exception` ya
  funciona como algo que se puede `raise` y `except`.

```python
class ErrorValidacion(ErrorSistema):
    """Se lanza cuando un dato no cumple las reglas de validacion (setters)."""
    pass
```

- Hereda de `ErrorSistema`, no directamente de `Exception` — formando una
  jerarquía de dos niveles.
- El docstring documenta cuándo se usa. Se dispara específicamente dentro de
  los `setters` de `models.py`.

El resto de las clases (`ProductoNoEncontrado`, `StockInsuficiente`,
`LimiteProductosAlcanzado`, `PersonaNoEncontrada`, `PersonaDuplicada`,
`OrdenSinItems`, `OrdenNoEncontrada`, `ErrorPersistencia`) siguen el
**mismo patrón exacto**: heredan de `ErrorSistema`, sin lógica propia, cada
una representando un escenario de error específico (inventario, personas,
órdenes, archivos).

**Relación con el resto:** `models.py` usa `ErrorValidacion` y
`StockInsuficiente`. `gestor.py` usa casi todas las demás. `gui.py` y
`main.py` nunca crean estas excepciones — solo las **atrapan** con
`except ErrorSistema` para mostrarle el mensaje al usuario.

---

## 2. models.py — Las clases del dominio

Define qué es cada entidad del sistema y las reglas que sus datos deben
cumplir. Es el archivo que no depende de ningún otro propio salvo
`excepts.py`.

### La interfaz Serializable

```python
from abc import ABC, abstractmethod
```

- `ABC` y `abstractmethod` vienen del módulo `abc`, y sirven para crear
  **clases abstractas**: clases que definen un contrato obligatorio para
  sus subclases, pero que no se pueden instanciar directamente.

```python
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
```

- `class Serializable(ABC)`: al heredar de `ABC`, la clase se vuelve
  abstracta — Python no deja hacer `Serializable()` directamente.
- `@abstractmethod`: marca `to_dict` como obligatorio para cualquier
  subclase concreta. Si una subclase no lo implementa, Python tampoco deja
  instanciarla — se detecta al crear el objeto, no recién al llamar el
  método.
- `-> dict`: type hint, documentación del tipo esperado de retorno (Python
  no lo fuerza en runtime).
- `@classmethod` + `@abstractmethod`: `from_dict` se llama sobre la
  **clase**, no sobre una instancia (recibe `cls` en vez de `self`) — tiene
  sentido porque su trabajo es crear una instancia nueva a partir de un
  diccionario; el objeto todavía no existe cuando se lo llama.
- **Para qué sirve:** es el contrato que le permite a `gestor.py` guardar y
  cargar cualquier tipo de objeto (Producto, Cliente, Trabajador, Orden) de
  forma **genérica**, sin código distinto por cada clase.

### La clase Persona (abstracta)

```python
class Persona(Serializable):
    def __init__(self, dni: int, nombre: str, edad: int):
        self.dni = dni
        self.nombre = nombre
        self.edad = edad
```

- Hereda de `Serializable` (y por lo tanto también de la obligación de
  implementar `to_dict`/`from_dict`, cosa que hará cada subclase concreta).
- `__init__` es el constructor: se ejecuta al crear el objeto.
- **Clave:** `self.dni = dni` no asigna directo — dispara el **setter** de
  la propiedad `dni` (ver abajo). Así, desde el instante de creación, el
  dato ya pasa por validación.

```python
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
```

Patrón central de todo el archivo (se repite para cada atributo de cada
clase):

- `@property`: convierte `dni(self)` en algo que se **accede como
  atributo** (`persona.dni`), no como función. Devuelve `self._dni`, el
  atributo interno real (con guion bajo, convención de "uso interno").
- `@dni.setter`: define qué pasa al **asignar** un valor
  (`persona.dni = 123`). En vez de guardarlo directo, corre esta validación
  primero.
- `type(value) != int`: valida el tipo exacto (no acepta un string
  numérico). Si falla, `raise ErrorValidacion(...)`.
- `1000000 < value < 99999999`: Python permite encadenar comparaciones así,
  equivalente a `a < b and b < c`.
- `self._dni = value`: recién si pasó ambas validaciones, guarda en el
  atributo interno.
- **Por qué este diseño:** cualquier lugar del código que haga
  `objeto.dni = algo` pasa automáticamente por la validación — no hay forma
  de saltearla sin tocar directamente `_dni`. Esto es **encapsulamiento**.

Los setters de `nombre` y `edad` siguen el mismo patrón, cambiando la
regla: `nombre` valida `str` con más de 2 caracteres tras `.strip()`;
`edad` valida `int` positivo.

```python
    @abstractmethod
    def descripcion(self) -> str:
        pass

    def __str__(self):
        return self.descripcion()
```

- `descripcion` es otro método abstracto: cada subclase (`Cliente`,
  `Trabajador`) lo implementa a su manera — esto es **polimorfismo**.
- `__str__` es un método mágico de Python: se llama automáticamente con
  `print(objeto)` o `str(objeto)`. Delegarlo a `descripcion()` hace que
  `print(persona)` siempre muestre el texto correcto, sea `Cliente` o
  `Trabajador`.

### Trabajador (hereda de Persona)

```python
class Trabajador(Persona):
    def __init__(self, dni: int, nombre: str, edad: int, legajo: int,
                 cargo: str, salario: float):
        super().__init__(dni, nombre, edad)
        self.legajo = legajo
        self.cargo = cargo
        self.salario = salario
```

- `class Trabajador(Persona)`: herencia — `Trabajador` **es una**
  `Persona`, con atributos extra.
- `super().__init__(...)`: llama al constructor del padre para que valide y
  guarde `dni`, `nombre`, `edad`, sin duplicar esa lógica acá.
- `legajo`, `cargo`, `salario` tienen sus propios `property`/`setter` con el
  mismo patrón (validar tipo + validar regla de negocio: `legajo > 0`,
  `cargo` no vacío, `salario > 0`).

```python
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
```

- `descripcion` implementa el método abstracto exigido por `Persona`.
- `to_dict` implementa el contrato de `Serializable`: devuelve un
  diccionario plano, más `"tipo": "Trabajador"` (campo informativo, aunque
  `gestor.py` en la práctica no lo usa para decidir la clase al cargar).
- `from_dict` reconstruye el objeto desde un diccionario. `cls(...)` en vez
  de `Trabajador(...)`: como es `@classmethod`, `cls` **es** la clase, así
  el método sigue funcionando bien aunque en algún momento se herede de
  `Trabajador`.

### Cliente (mismo esquema que Trabajador)

```python
class Cliente(Persona):
    TIPOS_VALIDOS = ("Minorista", "Mayorista")
```

- Atributo de **clase** (no de instancia): compartido por todos los
  objetos `Cliente`, no cada uno tiene su copia.

```python
    @tipo_cliente.setter
    def tipo_cliente(self, value):
        if type(value) != str:
            raise ErrorValidacion("El tipo de cliente debe ser texto.")
        if value not in self.TIPOS_VALIDOS:
            raise ErrorValidacion(
                f"Tipo de cliente invalido. Debe ser uno de: {self.TIPOS_VALIDOS}")
        self._tipo_cliente = value
```

- `value not in self.TIPOS_VALIDOS`: chequea que esté dentro de la tupla
  permitida.

```python
    @property
    def descuento(self) -> float:
        """Los mayoristas tienen un descuento fijo del 15%."""
        return 0.15 if self._tipo_cliente == "Mayorista" else 0.0
```

- Property **sin setter** (solo lectura): no se guarda, se **calcula al
  vuelo** cada vez que se accede, según `tipo_cliente`. Evita poder asignar
  `cliente.descuento = 0.5` manualmente.

El resto de `Cliente` (`email`, `to_dict`, `from_dict`) sigue los mismos
patrones ya vistos.

### Producto

Mismo esquema de `property`/`setter` para `codigo`, `descripcion`,
`precio`, `stock`.

```python
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
```

- Encapsula la regla de negocio de descontar stock **dentro de la propia
  clase** `Producto` (no en `gestor.py`): un producto nunca debería poder
  quedar con stock negativo, y es la clase misma la que lo garantiza.
- `from excepts import StockInsuficiente`: **import local**, dentro de la
  función en vez de arriba del archivo — técnica usada normalmente para
  evitar importaciones circulares.
- `self._stock -= cantidad`: resta directo sobre el atributo interno (no
  pasa por el setter de `stock`, que espera un valor completo nuevo, no un
  delta). Es seguro porque ya se validó arriba que no puede quedar
  negativo.

```python
    def __str__(self):
        return (f"Codigo: {self._codigo} | {self._descripcion} | "
                f"${self._precio:.2f} | Stock: {self._stock}")
```

### ItemOrden

```python
class ItemOrden:
    def __init__(self, codigo_producto: int, descripcion: str,
                 precio_unitario: float, cantidad: int):
        self.codigo_producto = codigo_producto
        self.descripcion = descripcion
        self.precio_unitario = precio_unitario
        self.cantidad = cantidad
```

- No hereda de nada (ni `Serializable`, ni `Persona`): es una clase simple
  de "solo transporte", sin validaciones con `property`/`setter`.
- Igual implementa `to_dict`/`from_dict` manualmente, cumpliendo el mismo
  contrato de `Serializable` sin heredar formalmente de ella.

```python
    @property
    def subtotal(self) -> float:
        return self.precio_unitario * self.cantidad
```

- Otra property calculada al vuelo, como `descuento` en `Cliente`.

### OrdenCompra

```python
class OrdenCompra(Serializable):
    def __init__(self, numero: int, dni_cliente: int, dni_trabajador: int,
                 fecha: str = None, items=None):
        self.numero = numero
        self.dni_cliente = dni_cliente
        self.dni_trabajador = dni_trabajador
        self.fecha = fecha or datetime.now().strftime("%d/%m/%Y %H:%M")
        self._items = list(items) if items else []
```

- `fecha=None`, `items=None`: parámetros con valor por defecto, permitiendo
  crear una orden nueva sin pasarlos, o reconstruir una desde JSON pasando
  ambos.
- `fecha or datetime.now().strftime(...)`: si `fecha` es `None` (falsy),
  usa la fecha/hora actual formateada; si vino con valor, usa ese.
- `list(items) if items else []`: **importante** — usar `items=None` como
  default y armar la lista adentro del `__init__` es la forma correcta en
  Python. Si se hubiera escrito `items=[]` directo en la firma, esa lista
  se crearía **una sola vez** al definir la función y se compartiría entre
  todas las órdenes que no pasen `items` — un bug clásico de Python que acá
  se evita bien.

```python
    @property
    def items(self):
        return list(self._items)

    def agregar_item(self, item: ItemOrden):
        self._items.append(item)
```

- `items` devuelve una **copia** de la lista interna, no la original — así
  nadie puede hacer `orden.items.append(...)` desde afuera y modificar la
  orden sin pasar por `agregar_item`. Más encapsulamiento.

```python
    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self._items)

    def calcular_total_con_descuento(self, descuento: float) -> float:
        return self.total * (1 - descuento)

    def validar_no_vacia(self):
        if not self._items:
            raise OrdenSinItems("La orden de compra no tiene items cargados.")
```

- `sum(... for ... in ...)`: expresión generadora, suma los subtotales sin
  crear una lista intermedia.
- `calcular_total_con_descuento`: si `descuento=0.15`, multiplica por
  `0.85` (15% menos).
- `not self._items`: una lista vacía es "falsy" en Python.

**Relación con el resto:** `models.py` solo depende de `excepts.py` (para
lanzar sus errores de validación). Todo lo demás (`gestor.py`, `main.py`,
`gui.py`) depende de `models.py`, nunca al revés.

---

## 3. gestor.py — Lógica de negocio y persistencia

Orquesta todo: usa las clases de `models.py`, lanza (o deja pasar) las
excepciones de `excepts.py`, y guarda/carga todo en archivos JSON. Es la
**única** clase que tanto `main.py` como `gui.py` conocen y usan.

```python
import json
import os
```

- `json`: convierte entre diccionarios/listas de Python y texto JSON
  (`json.dump` escribe, `json.load` lee).
- `os`: rutas de archivo portables entre sistemas operativos.

```python
MAX_PRODUCTOS = 100

ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_CLIENTES = "clientes.json"
ARCHIVO_TRABAJADORES = "trabajadores.json"
ARCHIVO_ORDENES = "ordenes.json"
```

- Constantes de módulo (mayúsculas por convención), centralizando números y
  nombres de archivo en un solo lugar.

```python
class GestorSistema:
    def __init__(self, directorio_datos: str = "."):
        self.directorio_datos = directorio_datos
        self.productos: dict[int, Producto] = {}
        self.clientes: dict[int, Cliente] = {}
        self.trabajadores: dict[int, Trabajador] = {}
        self.ordenes: dict[int, OrdenCompra] = {}
        self.cargar_todo()
```

- `directorio_datos="."`: por defecto usa el directorio actual, pero se
  puede cambiar (útil para tests, por ejemplo con una carpeta temporal).
- `dict[int, Producto]`: type hint, "diccionario con claves int y valores
  Producto" — solo documentación.
- Las 4 colecciones son **diccionarios**, no listas: la clave es el
  identificador natural (código, DNI, número de orden), lo que hace la
  búsqueda por ese identificador instantánea (`self.productos[123]`).
- `self.cargar_todo()`: al crear el gestor, intenta leer los JSON
  existentes y poblar las colecciones — el programa "recuerda" datos entre
  ejecuciones.

```python
    def _ruta(self, nombre_archivo: str) -> str:
        return os.path.join(self.directorio_datos, nombre_archivo)
```

- Guion bajo adelante: convención de "uso interno", no privado real en
  Python.
- `os.path.join`: arma la ruta con el separador correcto según el sistema
  operativo.

```python
    def _guardar_coleccion(self, nombre_archivo: str, coleccion: dict):
        try:
            datos = [obj.to_dict() for obj in coleccion.values()]
            with open(self._ruta(nombre_archivo), "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise ErrorPersistencia(f"No se pudo guardar '{nombre_archivo}': {e}")
```

- Método **genérico**: sirve para las 4 colecciones porque todas sus clases
  implementan `to_dict()` (contrato de `Serializable`).
- `coleccion.values()`: itera solo los objetos, ignorando claves.
- `with open(...) as f:`: context manager, garantiza que el archivo se
  cierre bien aunque ocurra un error adentro.
- `json.dump(datos, f, indent=2, ensure_ascii=False)`: `indent=2` lo
  formatea legible; `ensure_ascii=False` permite guardar tildes/ñ tal cual.
- `except OSError as e: raise ErrorPersistencia(...)`: **traduce**
  excepciones de bajo nivel de Python a tu excepción de dominio — el resto
  del programa nunca necesita saber sobre `OSError`.

```python
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
```

- `clase`: se le pasa la **clase en sí** como parámetro (`Producto`,
  `Cliente`, etc., no una instancia) — en Python las clases se pueden pasar
  como cualquier otro valor.
- `os.path.exists`: si el archivo no existe (primera ejecución del
  programa), devuelve diccionario vacío en vez de romper.
- `except (OSError, json.JSONDecodeError)`: atrapa dos tipos de excepción a
  la vez con una tupla — `JSONDecodeError` ocurre si el archivo existe pero
  tiene contenido corrupto.
- `clase.from_dict(item)`: usa el `classmethod` de cada clase para
  reconstruir el objeto — la misma línea sirve para cualquier clase gracias
  al contrato `Serializable`.
- El ternario anidado decide qué atributo usar como clave del diccionario
  según qué `clase` sea (`is` compara identidad de clase, no valores).

```python
    def guardar_productos(self):
        self._guardar_coleccion(ARCHIVO_PRODUCTOS, self.productos)
```

- Los 4 métodos `guardar_*` son **envoltorios** públicos del método
  genérico privado, fijando qué archivo/colección corresponde a cada uno.

```python
    def cargar_todo(self):
        self.productos = self._cargar_coleccion(ARCHIVO_PRODUCTOS, Producto)
        self.clientes = self._cargar_coleccion(ARCHIVO_CLIENTES, Cliente)
        self.trabajadores = self._cargar_coleccion(ARCHIVO_TRABAJADORES, Trabajador)
        self.ordenes = self._cargar_coleccion(ARCHIVO_ORDENES, OrdenCompra)
```

- Se llama una vez en el constructor para poblar las 4 colecciones al
  arrancar.

```python
    def _proximo_codigo_producto(self) -> int:
        return max(self.productos.keys(), default=0) + 1
```

- `max(..., default=0)`: mayor código actual, o 0 si está vacío (sin
  `default`, `max()` de vacío tira error).
- Autoincrement simple hecho a mano, ya que no hay base de datos real.

```python
    def agregar_producto(self, descripcion: str, precio: float, stock: int) -> Producto:
        if len(self.productos) >= MAX_PRODUCTOS:
            raise LimiteProductosAlcanzado(
                f"Se alcanzo el limite maximo de productos ({MAX_PRODUCTOS}).")
        codigo = self._proximo_codigo_producto()
        producto = Producto(codigo, descripcion, precio, stock)
        self.productos[codigo] = producto
        self.guardar_productos()
        return producto
```

- El código se asigna **automáticamente**, el usuario nunca lo escribe.
- `Producto(...)`: al construir, corren todos los setters con sus
  validaciones (si `precio` es negativo, tira `ErrorValidacion` acá mismo).
- `self.guardar_productos()`: persiste **inmediatamente** — no hay botón
  de "guardar" aparte, cada operación se guarda al toque.

```python
    def buscar_producto_por_codigo(self, codigo: int) -> Producto:
        producto = self.productos.get(codigo)
        if producto is None:
            raise ProductoNoEncontrado(f"No existe un producto con codigo {codigo}.")
        return producto
```

- `dict.get(clave)`: a diferencia de `dict[clave]`, si no existe devuelve
  `None` en vez de tirar `KeyError` — se chequea explícito y se convierte
  en tu excepción de dominio, con mensaje más claro.

```python
    def buscar_producto_por_descripcion(self, texto: str) -> Producto:
        texto_norm = texto.strip().lower()
        for producto in self.productos.values():
            if producto.descripcion.lower() == texto_norm:
                return producto
        raise ProductoNoEncontrado(f"No se encontro ningun producto llamado '{texto}'.")
```

- Como la descripción no es clave del diccionario, se busca recorriendo
  (`for`) todos los productos, comparando normalizado (`.strip().lower()`).
- Patrón "buscar en loop, si no encontrás nada, lanzar error después del
  loop".

```python
    def listar_productos(self) -> list[Producto]:
        return sorted(self.productos.values(), key=lambda p: p.codigo)
```

- `sorted(..., key=lambda p: p.codigo)`: ordena por código, necesario
  porque los diccionarios mantienen orden de inserción, no orden numérico
  de claves.

```python
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
```

- El `*` en la firma hace que todo lo siguiente sean parámetros
  **keyword-only** (obligatoriamente por nombre): `editar_producto(5,
  precio=100)`, no por posición.
- Cada parámetro con default `None` solo se aplica si vino con valor real
  — actualización parcial.
- `producto.descripcion = descripcion`: dispara el **setter** de
  `models.py`, entonces la validación corre automáticamente acá sin que
  `gestor.py` repita ninguna lógica.

```python
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
```

- `descontar_stock` delega la lógica real al método del propio objeto
  `Producto` (definido en `models.py`).
- `eliminar_producto` hace eliminación **física** (`del`), no lógica — no
  hay banderas `_activo` en este código.

Los métodos de `Cliente`/`Trabajador` siguen el mismo esquema, con una
diferencia: como el DNI lo provee el usuario (no se autogenera como el
código de producto), hay que validar explícitamente que no exista ya
(`PersonaDuplicada`).

```python
    def crear_orden(self, dni_cliente: int, dni_trabajador: int) -> OrdenCompra:
        self.buscar_cliente(dni_cliente)
        self.buscar_trabajador(dni_trabajador)
        numero = self._proximo_numero_orden()
        orden = OrdenCompra(numero, dni_cliente, dni_trabajador)
        self.ordenes[numero] = orden
        return orden
```

- `self.buscar_cliente(...)` y `self.buscar_trabajador(...)` se llaman **sin
  usar el resultado** — el propósito es solo validar que existan,
  aprovechando que tiran excepción si no los encuentran.
- La orden se agrega a `self.ordenes` ya acá, pero **no se guarda a disco
  todavía** — eso se pospone hasta `confirmar_orden`.

```python
    def agregar_item_a_orden(self, orden: OrdenCompra, codigo_producto: int, cantidad: int):
        producto = self.buscar_producto_por_codigo(codigo_producto)
        if cantidad > producto.stock:
            raise StockInsuficiente(...)
        item = ItemOrden(producto.codigo, producto.descripcion, producto.precio, cantidad)
        orden.agregar_item(item)
```

- Recibe el objeto `orden` directo (no su número) y lo modifica en memoria
  — como los objetos se pasan por referencia, el cambio se refleja
  automáticamente en `self.ordenes`.
- Valida stock contra el stock **actual** (todavía no descontado).
- Congela `descripcion` y `precio` del producto en el momento de agregarlo:
  si después alguien edita el precio del producto, la orden ya armada
  conserva el precio histórico.

```python
    def confirmar_orden(self, orden: OrdenCompra) -> float:
        orden.validar_no_vacia()
        cliente = self.buscar_cliente(orden.dni_cliente)
        for item in orden.items:
            self.descontar_stock(item.codigo_producto, item.cantidad)
        total = orden.calcular_total_con_descuento(cliente.descuento)
        self.guardar_ordenes()
        return total
```

- Secuencia: 1) valida no vacía (delegando a `models.py`), 2) busca el
  cliente para su descuento, 3) descuenta stock real de cada producto
  (`orden.items` es una copia, seguro de iterar), 4) calcula total con
  descuento, 5) recién ahora persiste la orden.
- Nota: cada `self.descontar_stock(...)` del loop ya guarda
  `productos.json` internamente — si la orden tiene 3 ítems, se reescribe
  3 veces. No es lo más eficiente, pero funciona bien para este tamaño de
  proyecto.

**Relación con el resto:** `gestor.py` es el único puente entre
`models.py`/`excepts.py` y las interfaces (`main.py`, `gui.py`). Ninguna
de las dos interfaces crea objetos `Producto`/`Cliente`/etc. directamente
— siempre pasan por métodos del `GestorSistema`.

---

## 4. main.py — Interfaz de consola

Interfaz alternativa a `gui.py`: usa `input()`/`print()` en vez de
ventanas, pero llama exactamente a los mismos métodos de `GestorSistema`.
Demuestra que la lógica de negocio está bien separada de la presentación.

```python
def leer_entero(mensaje: str) -> int:
    while True:
        entrada = input(mensaje)
        try:
            return int(entrada)
        except ValueError:
            print("Entrada invalida. Ingrese un numero entero.")
```

- Helper reutilizable: pide un dato y **no avanza** hasta que sea válido.
- `while True` solo se corta con el `return` de adentro del `try`.
- `leer_real` es igual pero para `float`, con el mismo truco de
  `.replace(",", ".")` que en la GUI, para aceptar coma decimal.

```python
def pausar():
    input("Presione Enter para continuar...")

def linea():
    print("-" * 60)
```

- `pausar()`: usa `input()` solo para bloquear hasta que el usuario
  presione Enter, sin importar qué tipee.
- `"-" * 60`: multiplicar un string repite ese string esa cantidad de
  veces — línea separadora visual.

```python
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
```

- Patrón repetido en **todos** los `menu_*`: encabezado → pedir datos con
  los helpers seguros → llamar al `gestor` dentro de un `try` → atrapar
  `ErrorSistema` y mostrarlo → `pausar()`.
- No hace falta distinguir `ValueError`/`ErrorSistema` como en la GUI,
  porque `leer_real`/`leer_entero` ya garantizan el tipo correcto antes de
  llegar al gestor.

```python
def menu_buscar_producto(gestor: GestorSistema):
    ...
    try:
        if opcion == 1:
            ...
        elif opcion == 2:
            ...
        else:
            print("Opcion invalida.")
            pausar()
            return
        print(producto)
    except ErrorSistema as e:
        print(f"Error: {e}")
    pausar()
```

- `else: ... return`: corta la función si la opción no es válida, evitando
  ejecutar `print(producto)` con una variable nunca definida.
- `print(producto)` usa el `__str__` de `Producto` (`models.py`).

```python
def menu_listar_personas(gestor: GestorSistema):
    ...
    personas = gestor.listar_clientes() + gestor.listar_trabajadores()
    ...
    for persona in personas:
        print(persona.descripcion())
    pausar()
```

- `gestor.listar_clientes() + gestor.listar_trabajadores()`: concatena dos
  listas de tipos **distintos** en una lista mixta — funciona porque el
  `+` entre listas solo las junta.
- Ejemplo más claro de **polimorfismo** en el proyecto: el loop no necesita
  saber si cada `persona` es `Cliente` o `Trabajador` — cada uno responde
  `.descripcion()` a su manera.

```python
def menu_generar_orden(gestor: GestorSistema):
    ...
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
    ...
```

- **Diferencia clave con la GUI**: acá no hay carrito temporal — cada
  `agregar_item_a_orden` se aplica directo sobre la orden real ya guardada
  en `self.ordenes` del gestor (porque `crear_orden` ya la agregó ahí).
- **Try/except anidados**: el externo atrapa errores generales de todo el
  flujo; el interno, específico a cada ítem, permite seguir intentando
  agregar otros aunque uno falle, sin cortar el loop entero.
- `codigo == 0`: convención de "0 para terminar" (los códigos reales
  arrancan en 1).

```python
def menu_principal():
    gestor = GestorSistema()
    opcion = -1
    while opcion != 0:
        ...
        opcion = leer_entero("Opcion: ")
        acciones = {
            1: menu_agregar_producto,
            2: menu_buscar_producto,
            ...
        }
        if opcion == 0:
            print("Fin del programa.")
        elif opcion in acciones:
            acciones[opcion](gestor)
        else:
            print("Opcion invalida.")
            pausar()
```

- `opcion = -1`: garantiza que el `while` entre al menos una vez.
- `acciones = {1: menu_agregar_producto, ...}`: patrón **"dispatch
  dictionary"** — se guardan las funciones mismas (sin ejecutarlas) como
  valores del diccionario.
- `acciones[opcion](gestor)`: primero obtiene la función del diccionario
  según lo que tipeó el usuario, y después la ejecuta pasándole `gestor` —
  equivalente a un `if/elif` largo pero más corto y fácil de extender.

```python
if __name__ == "__main__":
    menu_principal()
```

- Asegura que `menu_principal()` solo corra si ejecutás `python main.py`
  directamente, no si alguien importa este archivo desde otro script.

**Relación con el resto:** `main.py` solo conoce `GestorSistema` (de
`gestor.py`) y `ErrorSistema`/`ErrorValidacion` (de `excepts.py`). Nunca
importa nada de `models.py` directamente — todo lo que necesita de
Producto/Cliente/etc. lo obtiene a través de los métodos del gestor.

---

## Cómo se relacionan los 5 archivos

| Archivo       | Depende de                          | Lo usan                  |
|---------------|--------------------------------------|---------------------------|
| `excepts.py`  | nada                                 | todos los demás           |
| `models.py`   | `excepts.py`                         | `gestor.py`                |
| `gestor.py`   | `models.py`, `excepts.py`            | `main.py`, `gui.py`        |
| `main.py`     | `gestor.py`, `excepts.py`            | (es un punto de entrada)   |
| `gui.py`      | `gestor.py`, `excepts.py`            | (es un punto de entrada)   |

Flujo típico de una acción (ejemplo: agregar un producto desde la GUI):

1. El usuario completa el formulario en `ventana_producto` (`gui.py`) y
   toca "Guardar".
2. `gui.py` llama a `gestor.agregar_producto(descripcion, precio, stock)`.
3. `gestor.py` valida el límite de productos, genera el código, y crea
   `Producto(codigo, descripcion, precio, stock)` (`models.py`).
4. Al construirse, `Producto` corre sus **setters**, validando cada dato;
   si algo está mal, lanza una excepción de `excepts.py` (`ErrorValidacion`).
5. Si todo salió bien, `gestor.py` guarda el producto en su diccionario
   interno y llama a `guardar_productos()`, que serializa todo a
   `productos.json` usando `Producto.to_dict()`.
6. Si en el camino algo falló, la excepción sube hasta `gui.py`, que la
   atrapa con `except ErrorSistema` y le muestra un popup de error al
   usuario — sin que la ventana se rompa ni cierre.

`main.py` sigue exactamente el mismo flujo (pasos 2 a 6), cambiando
únicamente el paso 1: en vez de un formulario gráfico, pide los datos con
`input()` por consola.