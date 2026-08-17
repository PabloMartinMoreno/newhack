---
tipo: meta
aliases:
  - X-Frame-Options
  - frame-ancestors
  - frame buster bypass
tags:
  - meta/referencia
  - dominio/web
---

# Clickjacking - encuadre - matriz de referencia

> [!info] Referencia pura, no un zettel
> ¿Se puede encuadrar el objetivo? La superposición está en [[Clickjacking - superposición - matriz de referencia]]; el criterio, en [[MOC - Clickjacking]].

La primera pregunta del dominio: si no se puede encuadrar, no hay clickjacking. Esto es cómo comprobarlo y cómo sortear defensas débiles.

## 1. Probar el encuadre

Una página mínima:

```html
<iframe src="https://objetivo.com/perfil" width="800" height="600"></iframe>
```

Abrirla y ver la consola:

| Resultado | Qué significa |
|---|---|
| El objetivo aparece en el marco | Encuadrable → clickjacking posible |
| Marco en blanco + error en consola | Bloqueado por cabecera. Ver cuál abajo |
| El objetivo aparece y luego "salta" | Frame-buster por JS → § 4 |

## 2. Leer las defensas

```sh
curl -sI https://objetivo.com/perfil | grep -iE 'x-frame-options|content-security-policy'
```

| Cabecera | Encuadre |
|---|---|
| `X-Frame-Options: DENY` | Bloqueado en todos lados |
| `X-Frame-Options: SAMEORIGIN` | Solo desde el mismo origen |
| `X-Frame-Options: ALLOW-FROM url` | Obsoleto, muchos navegadores lo ignoran → **encuadrable** |
| `CSP: frame-ancestors 'none'` | Bloqueado |
| `CSP: frame-ancestors 'self'` | Solo mismo origen |
| `CSP: frame-ancestors *.objetivo.com` | Desde subdominios → si controlás uno, encuadrable |
| ninguna de las dos | **Encuadrable, sin defensa** |

## 3. Grietas en las defensas

- **`ALLOW-FROM` obsoleto.** Los navegadores modernos lo ignoran, así que un sitio que solo usa `X-Frame-Options: ALLOW-FROM` está desprotegido.
- **`frame-ancestors` con comodín de subdominio.** Si acepta `*.objetivo.com` y hay un subdominio bajo control —toma de subdominio, XSS, servicio de terceros—, se encuadra desde ahí. Misma superficie que [[CORS - null y comodín de subdominio]] y [[OAuth - redirect_uri mal validado]].
- **Solo en algunas rutas.** La cabecera puede estar en el login y faltar en la página de la acción sensible. Probar la ruta exacta del objetivo, no la raíz.
- **`X-Frame-Options` sin `frame-ancestors` en navegadores viejos**, o al revés.

## 4. Bypass de frame-busters por JavaScript

Cuando la defensa es código JS que detecta el marco y rompe (`if (top != self) top.location = self.location`), el atributo `sandbox` del marco lo neutraliza:

```html
<iframe src="https://objetivo.com/perfil"
        sandbox="allow-forms allow-scripts allow-same-origin"></iframe>
```

`sandbox` **sin** `allow-top-navigation` impide que el frame-buster cambie la ubicación de la página superior, así que el código de ruptura no puede hacer nada. Se dejan `allow-forms` y `allow-scripts` para que el objetivo funcione, y se omite `allow-top-navigation`.

Otras vías contra frame-busters:
- `onbeforeunload` que cancela la navegación de ruptura.
- Cargar el objetivo con `204 No Content` en medio para frustrar el redireccionamiento.
- Doble marco anidado, que confunde algunos frame-busters que solo miran `top`.

## 5. Herramienta

**Burp Clickbandit** — genera la página de ataque a partir de la acción objetivo, con la superposición y la calibración. Es lo más rápido para una prueba de concepto.

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| Marco en blanco | Cabecera de bloqueo; leer cuál con § 2 |
| El objetivo salta fuera del marco | Frame-buster JS; `sandbox`, § 4 |
| Encuadra la raíz pero no la acción | La cabecera está solo en algunas rutas; probar la exacta |
| `ALLOW-FROM` presente | Obsoleto: probablemente encuadrable igual |
| `frame-ancestors 'self'` | Solo mismo origen; buscar un subdominio si hay comodín |
| Encuadra pero el clic no pasa | Ver la superposición, [[Clickjacking - superposición - matriz de referencia]] |

## Relacionadas

[[MOC - Clickjacking]] · [[Clickjacking - superposición - matriz de referencia]] · [[XSS bypass de CSP - matriz de referencia]] · [[CORS bypass de origen - matriz de referencia]]
