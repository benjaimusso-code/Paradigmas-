Program Proc_tp1;

{$codepage UTF8}

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

function Validar_Numero(const s: string): boolean;
var
  i: integer;
begin
  if s <> '' then
  begin
    for i := 1 to Length(s) do
      if (s[i]<>'0') and (s[i]<>'1') and (s[i]<>'2') and (s[i]<>'3') and (s[i]<>'4') and (s[i]<>'5') and (s[i]<>'6') and (s[i]<>'7') and (s[i]<>'8') and (s[i]<>'9') and (s[i]<>'.') and (s[i]<>',') then
      begin
        Validar_Numero := false;
        exit;
      end;
    Validar_Numero := true;
  end
  else
    Validar_Numero := false;
end;

function LeerReal(const mensaje: string): real;
var
  entrada: string;
  valor: real;
  codigo: integer;
begin
  repeat
    write(mensaje);
    readln(entrada);
    if not Validar_Numero(entrada) then
      writeln('Entrada invalida. Ingrese un numero.')
    else
      Val(entrada, valor, codigo);
  until Validar_Numero(entrada);
  LeerReal := valor;
end;

function LeerEntero(const mensaje: string): integer;
var
  entrada: string;
  valor: integer;
  codigo: integer;
begin
  repeat
    write(mensaje);
    readln(entrada);
    Val(entrada, valor, codigo);
    if codigo <> 0 then
      writeln('Entrada invalida. Ingrese un numero entero.');
  until codigo = 0;
  LeerEntero := valor;
end;

function EsDescripcionValida(const s: string): boolean;
var
  i: integer;
begin
  EsDescripcionValida := false;
  for i := 1 to Length(s) do
    if s[i] <> ' ' then
    begin
      EsDescripcionValida := true;
      exit;
    end;
end;

function BuscarPorDescripcion: longint;
var
  descripcionBuscada: string;
  posicion: longint;
begin
  write('Ingrese la descripcion del producto a buscar: '); readln(descripcionBuscada);
  descripcionBuscada := LimpiarTildes_y_Mayusculas(descripcionBuscada);
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}
  if IOResult <> 0 then
  begin
    writeln('No hay productos cargados en el inventario.');
    BuscarPorDescripcion := -1;
    exit;
  end;

  posicion := -1;
  while not eof(archivo) do
  begin
    read(archivo, producto);
    if LimpiarTildes_y_Mayusculas(producto.descripcion) = descripcionBuscada then
    begin
      posicion := FilePos(archivo) - 1;
      writeln('Producto encontrado:');
      writeln('Codigo: ', producto.codigo);
      writeln('Descripcion: ', Minusculas(producto.descripcion));
      writeln('Precio: ', producto.precio:0:2);
      writeln('Stock: ', producto.stock);
      break;
    end;
  end;

  if posicion = -1 then
  begin
    writeln('Producto no encontrado.');
    close(archivo);
  end;

  BuscarPorDescripcion := posicion;
end;

procedure NuevoProducto;
var
  ultimoID: integer;
begin
  LimpiarPantalla;
  LineaSeparacion;
  writeln('=== Agregar Producto ===');
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

  if ultimoID < MAX_PRODUCTOS then
  begin
    producto.codigo := ultimoID + 1;
    writeln('Codigo asignado automaticamente: ', producto.codigo);

    repeat
      write('Descripcion: '); readln(producto.descripcion);
      if not EsDescripcionValida(producto.descripcion) then
        writeln('Descripcion invalida. No puede ser vacia o solo espacios.');
    until EsDescripcionValida(producto.descripcion);

    repeat
      producto.precio := LeerReal('Precio: ');
    until producto.precio > 0;

    repeat
      producto.stock := Round(LeerReal('Stock: '));
    until producto.stock >= 0;

    write(archivo, producto);
    close(archivo);
    writeln('Producto agregado correctamente.');
    writeln('Presione Enter para continuar');
  end
  else
  begin
    writeln('Se ha alcanzado el limite maximo de productos: (', MAX_PRODUCTOS, ').');
    close(archivo);
  end;
end;

Procedure BuscarPorCodigo;
var
  codigoBuscado: integer;
  encontrado: boolean;
begin
  codigoBuscado := LeerEntero('Ingrese el codigo del producto a buscar: ');
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}
  if IOResult <> 0 then
  begin
    writeln('No hay productos cargados en el inventario.');
    exit;
  end;

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

Procedure BuscarProducto;
var
  opcionBusqueda: integer;
begin
  LimpiarPantalla;
  LineaSeparacion;
  writeln('=== Buscar Producto ===');
  repeat
    writeln('Seleccione el criterio de busqueda:');
    writeln('1. Buscar por codigo');
    writeln('2. Buscar por descripcion');
    opcionBusqueda := LeerEntero('Opcion: ');
    if (opcionBusqueda <> 1) and (opcionBusqueda <> 2) then
      writeln('Opcion invalida. Ingrese 1 o 2.');
  until (opcionBusqueda = 1) or (opcionBusqueda = 2);

  case opcionBusqueda of
    1: BuscarPorCodigo;
    2: begin
         if BuscarPorDescripcion = -1 then
           writeln('Busqueda finalizada.')
         else
           close(archivo);
       end;
  end;
  writeln('Presione Enter para continuar');
  readln;
end;

Procedure ListarProducto;
begin
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}
  if IOResult <> 0 then
  begin
    writeln('No hay productos cargados en el inventario.');
    writeln('Presione Enter para continuar');
    readln;
    exit;
  end;
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
  writeln('Presione Enter para continuar');
  readln;
end;

Procedure EditarProducto;
var
  op: integer;
  confirmacion: string;
  posicion: longint;
begin
  LimpiarPantalla;
  LineaSeparacion;
  writeln('=== Editar Producto ===');
  posicion := BuscarPorDescripcion;

  if posicion < 0 then
  begin
    writeln('No se puede editar: Producto no encontrado.');
    writeln('Presione Enter para continuar');
    readln;
    exit;
  end;

  repeat
    write('Desea editar este producto? (s/n): '); readln(confirmacion);
    confirmacion := Minusculas(confirmacion);
    if (confirmacion <> 's') and (confirmacion <> 'n') then
      writeln('Opcion invalida. Ingrese s o n.');
  until (confirmacion = 's') or (confirmacion = 'n');

  if confirmacion = 'n' then
  begin
    writeln('Saliendo sin realizar cambios');
    close(archivo);
    writeln('Presione Enter para continuar');
    readln;
    exit;
  end;

  repeat
    writeln('--- Menu de Edicion ---');
    writeln('1. Descripcion');
    writeln('2. Precio');
    writeln('3. Stock');
    writeln('0. Salir sin editar');
    op := LeerEntero('Opcion: ');
    case op of
      1: repeat
           write('Ingrese la nueva descripcion: '); readln(producto.descripcion);
           if not EsDescripcionValida(producto.descripcion) then
             writeln('Descripcion invalida. No puede ser vacia o solo espacios.');
         until EsDescripcionValida(producto.descripcion);
      2: repeat
           producto.precio := LeerReal('Ingrese el nuevo precio: ');
         until producto.precio > 0;
      3: repeat
           producto.stock := Round(LeerReal('Ingrese el nuevo stock: '));
         until producto.stock >= 0;
      0: writeln('Saliendo sin realizar cambios');
      else writeln('Opcion invalida.');
    end;
  until (op >= 0) and (op <= 3);

  if (op >= 1) and (op <= 3) then
  begin
    seek(archivo, posicion);
    write(archivo, producto);
    writeln('Producto actualizado con exito.');
  end;

  close(archivo);
  writeln('Presione Enter para continuar');
  readln;
end;

Procedure EliminarProducto;
var
  descripcionBuscada: string;
  encontrado: boolean;
  stockActual, stockaEliminar: integer;
begin
  LimpiarPantalla;
  LineaSeparacion;
  writeln('=== Eliminar Producto (Bajar Stock) ===');
  write('Ingrese la descripcion del producto: '); readln(descripcionBuscada);
  descripcionBuscada := LimpiarTildes_y_Mayusculas(descripcionBuscada);
  assign(archivo, NOMBRE_ARCHIVO);
  {$I-} reset(archivo); {$I+}
  if IOResult <> 0 then
  begin
    writeln('No hay productos cargados en el inventario.');
    writeln('Presione Enter para continuar');
    readln;
    exit;
  end;

  encontrado := false;
  while not eof(archivo) do
  begin
    read(archivo, producto);
    if LimpiarTildes_y_Mayusculas(producto.descripcion) = descripcionBuscada then
    begin
      encontrado := true;
      stockaEliminar := LeerEntero('Ingrese la cantidad a eliminar del stock: ');
      stockActual := producto.stock;
      if (stockActual >= stockaEliminar) and (stockaEliminar > 0) then
      begin
        producto.stock := stockActual - stockaEliminar;
        seek(archivo, FilePos(archivo) - 1);
        write(archivo, producto);
        writeln('Stock actualizado.');
      end
      else writeln('Error: Stock insuficiente o cantidad invalida.');
      break;
    end;
  end;
  if not encontrado then writeln('Producto no encontrado.');
  close(archivo);
  writeln('Presione Enter para continuar');
  readln;
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
    opcion := LeerEntero('Opcion: ');

    case opcion of
      1: NuevoProducto;
      2: BuscarProducto;
      3: ListarProducto;
      4: EliminarProducto;
      5: EditarProducto;
      0: writeln('Fin del Programa.');
      else
      begin
        writeln('Opcion invalida.');
        writeln('Presione Enter para continuar');
        readln;
      end;
    end;
  until opcion = 0;
end.
