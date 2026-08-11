---
tipo: tradecraft
clase: "[[CWE-79 - Cross-site Scripting]]"
eje: tipo
implementacion: "Payload en la request, ejecutado en la respuesta del mismo request"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Informe de violación de CSP]]", "[[Registro del WAF]]"]
requisitos: [input-reflejado-en-la-respuesta, victima-abre-el-enlace]
coste: bajo
alternativas: ["[[XSS - almacenado]]", "[[XSS - DOM-based]]"]
probado: nunca
contexto: [chrome]
aliases:
  - reflected XSS
  - XSS reflejado
tags:
  - dominio/web
---

# XSS - reflejado

## Cuándo lo elijo

Cuando mi input vuelve en la respuesta del **mismo** request que lo envía. Es el más simple del árbol de [[MOC - Cross-site scripting]] y el primero para fijar el modelo: mando un parámetro, aparece en el HTML, ejecuto.

El límite es la entrega: no se guarda, así que solo afecta a quien **abra mi enlace** con el payload. Requiere ingeniería social — mandar el link a la víctima.

## Por qué funciona

La app toma un valor de la request (query string, a veces header o cuerpo) y lo escribe en la página sin codificar para el contexto. El payload viaja en la URL que le paso a la víctima; su navegador hace el request, recibe el HTML con mi JS adentro y lo ejecuta con el origen del sitio.

## Cómo falla

- **La víctima no abre el enlace** — es un ataque dirigido, no masivo.
- **El input se codifica** para el contexto de salida — la mitigación correcta lo mata.
- **CSP** que bloquea inline/scripts externos.
- **Filtros de entrada / WAF** — se combina con [[XSS evasión - matriz de referencia]].
- Navegadores modernos: el auditor XSS ya no existe (se removió de Chrome), así que eso ya no es obstáculo.

## Coste

Bajo en técnica. El costo real es la **entrega**: hay que hacer que la víctima haga clic en un enlace armado, con lo que eso implica de pretexto y de exposición del dominio del atacante en la URL.

## Huella esperada

- El payload viaja en la URL/cuerpo → queda entero en el [[Log de acceso del servidor web]].
- Un `Referer` con el payload en la petición siguiente, si el JS navega.

Payloads por contexto: [[XSS contextos - matriz de referencia]]. Qué hacer con la ejecución: [[XSS impacto - matriz de referencia]].
