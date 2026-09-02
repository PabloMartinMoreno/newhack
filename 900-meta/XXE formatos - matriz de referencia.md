---
tipo: meta
aliases:
  - Formatos XXE
  - Dónde nace un XXE
tags:
  - meta/referencia
  - dominio/web
---

# XXE formatos - matriz de referencia

> [!info] Referencia pura, no un zettel
> Catálogo de dónde hay un parser de XML esperando. El criterio de qué canal usar está en [[MOC - XXE]]. Matriz de reconocimiento: se recorre buscando, no se lee de corrido.

## 1. XML explícito

Lo evidente, y donde ya buscan todos.

```http
Content-Type: application/xml
Content-Type: text/xml
Content-Type: application/soap+xml
Content-Type: application/atom+xml
```

Endpoints SOAP heredados, APIs viejas, feeds RSS y Atom, sitemaps, XML-RPC. Los servicios SOAP son el terreno más fértil del dominio: son viejos por definición, y su antigüedad es exactamente lo que correlaciona con parsers sin endurecer.

## 2. Cambio de tipo de contenido

La superficie que más paga y la que menos se prueba.

Una API que espera JSON puede tener detrás un framework que **también** acepta XML. Se manda el mismo dato reescrito y con `Content-Type: application/xml`:

```json
{"nombre": "x"}
```

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><nombre>&xxe;</nombre></root>
```

Si el framework deserializa por tipo de contenido y nadie pensó en el caso XML, el endpoint entero es vulnerable sin que exista una sola línea de código que mencione XML.

Vale probarlo en **todo** endpoint que acepte un cuerpo estructurado. Cuesta una petición.

## 3. Formatos que son XML por dentro

Ninguno parece XML. Todos lo son.

| Formato | Dónde vive el XML | Cómo se prueba |
|---|---|---|
| SVG | El archivo entero | Subida de avatar, imagen, logo |
| DOCX · XLSX · PPTX | Un ZIP con XML adentro | Editar `word/document.xml`, recomprimir |
| ODT · ODS | Ídem, formato abierto | `content.xml` |
| PDF | Metadatos XMP | Conversores y extractores de metadatos |
| JPEG · TIFF | Metadatos XMP | Procesadores de imagen |
| PLIST | Configuración de Apple | Importadores |
| XLIFF · TMX | Traducción | Herramientas de localización |
| KML · GPX | Geodatos | Cualquier cosa con mapas |

El vector común es **la subida de archivos**: ver [[File upload - XXE por archivo]] para el criterio y [[MOC - File upload]] para el dominio. Es el punto donde los dos dominios se cruzan.

SVG merece mención aparte porque tiene dos caminos distintos que no hay que confundir: XXE por el parser, y [[File upload - SVG y XSS almacenado]] por el navegador que lo renderiza después. Son vulnerabilidades separadas en el mismo archivo.

## 4. Protocolos de identidad

Terreno de alto valor, porque el XML va firmado y por eso nadie sospecha de él.

**SAML.** La aserción es XML y el proveedor de servicio la parsea. La firma se verifica **después** de parsear, así que el XXE ocurre antes de que la validación de firma tenga oportunidad de rechazar nada.

**Metadatos de federación.** Las URL de metadatos de SAML e importadores de configuración de proveedores de identidad procesan XML de una fuente que a veces controla el usuario.

**WS-Security y WS-Federation.** SOAP con XML anidado y firmado, en productos viejos.

## 5. Superficies indirectas

Donde el XML aparece del lado del servidor y el atacante nunca lo ve. Es el terreno de [[XXE - XInclude]].

- Un parámetro que la app inserta en una petición SOAP a un servicio interno.
- Un valor que termina en un archivo de configuración XML.
- Un campo que se serializa a XML para ponerlo en una cola de mensajes.
- Un dato que un motor de plantillas de documentos inyecta en un DOCX.

La señal es que el parámetro no parece XML en absoluto. Se confirma con un payload de XInclude: si el valor se refleja después con el contenido de un archivo, había XML detrás.

## 6. Confirmar rápido

En este orden, por coste creciente:

1. Entidad **interna** — ¿se procesa el DTD? Una petición, sin red.
2. Entidad externa a un dominio propio — ¿se resuelven entidades externas? Confirma sin reflejo.
3. `file:///etc/passwd` reflejado — ¿hay canal directo?
4. XML mal formado a propósito — ¿vuelven errores detallados? Habilita [[XXE - canal por error]].
5. XInclude — para cuando 1 falla pero se sospecha XML detrás.

> [!tip] Anotar el formato en el hallazgo
> Un XXE en un endpoint SOAP y uno en la subida de avatares tienen la misma CWE y remediaciones distintas: uno se arregla en la configuración del parser del servicio, el otro en la biblioteca de procesamiento de imágenes. La severidad también cambia según quién puede llegar al endpoint.
