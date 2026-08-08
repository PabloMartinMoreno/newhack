---
tipo: telemetria
plataforma: [navegador]
producto: el navegador del usuario
identificador: "report-uri / report-to"
por-defecto: false
coste: medio
aliases:
  - CSP report
  - report-uri
  - violación de CSP
tags:
  - dominio/web
---

# Informe de violación de CSP

## Qué lo genera

El **navegador del usuario**, cuando la página intenta hacer algo que la política de seguridad de contenido prohíbe: ejecutar un script inline, cargar un recurso de un origen no permitido, usar `eval`.

Es el único artefacto del vault que **no lo emite un sistema propio**. Lo emite el navegador de la víctima y llega por una petición HTTP a un endpoint que la aplicación expone. Esa peculiaridad define todas sus limitaciones: es telemetría que envía un cliente no confiable, y hay que tratarla como tal.

También es la única fuente que ve el lado del cliente. [[XSS - DOM-based]] y [[XSS - mutation XSS]] **nunca tocan el servidor**: la carga viaja en el fragmento de la URL o se construye en el navegador, así que [[Log de acceso del servidor web]] no registra absolutamente nada. Sin esta fuente, ese medio dominio es invisible.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `violated-directive` | Qué regla se rompió | `script-src` es la que importa |
| `blocked-uri` | Qué se intentó cargar | Un dominio externo desconocido es exfiltración |
| `document-uri` | Dónde pasó | Identifica la página vulnerable |
| `script-sample` | Primeros bytes del script | A veces trae el payload — muy limitado a propósito |
| `source-file`, `line-number` | Dónde en el código | Ubica el sink de [[XSS - DOM-based]] |
| `disposition` | `enforce` o `report` | Si es `report`, el ataque **funcionó** |

`script-sample` está truncado por diseño de la especificación, para que la propia telemetría no se convierta en una fuga de datos. Alcanza para triaje, no para reconstruir el payload.

## Coste de recolección

Medio, y engañoso: el volumen no depende del tráfico propio sino de **las extensiones del navegador de los usuarios**, que inyectan scripts todo el tiempo y disparan violaciones sin parar. Una política recién desplegada genera miles de informes al día, casi todos basura.

Domarlo es un trabajo de semanas y es la razón por la que casi nadie mantiene esta fuente encendida.

## Cómo se activa

Directiva `report-uri` o `report-to` en la cabecera de política, apuntando a un endpoint propio. Se puede desplegar en modo solo-informe antes de aplicar la política, que es el orden correcto.

> [!warning] `Content-Security-Policy-Report-Only` no bloquea nada
> Si `disposition` es `report`, la violación **ocurrió**: el script se ejecutó y solo se avisó. Es útil para calibrar antes de aplicar la política y es un falso sentido de seguridad si queda así para siempre. Distinguir los dos modos en el triaje no es opcional.

## Limitaciones

- **La emite un cliente no confiable.** El endpoint recibe lo que cualquiera quiera mandarle: se puede inundar de informes falsos para enterrar uno real. Necesita control de ritmo propio y no debe alimentar decisiones automáticas.
- **Solo ve lo que la política prohíbe.** Un XSS que ejecuta dentro de lo permitido —ver [[XSS bypass de CSP - matriz de referencia]]— no genera ningún informe. Una política débil produce silencio, y el silencio se parece a estar seguro.
- **Sin CSP no hay fuente.** Es el caso mayoritario.
- **Ruido de extensiones** que puede sepultar la señal.
- **Muestra truncada**: no reconstruye el ataque.

## Quién lo emite / quién lo consume

Rojo: [[XSS - CSP]] · [[XSS - DOM-based]] · [[XSS - mutation XSS]] · [[XSS - almacenado]] · [[XSS - reflejado]] · [[File upload - SVG y XSS almacenado]]
Azul: [[Violación de CSP por script inline]]
