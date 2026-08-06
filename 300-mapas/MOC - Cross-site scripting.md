---
tipo: moc
dominio: web
aliases:
  - MOC XSS
  - Cross-site scripting
tags:
  - dominio/web
---

# MOC - Cross-site scripting

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-79 - Cross-site Scripting]]. Acá vive **la decisión**.

XSS es la intersección de cinco ejes ortogonales. Una nota por **valor de eje**, nunca por combinación.

| Eje | Valores |
|---|---|
| Tipo / entrega | reflejado · almacenado · DOM-based |
| Contexto de salida | HTML body · atributo · dentro de `<script>` · URL (href/src) · CSS |
| Sink (solo DOM) | `innerHTML` · `document.write` · `eval` · `location` · `setAttribute` |
| Obstáculo | filtro de chars/tags · WAF · CSP |
| Impacto | robo de sesión · keylogger · CSRF vía XSS · account takeover · worm |

## Árbol de decisión — qué tipo es

```
¿Tu input aparece en la respuesta del servidor?
├─ Sí, en el mismo request con el payload   → reflejado   → [[XSS - reflejado]]
├─ Sí, guardado y servido después           → almacenado  → [[XSS - almacenado]]
└─ No aparece en el HTML del server,
   pero lo procesa JavaScript del cliente     → DOM-based   → [[XSS - DOM-based]]
```

El tipo decide la **entrega y el impacto** (a quién le llega y cuándo), no cómo se arma el payload. Eso lo decide el contexto.

## Árbol de decisión — contexto → cómo romper

El eje que más rinde: el mismo payload no sirve en todos los contextos.

```
¿Dónde cae tu input en la página?
├─ Entre tags (body)      → inyectar tag: <script> / <img onerror>
├─ Dentro de un atributo  → cerrar la comilla + event handler
├─ Dentro de <script>     → cerrar el string/statement de JS
├─ En un href/src         → javascript: URI
└─ En CSS                 → url() / expression
```

Sintaxis de cada uno en [[XSS contextos - matriz de referencia]].

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[XSS contextos - matriz de referencia]] | Cómo romper según dónde cae el input — HTML, atributo, JS, URL, CSS |
| [[XSS sources y sinks - matriz de referencia]] | DOM-based: qué source alimenta qué sink y cómo se explota cada uno |
| [[XSS evasión - matriz de referencia]] | Filtros de chars/tags, sin paréntesis, sin comillas, mayúsculas, mXSS |
| [[XSS bypass de CSP - matriz de referencia]] | Gadgets JSONP, `nonce`, `strict-dynamic`, dominios permitidos |
| [[XSS dangling markup - matriz de referencia]] | Exfil sin JS cuando la CSP bloquea el script |
| [[XSS impacto - matriz de referencia]] | Robo de cookie/sesión, keylogger, forzar acciones, robo de credenciales |

## Orden de aprendizaje

1. [[CWE-79 - Cross-site Scripting]] — qué es y por qué existe
2. [[XSS contextos - matriz de referencia]] — dónde cae el input y cómo romper (base de todo)
3. [[XSS - reflejado]] — el caso más simple, fija el modelo
4. [[XSS - almacenado]] — cambia el impacto: le llega a otros, persiste
5. [[XSS - DOM-based]] → [[XSS sources y sinks - matriz de referencia]] — el modelo cliente-only
6. [[XSS evasión - matriz de referencia]] — cuando el filtro bloquea el payload básico
7. [[XSS - CSP]] y su [[XSS bypass de CSP - matriz de referencia]] — el obstáculo del XSS moderno
8. [[XSS impacto - matriz de referencia]] — qué hacés con la ejecución

## Cara azul

| Tipo | Telemetría | Firma |
|---|---|---|
| Reflejado / almacenado | [[Log de acceso del servidor web]] | `<script`, `onerror=`, `javascript:` en parámetros o cuerpo |
| DOM-based | — | **Invisible al servidor**: el payload nunca llega al backend; solo se ve en el cliente o en violaciones de CSP |

## Huecos conocidos

- [x] Tres tipos + contextos + sinks + evasión + CSP + impacto
- [x] [[XSS - mutation XSS]] (bypass de sanitizador)
- [x] [[XSS - dangling markup injection]] (exfil sin ejecución de JS)
- [ ] Telemetría propia: reporte de violación de CSP como artefacto en `550-telemetria/`
