---
tipo: tradecraft
clase: "[[CWE-79 - Cross-site Scripting]]"
eje: tipo
implementacion: "Payload guardado por la app y servido a cada visitante"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Informe de violación de CSP]]", "[[Registro del WAF]]"]
requisitos: [input-persistido, servido-a-otros-usuarios]
coste: bajo
alternativas: ["[[XSS - reflejado]]", "[[XSS - DOM-based]]"]
probado: 2026-08-06
contexto: [chrome]
aliases:
  - stored XSS
  - persistent XSS
  - XSS almacenado
tags:
  - dominio/web
---

# XSS - almacenado

## Cuándo lo elijo

Cuando el input se **guarda** y se sirve después a quien visite la página: un comentario, un nombre de perfil, un ticket de soporte. Mismo payload que reflejado, **impacto mucho mayor** — no necesito que nadie haga clic en un enlace, le llega a todo el que abra la página.

Es el que apunto cuando quiero alcanzar a un **administrador**: dejo el payload en un campo que un admin va a revisar (un ticket, un reporte de abuso) y ejecuto en su sesión.

## Por qué funciona

Igual que reflejado, pero la app persiste el valor sin codificar y lo re-emite en cada render. La entrega deja de depender de un enlace: el propio sitio distribuye el payload a sus usuarios.

## Cómo falla

- **Codificación en la salida** — si escapan al renderizar, no importa que se haya guardado crudo.
- **Sanitización al guardar** (DOMPurify y afines) — el payload llega ya roto a la base.
- **Moderación** — contenido que un humano revisa antes de publicarse.
- **CSP**.

## Coste

Bajo, y con el mejor retorno de los tres tipos: una sola inyección alcanza a muchas víctimas sin interacción del atacante. El riesgo es de **detección**: queda persistido y visible, un defensor puede encontrarlo revisando contenido.

## Huella esperada

- El payload queda en la base **y** en el [[Log de acceso del servidor web]] de la petición que lo guardó.
- Cada víctima genera peticiones salientes (robo de cookie, callback) que se pueden correlacionar.
- A diferencia del reflejado, deja **evidencia persistente** en el almacenamiento de la app.

Payloads por contexto: [[XSS contextos - matriz de referencia]]. Qué hacer con la ejecución: [[XSS impacto - matriz de referencia]].
