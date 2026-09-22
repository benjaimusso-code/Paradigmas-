class ErrorSistema(Exception):
    pass

class ErrorValidacion(ErrorSistema):
    """Se lanza cuando un dato no cumple las reglas de validacion (setters)."""
    pass

class ProductoNoEncontrado(ErrorSistema):
    """Se lanza cuando se busca un producto por codigo o descripcion y no existe."""
    pass

class StockInsuficiente(ErrorSistema):
    """Se lanza cuando se intenta descontar mas stock del disponible."""
    pass

class LimiteProductosAlcanzado(ErrorSistema):
    """Se lanza cuando se alcanza el maximo de productos permitidos."""
    pass

class PersonaNoEncontrada(ErrorSistema):
    """Se lanza cuando se busca una persona (cliente o trabajador) por DNI y no existe."""
    pass

class PersonaDuplicada(ErrorSistema):
    """Se lanza cuando se intenta registrar una persona con un DNI ya existente."""
    pass

class OrdenSinItems(ErrorSistema):
    """Se lanza cuando se intenta cerrar/guardar una orden de compra sin items cargados."""
    pass

class OrdenNoEncontrada(ErrorSistema):
    """Se lanza cuando se busca una orden de compra por numero y no existe."""
    pass

class ErrorPersistencia(ErrorSistema):
    """Se lanza ante problemas al leer o escribir los archivos JSON."""
    pass
