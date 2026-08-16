---
tipo: tecnica
taxonomia: cwe
identificador: CWE-113
wstg: WSTG-INPV-16
tacticas: []
aliases:
  - CWE-113
  - CRLF injection
  - HTTP response splitting
  - inyección CRLF
tags:
  - dominio/web
---

# CWE-113 - Improper Neutralization of CRLF Sequences in HTTP Headers

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - CRLF injection]]; las codificaciones en [[CRLF inyección - matriz de referencia]]; los payloads en [[CRLF impacto - matriz de referencia]].

## Qué es

Las cabeceras HTTP se separan entre sí con la secuencia de retorno de carro y salto de línea —`\r\n`, o `%0d%0a` codificada—. Si la aplicación construye una cabecera de respuesta con entrada del usuario sin filtrar esa secuencia, el atacante la inyecta y **crea una cabecera nueva** donde debería haber un valor, o **termina las cabeceras y empieza un cuerpo** que él controla.

El caso mínimo: una redirección que refleja un parámetro en la cabecera `Location`. Inyectar `%0d%0a` corta la cabecera y permite agregar las propias.

## Por qué el átomo es `\r\n`

Todo el protocolo HTTP/1.1 estructura la respuesta con `\r\n`: separa cabeceras, y un `\r\n\r\n` doble separa las cabeceras del cuerpo. Controlar esa secuencia dentro de un valor da control sobre la estructura de la respuesta:

- **Un `\r\n`** rompe el valor y empieza una cabecera nueva → inyección de cabecera.
- **Un `\r\n\r\n`** cierra las cabeceras y empieza el cuerpo → división de respuesta, con un cuerpo controlado.

Es el mismo átomo que sostiene [[MOC - Request smuggling]] —allá el `\r\n` desincroniza dónde termina una **petición**; acá controla la estructura de una **respuesta**—. Las dos clases explotan que HTTP delimita con caracteres que pueden viajar en los datos.

## Qué se consigue, en orden de impacto

| Inyección | Resultado |
|---|---|
| Una cabecera `Set-Cookie` | Fijación de sesión — [[CWE-384 - Session Fixation]] |
| La cabecera `Location` | Redirección abierta — [[CWE-601 - URL Redirection to Untrusted Site]] |
| Cabeceras de CORS | Relajar la política de origen — [[MOC - CORS]] |
| Un cuerpo de respuesta completo | XSS reflejado, y si se cachea, masivo — [[MOC - Web cache]] |
| Líneas en un registro | Falsificar entradas de log — ataca la telemetría |

El último es particular: el CRLF puede **corromper los registros** que deberían detectar el ataque, inyectando líneas de log falsas. Es una de las pocas técnicas que ataca directamente la capa defensiva.

## Por qué la mitigación es filtrar el salto de línea

- **Eliminar o rechazar** `\r` y `\n` —y sus codificaciones— en cualquier entrada que llegue a una cabecera de respuesta. Es la defensa directa.
- **No construir cabeceras con entrada del usuario**: usar APIs que serializan las cabeceras y rechazan los saltos de línea por diseño —los frameworks modernos ya lo hacen, que es por qué la clase decayó en HTTP/1.1 pero sigue viva en integraciones a mano.
- HTTP/2 lo mitiga estructuralmente —las cabeceras no se delimitan con `\r\n`— pero la degradación a HTTP/1.1 lo reintroduce, igual que en el smuggling.

## Referencias canónicas

- [CWE-113](https://cwe.mitre.org/data/definitions/113.html)
- [CWE-93](https://cwe.mitre.org/data/definitions/93.html) — CRLF Injection genérica, la clase padre
- WSTG-INPV-16
- OWASP — HTTP Response Splitting
