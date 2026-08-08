---
tipo: deteccion
tecnicas: ["[[CWE-79 - Cross-site Scripting]]"]
telemetria: ["[[Informe de violación de CSP]]"]
forma: agregado
ventana: "1h"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - CSP report como detección de XSS
tags:
  - dominio/web
---

# Violación de CSP por script inline

## Qué detecta

Informes de violación de `script-src` sobre una misma página, con `blocked-uri` de tipo inline o `eval`, por encima de la línea base de esa página.

Es la **única** detección del vault que ve [[XSS - DOM-based]] y [[XSS - mutation XSS]]. Esas dos nunca tocan el servidor: la carga viaja en el fragmento de la URL o se construye en el navegador, así que [[Log de acceso del servidor web]] no registra nada y [[Registro del WAF]] tampoco. Sin esta fuente, ese medio dominio es invisible.

## Lógica

```
csp_reports
| where timestamp > ago(1h)
| where violated_directive startswith 'script-src'
| where blocked_uri in ('inline', 'eval', 'data') or blocked_uri !in (origenes_conocidos)
| summarize
    n = count(),
    usuarios = dcount(session_id),
    muestras = make_set(script_sample, 5)
  by document_uri, blocked_uri
| where n > baseline_de_la_pagina * 3
```

Dos afinados que cambian el resultado:

**Separar por `disposition`.** Si es `report`, la política no bloqueó y **el script se ejecutó**. Esos informes no son "un ataque frustrado": son un ataque exitoso con aviso.

**Mirar `usuarios`.** Una violación en muchas sesiones distintas sobre la misma página es [[XSS - almacenado]] sirviéndose a todos los visitantes, que es la más grave del dominio. Una violación en una sola sesión es reflejado, DOM-based, o una extensión del navegador.

Y una regla aparte, de mayor fidelidad: `blocked-uri` apuntando a un **dominio externo desconocido** es exfiltración en curso — el payload intentando sacar datos. Ver [[XSS impacto - matriz de referencia]].

## Falsos positivos conocidos

- **Extensiones del navegador**, que inyectan scripts permanentemente. Es el falso positivo dominante y por lejos: en una política recién desplegada son la mayoría absoluta de los informes. Domarlas lleva semanas y es la razón por la que casi nadie mantiene esta fuente.
- **Scripts propios que la política no contempla** — analítica, chat de soporte, publicidad. Ruido constante hasta que la política se afina.
- **Informes falsos.** La fuente la emite un cliente no confiable: cualquiera puede inundar el endpoint para enterrar un informe real. Necesita control de ritmo propio.
- **Navegadores viejos** con implementaciones divergentes.

Por eso la regla es de forma `agregado` contra una línea base por página, y no una alerta por informe.

## Evasiones conocidas

- **Que la política sea débil.** Cualquier técnica de [[XSS bypass de CSP - matriz de referencia]] ejecuta **dentro** de lo permitido y no genera ningún informe. Una política con `unsafe-inline`, con un comodín, o con un extremo JSONP alcanzable produce silencio — y el silencio se parece a estar seguro.
- **Sin CSP no hay fuente**, que es el caso mayoritario.
- **Inundar el endpoint** con informes basura para tapar el real.
- **Payload que no viola nada** — un XSS que solo lee el DOM y exfiltra por un canal permitido.

Esta detección mide la calidad de la política tanto como la presencia de ataques. Pocos informes puede significar que no hay XSS o que la política no bloquea nada, y **distinguir esas dos cosas requiere revisar la política, no los informes**.

## Cómo se prueba

Disparadores: [[XSS - reflejado]] y [[XSS - DOM-based]] contra un laboratorio con CSP en modo de aplicación y `report-uri` configurado.

Forma `agregado`: necesita la línea base por página, que en este caso es sobre todo el ruido de las extensiones de los usuarios reales. Sin población real, la línea base de laboratorio no sirve para nada.
