---
tipo: tradecraft
clase: "[[CWE-522 - Insufficiently Protected Credentials]]"
eje: vector-de-robo
implementacion: "Capturar un token de sesión existente por XSS, red, referencia o registro"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [token-alcanzable]
coste: bajo
alternativas: ["[[Sesión - fijación]]", "[[Sesión - falsificación de JWT]]"]
probado: 2026-08-08
contexto: [web-generica]
aliases:
  - robo de sesión
  - session hijacking
tags:
  - dominio/web
---

# Sesión - robo de token

## Cuándo lo elijo

Cuando el token existe y es alcanzable. Es la rama más directa del árbol de [[MOC - Gestión de sesión]] y la que más veces se usa, porque casi siempre llega **como consecuencia de otra vulnerabilidad** en vez de por mérito propio.

Los cuatro caminos, y el primero domina:

**XSS.** Si el token es legible por JavaScript, un XSS lo entrega. Ver [[XSS impacto - matriz de referencia]]. Es la razón por la que `HttpOnly` importa tanto y por la que guardar sesión en el almacenamiento del navegador —que es siempre legible por script— es una decisión de arquitectura con consecuencias directas acá.

**Fuga por referencia o por registro.** El token en una URL termina en el encabezado de referencia hacia sitios externos, en registros de proxy, en historiales de navegador y en informes de error. No hace falta atacar nada: hace falta mirar dónde quedó.

**Red.** Sin `Secure`, la cookie viaja en claro ante cualquier petición no cifrada. Cada vez menos viable, y todavía presente en redes internas y en aplicaciones con contenido mixto.

**Subdominio.** Una cookie con dominio del padre se envía a todos los subdominios: uno comprometido o de un tercero la recibe entera.

## Por qué funciona

Porque el token **es** la identidad. El servidor no distingue quién lo presenta: cualquiera que lo tenga es el usuario, y esa es toda la premisa del manejo de sesión sin estado adicional.

Las defensas del navegador —`HttpOnly`, `Secure`, `SameSite`, los prefijos de nombre— no cambian esa premisa: reducen la superficie por la que el token se escapa. La premisa solo cambia si el servidor ata la sesión a algo más que el token, cosa que casi ninguna aplicación hace porque rompe la movilidad de los usuarios.

## Cómo falla

- **`HttpOnly`** — corta la vía de XSS, que es la principal. Es el atributo de mayor retorno del dominio.
- **`Secure` y `SameSite`** — cortan la vía de red y la de envío entre sitios.
- **Prefijo `__Host-`** — impide escritura desde subdominios y exige `Secure` y ruta raíz. Barato y casi nunca usado.
- **Sesión atada a la IP o a la huella del cliente** — el token robado no sirve desde otro origen. Efectivo, y molesto para usuarios con IP variable: por eso casi no se implementa.
- **Vida corta con rotación** — reduce la ventana de utilidad del token robado.
- **El token es un JWT sin estado** — se roba igual, y además **no se puede revocar** cuando se descubre. Ver [[CWE-613 - Insufficient Session Expiration]].

## Coste

Bajo, pero **el costo real es el de la vulnerabilidad que lo habilita**. Nadie roba una sesión sin antes tener un XSS, un acceso a la red o una fuga. Esta nota es el impacto de otras técnicas más que una técnica propia, y así conviene reportarla: como consecuencia, encadenada a su causa.

## Huella esperada

- **La misma sesión desde dos orígenes distintos**, a veces simultáneamente. Es la firma central del robo de sesión y la detección de mayor retorno del dominio: un identificador que aparece desde dos países en cinco minutos no tiene explicación legítima.
- Cambio abrupto de agente de usuario para una sesión que venía estable.
- [[Log de acceso del servidor web]] con el token en la URL, si la fuga fue por ahí — y en ese caso el token está también en los registros del proxy y en los de cualquier sitio externo enlazado.
- Si la vía fue XSS, aplica además toda la huella de [[MOC - Cross-site scripting]]: el robo es el segundo acto y el primero suele ser más visible.

La detección por origen es la única que funciona sin instrumentar nada nuevo, y es la que conviene recomendar primero en un informe.

Los atributos de cookie y cómo probarlos están en [[Sesión - matriz de referencia]] § Atributos.
