---
tipo: tradecraft
clase: "[[CWE-918 - Server-Side Request Forgery]]"
eje: uso-del-host
implementacion: "Cambiar el Host para que el proxy de adelante enrute la petición a un servidor interno que no debería ser alcanzable"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Log de acceso del servidor web]]", "[[Log de errores del servidor web]]"]
requisitos: [proxy-que-enruta-por-el-host]
coste: medio
alternativas: ["[[Host header - envenenamiento del restablecimiento]]", "[[SSRF - escaneo de la red interna]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - routing-based SSRF
  - SSRF por Host
tags:
  - dominio/web
---

# Host header - SSRF por enrutamiento

## Cuándo lo elijo

Cuando delante de la aplicación hay un proxy o balanceador que **decide a qué servidor mandar la petición según el `Host`**, y ese enrutamiento se puede desviar a un destino interno. Se reconoce cuando cambiar el `Host` cambia a qué backend responde —un `Host` distinto devuelve otra aplicación, un error distinto, o alcanza algo que no debería.

Es la rama que convierte el `Host` en un vector de [[MOC - SSRF]] sin necesitar un parámetro de URL. Se elige cuando el objetivo es alcanzar la red interna y el enrutamiento del frente lo permite; si el Host construye un enlace de correo, la rama es [[Host header - envenenamiento del restablecimiento]].

## Por qué funciona

En una infraestructura con muchos sitios detrás de un mismo proxy, el proxy usa el `Host` para saber a cuál reenviar —el enrutamiento por nombre de host virtual—. Si el proxy confía en el `Host` sin restringirlo a los dominios públicos, el atacante lo apunta a un servicio interno:

```http
GET / HTTP/1.1
Host: servicio-interno
```

El proxy resuelve `servicio-interno` y reenvía la petición ahí, dándole al atacante acceso a algo que no cruza el perímetro. A partir de ahí es SSRF ordinario y se sigue por [[MOC - SSRF]]:

- **Paneles de administración internos** que confían en que solo se los alcanza desde adentro.
- **El servicio de metadatos de instancia** —`169.254.169.254`— si el proxy lo enruta, con el impacto de [[SSRF - metadatos de instancia cloud]].
- **Escaneo de la red interna** cambiando el `Host` por IPs y nombres internos.

La variante más potente es cuando el proxy acepta una **URL absoluta en la línea de petición** —`GET https://interno/ HTTP/1.1`— o un `Host` con puerto, que algunos proxies reenvían tal cual. Las formas están en [[Host header inyección - matriz de referencia]].

A diferencia del SSRF por parámetro, acá el atacante no necesita que la aplicación haga una petición: **el proxy la hace por diseño**, solo que al destino equivocado.

## Cómo falla

Falla cuando el proxy **restringe el enrutamiento a una lista blanca de dominios** y rechaza o normaliza cualquier `Host` que no esté en ella. Es la mitigación correcta.

Falla cuando el frente resuelve el backend por su configuración y no por el `Host` del cliente —el `Host` se usa solo para el enrutamiento entre sitios públicos conocidos.

Y falla, como todo SSRF interno, si la red interna está segmentada de modo que el proxy no alcanza los servicios sensibles.

## Coste

Medio. Confirmar que el `Host` enruta son pocas peticiones probando nombres internos y viendo si la respuesta cambia. Lo que sigue es el costo de [[MOC - SSRF]] —barrer, alcanzar metadatos—, con la misma economía: metadatos de instancia primero (una petición, termina el trabajo), barrido después (caro).

El reconocimiento del enrutamiento es lo específico: hay que descubrir nombres internos válidos, que a veces salen de errores, de certificados, o de adivinar convenciones.

## Huella esperada

Ruidosa y bien cubierta, porque el proxy termina conectándose a un destino interno —lo mismo que cualquier SSRF—:

- Si el destino es un servicio interno o `169.254.169.254`, la conexión la ve [[Conexión saliente del servidor de aplicación]] y la cubren [[Barrido de puertos internos desde el servidor de aplicación]] y [[Petición al servicio de metadatos de instancia]] según el destino, sin saber que el vector fue el `Host`.
- El `Host` anómalo en sí queda en [[Log de acceso del servidor web]] si se registra —un `Host` que no es un dominio público de la aplicación—, la misma firma escribible que las otras ramas del dominio.
- El reconocimiento fallido —nombres internos que no resuelven— deja errores en [[Log de errores del servidor web]].

Es la rama del dominio con la cara azul más cubierta, porque hereda las detecciones de SSRF que ya existen. El `Host` interno es además una firma de host propia: un `Host` que apunta a una IP privada o a un nombre no público es tan anómalo como el `Origin: null` de CORS. Anotado en [[MOC - Host header]].
