---
tipo: moc
dominio: protocolo
aliases:
  - MOC HTTP
tags:
  - dominio/web
---

# MOC - HTTP

> [!abstract] Mapa de teoría, no de ataque
> Los otros MOCs contestan *cómo exploto esto*. Este contesta *qué presupone lo que estoy por explotar*. Cada nota enlazada existe porque hay al menos un ataque del vault que no se entiende sin ella — la regla de admisión de [[Estructura del vault]] § teoría.

HTTP es el sustrato de los 34 dominios web del vault. Casi ninguno ataca a HTTP: **atacan el desacuerdo entre dos lecturas del mismo mensaje**. Por eso la teoría acá no es contexto opcional, es la explicación de por qué el bug existe — y es lo primero que se cae cuando la técnica se enseña como receta.

Tres piezas concentran la mayoría de los dominios:

| Pieza | Por qué rinde tanto |
|---|---|
| Delimitación del cuerpo | Define dónde termina un mensaje y empieza otro |
| Sintaxis de cabeceras | Define qué es un campo y qué es un salto de línea |
| Clave de caché | Define cuándo dos peticiones son "la misma" |

## Árbol de decisión — qué pieza estoy mirando

```
¿Qué parte del mensaje está en juego?
├─ El límite entre un mensaje y el siguiente
│  ├─ ¿Cuántos bytes tiene el cuerpo? → [[HTTP - delimitación del cuerpo]]
│  ├─ ¿Quién comparte el socket?      → [[HTTP - el modelo de conexión]]
│  └─ ¿Por qué hay que delimitar?     → [[TCP - establecimiento de la conexión]]
├─ La primera línea
│  ├─ Forma de la URI (origin / absolute / authority) → [[HTTP - la línea de petición]]
│  └─ Método y sus garantías                          → [[HTTP - métodos y sus garantías]]
├─ Las cabeceras
│  ├─ Sintaxis, repetición, plegado → [[HTTP - sintaxis de cabeceras]]
│  ├─ Estado atornillado (cookies)  → [[HTTP - cookies]]
│  ├─ Identidad nativa del protocolo → [[HTTP - autenticación nativa]]
│  └─ El origen como frontera        → [[HTTP - el origen como frontera de confianza]]
├─ El cuerpo y su interpretación
│  ├─ Tipo de medio y sniffing → [[HTTP - negociación de contenido]]
│  └─ Codificaciones            → [[HTTP - codificaciones]]
└─ Lo que pasa entre cliente y aplicación
   ├─ ¿Quién almacena la respuesta? → [[HTTP - el modelo de caché]]
   ├─ ¿Cuántos saltos hay?          → [[HTTP - la cadena de intermediarios]]
   ├─ ¿Adónde te mandan?            → [[HTTP - códigos de estado y redirecciones]]
   └─ ¿Se habla HTTP/1.1 de verdad? → [[HTTP - HTTP2 y HTTP3]]
```

## Orden de aprendizaje

Por dependencia conceptual. Es el temario del módulo de fundamentos, y va **antes** de cualquier dominio web.

1. [[HTTP - la línea de petición]] — la unidad mínima y las tres formas de la URI
2. [[HTTP - sintaxis de cabeceras]] — qué es un campo, qué hace `\r\n`
3. [[HTTP - delimitación del cuerpo]] — dónde termina un mensaje
4. [[HTTP - el modelo de conexión]] — el socket como recurso compartido
5. [[HTTP - métodos y sus garantías]] — seguro, idempotente, y por qué nadie lo respeta
6. [[HTTP - códigos de estado y redirecciones]] — el control de flujo del protocolo
7. [[HTTP - cookies]] — el estado que HTTP no tiene
8. [[HTTP - el origen como frontera de confianza]] — de dónde sale el permiso del navegador
9. [[HTTP - negociación de contenido]] — quién decide cómo se interpreta el cuerpo
10. [[HTTP - codificaciones]] — percent, chunked, charset, compresión
11. [[HTTP - autenticación nativa]] — `Basic`, `Digest`, `Negotiate` y por qué la app hizo la suya
12. [[HTTP - el modelo de caché]] — clave y frescura
13. [[HTTP - la cadena de intermediarios]] — proxy inverso, CDN, WAF, normalización
14. [[HTTP - HTTP2 y HTTP3]] — binario, multiplexado, y la degradación como regreso a los problemas de 1.1

## Qué ataque habilita cada pieza

Esta tabla es la bisagra del mapa: enlaza la teoría con lo que ya está escrito.

| Pieza | Dominios que la presuponen |
|---|---|
| Delimitación del cuerpo | [[MOC - Request smuggling]] |
| Modelo de conexión | [[MOC - Request smuggling]] · [[MOC - Race conditions]] |
| Línea de petición | [[MOC - Host header]] · [[MOC - Request smuggling]] |
| Sintaxis de cabeceras | [[MOC - CRLF injection]] · [[MOC - Email header injection]] · [[MOC - HTTP parameter pollution]] |
| Métodos | [[MOC - CSRF]] · [[MOC - Broken access control]] |
| Estado y redirecciones | [[MOC - SSRF]] · [[MOC - OAuth]] |
| Cookies | [[MOC - Gestión de sesión]] · [[MOC - CSRF]] |
| Origen como frontera | [[MOC - CORS]] · [[MOC - Clickjacking]] · [[MOC - Tabnabbing]] · [[MOC - WebSocket]] |
| Negociación de contenido | [[MOC - File upload]] · [[MOC - Cross-site scripting]] |
| Codificaciones | [[MOC - Request smuggling]] · [[MOC - File inclusion]] |
| Autenticación nativa | [[MOC - Autenticación]] · [[MOC - AD envenenamiento y relay]] |
| Modelo de caché | [[MOC - Web cache]] |
| Cadena de intermediarios | [[MOC - Web cache]] · [[MOC - Host header]] · [[MOC - Request smuggling]] |
| HTTP/2 y HTTP/3 | [[MOC - Request smuggling]] |

## Cara azul

La teoría del protocolo decide **qué se puede registrar**, y la respuesta incómoda es que el log de la aplicación ve muy poco de lo que acá importa:

- El frente normaliza las cabeceras antes de que el back las escriba, así que la firma cruda de un smuggling se pierde en el salto.
- La conexión que trajo la petición no aparece en el log de aplicación: correlacionar dos peticiones por socket necesita telemetría del proxy.
- Lo que sí sobrevive son los observables de la caché — `X-Cache`, `Age` — y los de estado: una respuesta que no corresponde a la petición que la pidió.

La conclusión transversal es de [[La detección vive en el agregado, no en el evento]]: ninguna de estas piezas se detecta mirando una petición sola.

## Huecos conocidos

Escritas 3 de 14. Faltan las once del orden de aprendizaje que todavía no tienen nota — el enlace queda igual, es roadmap explícito. Prioridad por deuda: sintaxis de cabeceras y la línea de petición, porque son las dos que más dominios ya escritos presuponen.

**TCP** tiene su primera pieza escrita ([[TCP - establecimiento de la conexión]]) y todavía no tiene MOC propio: con una sola nota, un árbol de decisión de una rama sería ceremonia vacía. Cuando llegue a cuatro o cinco piezas —ventana y control de flujo, cierre y estados, fragmentación y MSS— se abre `MOC - TCP` y este mapa lo enlaza como sistema hermano en lugar de alojarlo.

Sistemas sin abrir: TLS, DNS, Kerberos, LDAP, SMB, el DOM.
