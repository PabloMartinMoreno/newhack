---
tipo: tecnica
taxonomia: cwe
identificador: CWE-522
wstg: [WSTG-SESS-02, WSTG-SESS-04]
tacticas: []
aliases:
  - CWE-522
  - Credenciales mal protegidas
  - Token expuesto
tags:
  - dominio/web
---

# CWE-522 - Insufficiently Protected Credentials

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Gestión de sesión]]; la variante, en [[Sesión - robo de token]].

## Qué es

La credencial —acá, el token de sesión— se almacena o se transmite de forma que alguien más puede obtenerla. No hay que romper criptografía ni adivinar nada: hay que estar donde la credencial pasa.

## Por qué el token de sesión cuenta como credencial

Porque **es** la identidad. El servidor no distingue quién lo presenta: cualquiera que lo tenga es el usuario. Un token de sesión robado vale lo mismo que la contraseña, y a veces más — no lo protege el segundo factor, que ya se verificó cuando la sesión se emitió.

## Las cuatro exposiciones

- **Legible por script.** Sin `HttpOnly`, o guardado en el almacenamiento del navegador —que es siempre legible—, cualquier XSS lo entrega. Es la vía principal y la razón por la que ese atributo importa tanto.
- **En la URL.** El token en una ruta o en la cadena de consulta queda en el encabezado de referencia hacia sitios externos, en registros de proxy, en historiales y en informes de error. Nadie tiene que atacar nada.
- **En claro por la red.** Sin `Secure`, la cookie viaja ante cualquier petición no cifrada.
- **Compartido con subdominios.** Una cookie con dominio del padre se envía a todos: un subdominio de un tercero la recibe entera.

## Las defensas y su alcance real

`HttpOnly`, `Secure`, `SameSite` y los prefijos de nombre **no cambian la premisa** de que quien tiene el token es el usuario: reducen la superficie por la que se escapa. Es una distinción que conviene hacer explícita en un informe, porque explica por qué no alcanza con poner los atributos.

La premisa solo cambia si el servidor ata la sesión a algo más que el token —origen, huella del cliente, prueba de posesión—, cosa que casi ninguna aplicación hace porque rompe la movilidad de los usuarios. Es una decisión de compromiso legítima, no un descuido, y por eso este dominio se defiende sobre todo **detectando** el uso del token robado y no impidiéndolo.

## Referencias canónicas

- [CWE-522](https://cwe.mitre.org/data/definitions/522.html)
- [CWE-1004](https://cwe.mitre.org/data/definitions/1004.html) — cookie sensible sin `HttpOnly`
- [CWE-598](https://cwe.mitre.org/data/definitions/598.html) — datos sensibles en la cadena de consulta
- WSTG-SESS-02, WSTG-SESS-04
