Program Proc_tp1;

type 
    TProducto = record  {Se define la clase producto}
        codigo: integer;  {Cada uno es un atributo de la clase}
        descripcion: string[50];
        precio: real;
        stock: integer;
    end;

var
    producto: TProducto;  {Se declara una variable de tipo producto}
    archivo: file of TProducto;  {Se declara un archivo de tipo producto}
    opcion: integer;  {Variable para almacenar la opcion del menu}

procedure NuevoProducto;  {Procedimiento para agregar un nuevo producto al inventario}

begin
    while not eof(archivo) do  {Se recorre el archivo para encontrar el ultimo codigo registrado}
    begin
        read(archivo, producto);  {Se lee el producto del archivo}
        if filesize(archivo) = 0 then  {Si el archivo esta vacio, se asigna el codigo 1 al nuevo producto}
            producto.codigo := 1
        else
            producto.codigo := producto.codigo + 1;  {Si el archivo no esta vacio, se asigna el codigo del ultimo producto + 1 al nuevo producto}
        
    end;
  write('Descripcion: '); readln(producto.descripcion);  {Se solicita la descripcion del producto}
  write('Precio: '); readln(producto.precio);  {Se solicita el precio del producto}
  write('Stock: '); readln(producto.stock);  {Se solicita el stock del producto}

  assign(archivo, 'inventario.dat');  {Se asigna el archivo al que se va a escribir}
  {$I-}  {Se deshabilitan los mensajes de error}
  reset(archivo);  {Se intenta abrir el archivo para lectura}
  {$I+}  {Se vuelven a habilitar los mensajes de error}

  if IOResult <> 0 then  {Si el archivo no existe o no se pudo abrir}
    rewrite(archivo)  {Se crea un nuevo archivo}
  else
    seek(archivo, filesize(archivo));  {Si el archivo existe, se posiciona al final para agregar el nuevo producto}

  write (archivo, producto);  {Se escribe el nuevo producto en el archivo}
  close(archivo);  {Se cierra el archivo}
  writeln('Producto agregado correctamente.');  {Mensaje de confirmacion}
end;

Procedure BuscarProducto;  {Procedimiento para buscar un producto por su codigo}
var
  codigoBuscado: integer;  {Variable para almacenar el codigo a buscar}
  encontrado: boolean;  {Variable para indicar si se encontro el producto}
begin
  write('Ingrese el codigo del producto a buscar: '); readln(codigoBuscado);  {Se solicita el codigo a buscar}

  assign(archivo, 'inventario.dat');  {Se asigna el archivo para lectura}
  {$I-}  {Se deshabilitan los mensajes de error}
  reset(archivo);  {Se intenta abrir el archivo para lectura}
  {$I+}  {Se vuelven a habilitar los mensajes de error}

  If IOResult <> 0 then  {Si el archivo no existe o no se pudo abrir}
  begin
    writeln('El inventario esta vacio.');  {Mensaje de error}
    exit;  {Se sale del procedimiento}
  end;

  encontrado := false;  {Se inicializa la variable de encontrado}
  while not eof(archivo) do  {Mientras no se llegue al final del archivo}

begin

end;