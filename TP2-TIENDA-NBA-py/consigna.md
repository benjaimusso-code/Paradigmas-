# **TRABAJO PRÁCTICO N° 2**

### Paradigmas de Programación

Ingeniería de Sistemas - 2do Año

### **Paradigma Orientado a Objetos - Lenguaje Python**

_CRUD: Gestión de Tienda de Artículos de NBA (versión POO)_

| **Campo**         | **Detalle**                                                |
| ------------------ | ----------------------------------------------------------- |
| Materia            | Paradigmas de Programación                                  |
| Año                | 2do. Año - Ingeniería de Sistemas                            |
| Modalidad           | Grupal (2 o 3 alumnos - mismo grupo que TP1, de ser posible) |
| Lenguaje            | Python (POO)                                                 |
| Entrega             | Presentación y defensa oral en clase                        |
| Requisito previo    | Haber entregado el TP1 (versión estructurada en Pascal)     |

## **Objetivo del Trabajo**

Este TP2 retoma el mismo dominio de negocio que el TP1 (Gestión de Tienda de Artículos de NBA), pero exige resolverlo aplicando el paradigma de Programación Orientada a Objetos en Python. El objetivo no es solo "traducir" el código de Pascal a Python, sino rediseñar la solución utilizando clases, encapsulamiento, herencia, polimorfismo y manejo de excepciones, de forma que el grupo pueda explicar y justificar en qué cambia el diseño respecto de la versión estructurada.

Durante la defensa oral se pedirá explícitamente una comparación entre ambos paradigmas.

## **1. Historia de Usuario**

| **Campo** | **Descripción**                                                                              |
| ---------- | ---------------------------------------------------------------------------------------------- |
| Como       | Encargado de inventario de la tienda                                                           |
| Quiero     | Registrar, consultar, modificar, dar de baja y listar artículos de la NBA                      |
| Para       | Mantener un control exacto del stock disponible y organizar el catálogo de productos de forma eficiente |

## **2. Modelo de Clases del Sistema**

A diferencia del TP1 (donde todo era un único record `TProducto`), en esta versión el dominio se modela con una jerarquía de clases. El sistema incluye:

#### **2.1 Clase abstracta Persona**

Clase base con los atributos comunes a Trabajadores y Clientes. No se instancia directamente (hereda de `Serializable`, que a su vez hereda de `ABC`).

| **Atributo** | **Tipo** | **Descripción**            |
| ------------- | --------- | ---------------------------- |
| _dni          | int       | Documento de identidad (privado) |
| _nombre       | str       | Nombre completo (privado)   |
| _edad         | int       | Edad de la persona (privado) |

El acceso a estos atributos se expone mediante `@property` con validación en cada setter (por ejemplo, el DNI debe estar entre 1.000.000 y 99.999.999, el nombre debe tener más de 2 caracteres). El método `descripcion()` está decorado con `@abstractmethod`: `Persona` no puede instanciarse directamente y cada subclase está obligada a implementar su propia versión (equivalente funcional a lanzar `NotImplementedError` desde la clase base).

#### **2.2 Clase Cliente (hereda de Persona)**

| **Atributo**  | **Tipo** | **Descripción**                              |
| -------------- | --------- | ---------------------------------------------- |
| _email         | str       | Correo electrónico de contacto                |
| _tipo_cliente  | str       | 'Minorista' o 'Mayorista'                     |

Expone además la propiedad calculada `descuento`, que devuelve 15% si el cliente es Mayorista y 0% si es Minorista.

#### **2.3 Clase Trabajador (hereda de Persona)**

| **Atributo** | **Tipo** | **Descripción**                  |
| ------------- | --------- | ----------------------------------- |
| _legajo       | int       | Número de legajo interno            |
| _cargo        | str       | Puesto que ocupa (ej. 'Vendedor')  |
| _salario      | float     | Salario mensual                    |

#### **2.4 Clase Producto**

| **Atributo**   | **Tipo** | **Descripción**                          |
| --------------- | --------- | ------------------------------------------- |
| _codigo         | int       | Identificador único, asignado automáticamente |
| _descripcion    | str       | Nombre/descripción del artículo             |
| _precio         | float     | Precio unitario                             |
| _stock          | int       | Cantidad disponible en inventario           |

#### **2.5 Clase OrdenCompra**

Equivalente a un comprobante de venta: vincula un `Cliente`, un `Trabajador` y una lista de artículos comprados.

| **Atributo**    | **Tipo**         | **Descripción**                                  |
| ---------------- | ----------------- | --------------------------------------------------- |
| _numero          | int               | Identificador único, asignado automáticamente       |
| dni_cliente      | int               | DNI del cliente asociado                            |
| dni_trabajador   | int               | DNI del trabajador que atendió la venta             |
| fecha            | str               | Fecha y hora de la orden (asignada automáticamente) |
| _items           | List[ItemOrden]   | Líneas de la orden (producto + cantidad)            |

Cada `ItemOrden` guarda el código, descripción y precio del producto en el momento de la venta, además de la cantidad pedida, y expone la propiedad calculada `subtotal`.

#### **2.6 Clase GestorSistema**

Clase que encapsula las colecciones de productos, clientes, trabajadores y órdenes, y todas las operaciones del CRUD. Internamente usa diccionarios (`{clave: objeto}`) para poder buscar por código/DNI/número en O(1).


## **3. Requerimientos Funcionales (CRUD)**

#### **3.1 Alta - Registrar Producto / Cliente / Trabajador**

- `agregar_producto()` crea un nuevo `Producto` y le asigna automáticamente un código correlativo único.
- `agregar_cliente()` / `agregar_trabajador()` crean una `Cliente`/`Trabajador` a partir de un DNI que no debe estar ya registrado (si lo está, se lanza `PersonaDuplicada`).
- No se aceptan campos vacíos ni inválidos: la validación de cada setter lanza `ErrorValidacion` en vez de simplemente imprimir un mensaje.
- El stock inicial de un producto nuevo puede ser 0 o mayor.

#### **3.2 Consulta - Buscar Producto**

- `buscar_producto_por_codigo()` permite buscar un producto por su código.
- `buscar_producto_por_descripcion()` permite buscar un producto por su nombre exacto.
- Si no se encuentra ningún resultado, se lanza `ProductoNoEncontrado`, capturada en el menú (`main.py`) o en la interfaz gráfica (`gui.py`), mostrando un mensaje claro al usuario.
- Los datos del producto encontrado se muestran con formato legible delegado al propio objeto, mediante `__str__()`.

#### **3.3 Modificación - Editar Producto**

- `editar_producto()` permite modificar descripción, precio y/o stock de un producto existente.
- El código del producto no puede modificarse: no existe ningún método que permita cambiarlo una vez creado.
- `descontar_stock()` es la operación específica para restar unidades por una venta; lanza `StockInsuficiente` si la cantidad pedida supera el stock disponible.

#### **3.4 Baja - Eliminar Producto / Cliente / Trabajador**

- `eliminar_producto()`, `eliminar_cliente()` y `eliminar_trabajador()` piden confirmación en la interfaz (popup `sg.popup_yes_no` en la GUI) antes de ejecutarse.
- Si el DNI/código no existe, se lanza `PersonaNoEncontrada` o `ProductoNoEncontrado` según corresponda.


#### **3.5 Listado - Ver Todos los Productos / Personas / Órdenes**

- `listar_productos()`, `listar_clientes()`, `listar_trabajadores()` y `listar_ordenes()` muestran todos los registros en formato de tabla (por consola en `main.py`, o en un `sg.Table` en `gui.py`).
- Los listados usan `sorted()` con `key=lambda` para ordenar (productos por código, clientes por nombre, trabajadores por legajo, órdenes por número).
- Si la colección está vacía, se informa "No hay productos/personas/órdenes registrados/as".

## **4. Requisitos de Diseño Orientado a Objetos**

#### **4.1 Encapsulamiento**

- Todos los atributos de `Persona`, `Cliente`, `Trabajador`, `Producto`, `OrdenCompra` e `ItemOrden` son privados (prefijo `_`).
- El acceso externo se hace mediante `@property` y sus respectivos setters con validación.
- **Pendiente:** las colecciones internas de `GestorSistema` deben pasar a ser privadas (ver nota en el punto 2.6) para cumplir este requisito de punta a punta.

#### **4.2 Herencia**

- `Cliente` y `Trabajador` heredan de `Persona`, reutilizando `_dni`, `_nombre`, `_edad` y sus validaciones.
- Ambos constructores usan `super().__init__(dni, nombre, edad)` antes de inicializar sus atributos propios.

#### **4.3 Polimorfismo**

- El método `descripcion()` se comporta de forma distinta según el tipo de objeto que lo invoca: un `Cliente` devuelve `"[Cliente Mayorista] Ana Perez - DNI ... - email"` mientras que un `Trabajador` devuelve `"[Trabajador] Legajo ... - Nombre (Cargo) - DNI ..."`.
- En `menu_listar_personas()` (`main.py`) y en la tabla de personas de la GUI, se recorren clientes y trabajadores mezclados en una misma lista y se les llama `.descripcion()` sin distinguir el tipo — cada objeto responde según su propia clase.
- Para la defensa: en Pascal estructurado esto se resolvería con un `case` o `if` explícito comprobando un campo "tipo" antes de decidir qué imprimir; en POO, el propio objeto decide su comportamiento sin que quien lo invoca necesite saber de qué clase es.

#### **4.4 Manejo de excepciones**

Excepciones propias definidas en `excepts.py`, todas heredadas de `ErrorSistema(Exception)`:

- `ErrorValidacion` — dato inválido en un setter.
- `ProductoNoEncontrado` — búsqueda de producto sin resultado.
- `StockInsuficiente` — se pide descontar más stock del disponible.
- `LimiteProductosAlcanzado` — se alcanzó el máximo de productos permitidos.
- `PersonaNoEncontrada` — búsqueda de cliente/trabajador sin resultado.
- `PersonaDuplicada` — alta de una persona con un DNI ya registrado.
- `OrdenSinItems` — se intenta confirmar una orden sin productos cargados.
- `OrdenNoEncontrada` — búsqueda de orden por número sin resultado.
- `ErrorPersistencia` — falla al leer o escribir un archivo JSON.

Tanto `main.py` como `gui.py` capturan estas excepciones con `try/except ErrorSistema` y muestran el mensaje al usuario (por consola o con `sg.popup_error`), sin que el programa se caiga ante una entrada inválida.

#### **4.5 Persistencia**

Guardado y carga automática en cuatro archivos JSON independientes: `productos.json`, `clientes.json`, `trabajadores.json` y `ordenes.json`. Cada clase implementa `to_dict()`/`from_dict()` (interfaz `Serializable`), y `GestorSistema` los usa para serializar/deserializar sin que el resto del programa conozca el formato de archivo.

## **5. Criterios de Aceptación**

| **Operación** | **Escenario**          | **Acción / Entrada**                         | **Resultado Esperado**                                  |
| -------------- | ------------------------ | ----------------------------------------------- | ----------------------------------------------------------- |
| Alta           | Producto válido          | Todos los campos completos                      | Producto creado con código único                            |
| Alta           | Campo vacío               | Intentar guardar sin descripción                | Se lanza `ErrorValidacion`, no se guarda                   |
| Alta           | Cliente/Trabajador duplicado | Registrar un DNI ya existente                | Se lanza `PersonaDuplicada`, no se guarda                  |
| Consulta       | Código existente          | Buscar por código válido                        | Muestra todos los datos del producto                        |
| Consulta       | Código inexistente        | Buscar código que no existe                     | Se lanza `ProductoNoEncontrado`, mensaje claro              |
| Modificación   | Stock suficiente          | Descontar stock dentro del disponible           | Stock actualizado correctamente                             |
| Modificación   | Stock insuficiente        | Descontar más stock del disponible              | Se lanza `StockInsuficiente`                                |
| Baja           | Con confirmación          | Confirmar eliminación                           | El registro se elimina de la colección y del JSON          |
| Baja           | Registro inexistente      | Intentar eliminar un código/DNI que no existe   | Se rechaza con excepción/mensaje claro                       |
| Listado        | Sin registros             | Listar con colección vacía                      | Mensaje: 'No hay productos/personas/órdenes registrados/as' |
| Listado        | Con registros             | Listar con datos cargados                       | Tabla ordenada, con posibilidad de recorrerla completa       |

## **6. Estructura del Programa Requerida**

| **Elemento**                                                                          | **Tipo Python**                | **Responsabilidad**                                             |
| ---------------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------- |
| `Persona`                                                                              | Clase abstracta (`ABC`)          | Atributos y comportamiento común a clientes y trabajadores          |
| `Cliente`                                                                              | Clase (hereda de `Persona`)      | Representa a un cliente de la tienda                                |
| `Trabajador`                                                                           | Clase (hereda de `Persona`)      | Representa a un empleado de la tienda                               |
| `Producto`                                                                             | Clase                              | Representa un artículo del inventario                               |
| `OrdenCompra` / `ItemOrden`                                                            | Clase                              | Representa una venta y sus líneas de detalle                       |
| `GestorSistema`                                                                        | Clase                              | Encapsula las colecciones y el CRUD completo, con persistencia JSON |
| `ErrorValidacion`, `ProductoNoEncontrado`, `StockInsuficiente`, `PersonaNoEncontrada`, `PersonaDuplicada`, `OrdenSinItems`, `OrdenNoEncontrada`, `ErrorPersistencia` | Clases de excepción (`Exception`) | Errores de negocio propios del dominio                              |
| `menu_principal()`                                                                     | Función (`main.py`)               | Imprime el menú principal por consola y contiene el bucle del menú |
| `main()`                                                                                | Función (`gui.py`)                | Punto de entrada de la interfaz gráfica (PySimpleGUI)               |

## **7. Interfaz Gráfica**

Además de la versión por consola (`main.py`), el grupo desarrolló una interfaz gráfica con **PySimpleGUI** (`gui.py`) que reutiliza `GestorSistema` sin duplicar lógica de negocio: cuatro pestañas (Productos, Clientes, Trabajadores, Órdenes de Compra), tablas con los listados y ventanas modales para alta/edición/baja, todas con manejo de las mismas excepciones propias mostradas mediante `sg.popup_error()`.

## **8. Presentación en Clase**

Durante la defensa, el grupo deberá:

- Ejecutar el programa en vivo (por consola y/o con la interfaz gráfica), sin errores, mostrando el CRUD completo con datos de prueba preparados con anticipación.
- Mostrar en el código dónde está aplicado cada pilar de la POO pedido: encapsulamiento, herencia y polimorfismo.
- Mostrar al menos un caso de excepción manejada en vivo (campo vacío, código/DNI inexistente, stock insuficiente, etc.).
- Explicar una decisión de diseño propia del grupo: por qué modelaron las clases de esa forma, qué alternativas consideraron (por ejemplo, por qué `Producto` no hereda de `Persona`, o por qué se separó `ItemOrden` de `OrdenCompra`).
- Responder una pregunta comparativa del docente sobre las diferencias entre esta solución y la del TP1 en Pascal (por ejemplo: ¿qué pasaba en Pascal cuando querían diferenciar el comportamiento de un Cliente y un Trabajador? ¿Cómo se resuelve eso ahora con `descripcion()`?).
- Responder preguntas del docente sobre cualquier parte del código.

_Nota: cada integrante debe poder explicar cualquier parte del código, no solo la parte que escribió. Se espera además que puedan argumentar, con sus palabras, por qué el mismo problema de negocio se resuelve distinto en un paradigma estructurado y en uno orientado a objetos._