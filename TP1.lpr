Program Proc_tp1;

{$codepage UTF8} { Ayuda al compilador con los acentos}

uses crt, sysutils;

const
    MAX_PRODUCTOS = 100;
    NOMBRE_ARCHIVO = 'inventario.dat';

type 
    TProducto = record
        codigo: integer;
        descripcion: string[50];
        precio: real;
        stock: integer;
    end;

var
    producto: TProducto;
    archivo: file of TProducto;
    opcion: integer;

Procedure LimpiarPantalla;
begin
  ClrScr;
end;

Procedure LineaSeparacion;
var
  i, ancho: integer;
begin
  ancho := Lo(WindMax) + 1; 
  writeln;
  for i := 1 to ancho do
    write('-');
  writeln;
end;

function LimpiarTildes_y_Mayusculas(const s: string): string;
var
  i: integer;
  res: string;
  c: string;
begin
  res := '';
  for i := 1 to Length(s) do
  begin
    c := UpCase(s[i]);
    if (s[i] = 'á') or (s[i] = 'à') or (s[i] = 'ä') or (s[i] = 'â') then res := res + 'A'
    else if (s[i] = 'é') or (s[i] = 'è') or (s[i] = 'ë') or (s[i] = 'ê') then res := res + 'E'
    else if (s[i] = 'í') or (s[i] = 'ì') or (s[i] = 'ï') or (s[i] = 'î') then res := res + 'I'
    else if (s[i] = 'ó') or (s[i] = 'ò') or (s[i] = 'ö') or (s[i] = 'ô') then res := res + 'O'
    else if (s[i] = 'ú') or (s[i] = 'ù') or (s[i] = 'ü') or (s[i] = 'û') then res := res + 'U'
    else if (s[i] = 'ñ') or (s[i] = 'Ñ') then res := res + 'N'
    else res := res + UpCase(s[i]);
  end;
  LimpiarTildes_y_Mayusculas := res;
end;

function Minusculas(const s: string): string;
var
  i: integer;
  res: string;
begin
  res := '';
  for i := 1 to Length(s) do
    res := res + LowerCase(s[i]);
  Minusculas := res;
end;

procedure NuevoProducto;
var
  ultimoID: integer;
begin
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}

  if IOResult <> 0 then
  begin
    rewrite(archivo);
    ultimoID := 0;
  end
  else
  begin
    if FileSize(archivo) > 0 then
    begin
      seek(archivo, FileSize(archivo) - 1);
      read(archivo, producto);
      ultimoID := producto.codigo;
    end
    else
      ultimoID := 0;
    seek(archivo, FileSize(archivo));
  end;

  producto.codigo := ultimoID + 1;
  writeln('Codigo asignado automaticamente: ', producto.codigo);

  repeat
    write('Descripcion: '); readln(producto.descripcion);
  until producto.descripcion <> '';

  repeat
    write('Precio: '); readln(producto.precio);
  until producto.precio > 0;

  repeat
    write('Stock: '); readln(producto.stock);
  until producto.stock >= 0;

  write(archivo, producto);
  close(archivo);
  writeln('Producto agregado correctamente.');
  writeln('Presione Enter para continuar...');

end;

Procedure BuscarPorCodigo;
var
  codigoBuscado: integer;
  encontrado: boolean;
begin
  write('Ingrese el codigo del producto a buscar: '); readln(codigoBuscado);
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}
  if IOResult <> 0 then exit;

  encontrado := false;
  while not eof(archivo) do
  begin
    read(archivo, producto);
    if producto.codigo = codigoBuscado then
    begin
      encontrado := true;
      writeln('Producto encontrado:');
      writeln('Codigo: ', producto.codigo);
      writeln('Descripcion: ', producto.descripcion);
      writeln('Precio: ', producto.precio:0:2);
      writeln('Stock: ', producto.stock);
    end;
  end;
  close(archivo);
  if not encontrado then writeln('Producto no encontrado.');
end;

Procedure BuscarPorDescripcion;
var
  descripcionBuscada: string;
  encontrado: boolean;
begin
  write('Ingrese la descripcion del producto a buscar: '); readln(descripcionBuscada);
  descripcionBuscada := LimpiarTildes_y_Mayusculas(descripcionBuscada);
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}
  if IOResult <> 0 then exit;

  encontrado := false;
  while not eof(archivo) do
  begin
    read(archivo, producto);
    if LimpiarTildes_y_Mayusculas(producto.descripcion) = descripcionBuscada then
    begin
      encontrado := true;
      writeln('Producto encontrado:');
      writeln('Codigo: ', producto.codigo);
      writeln('Descripcion: ', Minusculas(producto.descripcion));
      writeln('Precio: ', producto.precio:0:2);
      writeln('Stock: ', producto.stock);
    end;
  end;
end;

Procedure BuscarProducto;
var
  opcionBusqueda: integer;
begin
  writeln('Seleccione el criterio de busqueda:');
  writeln('1. Buscar por codigo');
  writeln('2. Buscar por descripcion');
  write('Opcion: '); readln(opcionBusqueda);
  case opcionBusqueda of
    1: BuscarPorCodigo;
    2: begin BuscarPorDescripcion; close(archivo); end;
    else writeln('Opcion invalida.');
  end;
    writeln('Presione Enter para continuar...');
end;

Procedure ListarProducto;
begin
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}
  if IOResult <> 0 then exit;
  LimpiarPantalla;
  LineaSeparacion;
  writeln('=== Inventario ===');
  while not eof(archivo) do
  begin
    read(archivo, producto);
    writeln('Codigo       : ', producto.codigo);
    writeln('Descripcion  : ', producto.descripcion);
    writeln('Precio       : $', producto.precio:0:2);
    writeln('Stock        : ', producto.stock, ' unidades');
    writeln;
  end;
  close(archivo);
  writeln('Presione Enter para continuar...');
end;

Procedure EditarProducto;
var 
  edit: string;
  op: integer;
  posicion: longint;
begin
  BuscarPorDescripcion;
  posicion := FilePos(archivo) - 1;
  if (posicion < 0) then 
  begin
     writeln('No se puede editar: Producto no encontrado.');
     close(archivo);
     exit;
     writeln('Presione Enter para continuar...');

  end;

  repeat
    writeln('--- Menu de Edicion ---');
    writeln('1. Descripcion');
    writeln('2. Precio');
    writeln('3. Stock');
    writeln('0. Salir sin editar');
    write('Opcion: '); readln(op);
    case op of
      1: repeat
           write('Ingrese la nueva descripcion: '); readln(producto.descripcion);
         until producto.descripcion <> '';
      2: repeat
           write('Ingrese el nuevo precio: '); readln(producto.precio);
         until producto.precio > 0;
      3: repeat
           write('Ingrese el nuevo stock: '); readln(producto.stock);
         until producto.stock >= 0;
      0: writeln('Saliendo sin realizar cambios...');
    end;
  until (op >= 0) and (op <= 3);

  if (op >= 1) and (op <= 3) then
  begin
    seek(archivo, posicion);
    write(archivo, producto);
    writeln('Producto actualizado con exito.');
  end;
  close(archivo);
end;

Procedure EliminarProducto;
var
  descripcionBuscada: string;
  encontrado: boolean;
  stockActual, stockaEliminar: integer;
begin
  write('Ingrese la descripcion del producto: '); readln(descripcionBuscada);
  descripcionBuscada := LimpiarTildes_y_Mayusculas(descripcionBuscada);
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}
  if IOResult <> 0 then exit;

  encontrado := false;
  while not eof(archivo) do
  begin
    read(archivo, producto);
    if LimpiarTildes_y_Mayusculas(producto.descripcion) = descripcionBuscada then
    begin
      encontrado := true;
      write('Ingrese la cantidad a eliminar del stock: '); readln(stockaEliminar);
      stockActual := producto.stock;
      if (stockActual >= stockaEliminar) and (stockaEliminar > 0) then
      begin
        producto.stock := stockActual - stockaEliminar;
        seek(archivo, FilePos(archivo) - 1);
        write(archivo, producto);
        writeln('Stock actualizado.');
      end
      else writeln('Error: Stock insuficiente.');
      break;
    end;
  end;
  if not encontrado then writeln('Producto no encontrado.');
  close(archivo);
end;

begin
  repeat
    LimpiarPantalla;
    LineaSeparacion;
    writeln('-------- Menu de Opciones ------');
    writeln('1. Agregar Producto');
    writeln('2. Buscar Producto');
    writeln('3. Listar Producto');
    writeln('4. Eliminar Producto (Bajar Stock)');
    writeln('5. Editar Producto ');
    writeln('0. Salir');
    write('Opcion: '); readln(opcion);

    case opcion of
      1: NuevoProducto;
      2: BuscarProducto;
      3: ListarProducto;
      4: EliminarProducto;
      5: EditarProducto;
      0: writeln('Fin del Programa.');
    end;
    if opcion <> 0 then readln;
  until opcion = 0;
end.
