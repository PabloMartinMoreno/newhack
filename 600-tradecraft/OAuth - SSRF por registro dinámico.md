---
tipo: tradecraft
clase: "[[CWE-918 - Server-Side Request Forgery]]"
eje: fase-del-flujo
implementacion: "Registrar un cliente cuyos campos de dirección hacen que el servidor de autorización pida lo que yo elija"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Consulta DNS saliente]]", "[[Log de errores del servidor web]]"]
requisitos: [registro-dinamico-de-cliente]
coste: medio
alternativas: ["[[SSRF - escaneo de la red interna]]", "[[SSRF - metadatos de instancia cloud]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - dynamic client registration
  - request_uri SSRF
tags:
  - dominio/web
---

# OAuth - SSRF por registro dinámico

## Cuándo lo elijo

Cuando el objetivo **es el servidor de autorización**, no el cliente. Es la única rama del dominio que invierte los papeles, y por eso cambia todo lo demás: no hace falta víctima, no hace falta interacción, y el impacto no es una cuenta sino la red interna del proveedor.

La condición es que exista registro dinámico de clientes —`/register` en el documento de descubrimiento— o que el flujo acepte parámetros que contengan direcciones. Si el registro es manual y cerrado, esta rama no aplica.

## Por qué funciona

El servidor de autorización tiene que **buscar cosas por la red**: la imagen de un cliente para mostrarla en la pantalla de consentimiento, las claves públicas del cliente para verificar sus peticiones firmadas, el objeto de petición cuando viene por referencia. Cada una de esas búsquedas es una dirección que el cliente aporta.

Los campos que sirven, en orden de fiabilidad:

| Campo | Qué hace el servidor | Qué devuelve |
|---|---|---|
| `jwks_uri` | Descarga las claves del cliente | Lo pide y a veces refleja el error con el cuerpo |
| `request_uri` | Descarga el objeto de petición | Ciego o con error reflejado |
| `logo_uri` | Descarga la imagen para el consentimiento | Ciego, pero se dispara en cada consentimiento |
| `sector_identifier_uri` | Descarga la lista de direcciones del sector | Reflejo en el error |
| `initiate_login_uri` | Lo invoca el proveedor | Ciego |

A partir de ahí es SSRF ordinario y se sigue por [[MOC - SSRF]]: primero metadatos de instancia, después red interna. El orden importa igual que allá — [[SSRF - metadatos de instancia cloud]] cuesta una petición y termina el trabajo, barrer cuesta cientos.

Lo específico de acá es que **los servidores de autorización suelen estar en el interior**. Un proveedor de identidad corporativo habla con el directorio, con bases de datos de usuarios y con servicios de administración; es de las máquinas mejor conectadas de la red, y eso hace que el mismo SSRF valga mucho más desde ahí que desde una aplicación web cualquiera.

`request_uri` tiene un segundo uso que conviene tener presente: apuntarlo a un recurso que devuelva un objeto de petición controlado permite fijar parámetros que el cliente no envió.

## Cómo falla

Falla cuando el registro dinámico está deshabilitado o requiere autenticación, que es lo que recomienda RFC 9700 para despliegues públicos.

Falla contra una lista blanca de esquemas y destinos para las descargas del servidor, o cuando esas búsquedas salen por un proxy que solo alcanza internet.

Y falla parcialmente cuando el servidor cachea: si guarda el resultado de la primera descarga, las variantes posteriores no se vuelven a pedir y hay que rotar el identificador de cliente en cada intento.

## Coste

Medio. Registrar un cliente y probar los cinco campos son diez peticiones; lo que sigue es el coste de [[MOC - SSRF]], que depende de si el canal es ciego.

El registro dinámico deja además un rastro administrativo —clientes basura en el proveedor— que conviene limpiar o al menos declarar en el informe. Es la única rama del dominio que **crea estado en el objetivo**, y eso cambia cómo se pide autorización antes de probarla.

## Huella esperada

Es la rama más ruidosa del dominio y la única con huella propia sólida, porque el servidor de autorización hace algo que normalmente no hace: **conectarse a un destino elegido por un tercero**.

- [[Conexión saliente del servidor de aplicación]] ve la petición. Si el destino es interno, es el caso que ninguna telemetría de borde cubre y que motivó ese artefacto.
- Si el destino es `169.254.169.254`, lo cubre [[Petición al servicio de metadatos de instancia]] con altísima fidelidad: un servidor de autorización no pide metadatos de instancia en medio de un registro de cliente.
- El barrido de la red interna lo cubre [[Barrido de puertos internos desde el servidor de aplicación]].
- Con el canal ciego queda [[Consulta DNS saliente]], y los errores de descarga fallida caen en [[Log de errores del servidor web]].

Hay además una señal administrativa que no es de red y que discrimina muy bien: **registros de cliente en ráfaga desde un mismo origen**, con campos de dirección que no apuntan a ningún dominio del cliente declarado. Ninguna detección del vault la cubre porque el vault no modela el registro de clientes como artefacto; queda anotado como hueco en [[MOC - OAuth]].
