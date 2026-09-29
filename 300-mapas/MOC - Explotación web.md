---
tipo: moc
dominio: web
aliases:
  - Explotación web
  - Web explotación
  - MOC web explotación
tags:
  - dominio/web
---

# MOC - Explotación web

> [!abstract] Hub de explotación de la superficie web
> La teoría del protocolo, en [[MOC - HTTP]]. El reconocimiento de esta superficie —footprinting, subdominios, fingerprint, crawling— se separó a [[MOC - Reconocimiento web]]. Acá vive el **árbol maestro** que enruta por *dónde falla la aplicación*; cada familia es un grupo de MOCs propios, indexados abajo. Los MOCs se organizan por **mecanismo**, no por nombre: la pregunta que abre cada familia es dónde falla la app, no cómo se llama el bug. El orden va de lo clásico a lo avanzado.

La web no se ataca por un servicio ni por una herramienta: se ataca por **dónde la aplicación confía de más** —en el input, en la identidad, en un recurso que trae, en el navegador de la víctima, en que dos capas lean igual un mensaje, o en que su lógica no se pueda torcer—. Ese "dónde falla" es el eje raíz, y es lo que decide a qué familia ir.

| Familia | La app falla en… |
|---|---|
| Inyección | interpretar el dato como código o consulta |
| Identidad y acceso | verificar quién sos o qué podés |
| El servidor trae/incluye | pedir o incluir un recurso que no debía |
| Cliente y confianza del navegador | lo que ejecuta o en quién confía el browser |
| Discrepancia de parseo | dos capas que leen el mismo mensaje distinto |
| Lógica, estado y objetos | una secuencia o un objeto que se puede torcer |

## Árbol de decisión — ¿dónde falla la app?

```
¿Qué hace mal la aplicación con lo que le mando?
├─ Lo ejecuta como código o consulta          → Inyección
│  ├─ motor de datos (SQL/NoSQL/LDAP/XPath)    → familia Inyección ↓
│  ├─ comando de SO                            → [[MOC - Command injection]]
│  └─ plantilla / expresión / transformación   → [[MOC - SSTI]] · [[MOC - EL injection]] · [[MOC - XSLT injection]]
├─ Confía en quién digo ser o qué digo poder   → Identidad y acceso ↓
├─ Trae o incluye un recurso que no debía      → [[MOC - SSRF]] · [[MOC - XXE]] · [[MOC - File inclusion]] · [[MOC - File upload]]
├─ Deja ejecutar en el navegador de otro / abusar su confianza  → Cliente ↓
├─ Dos capas leen el mismo mensaje distinto    → Discrepancia de parseo ↓
└─ Su lógica o su estado se puede torcer       → Lógica, estado y objetos ↓
```

Probar es barato: casi todas las familias se confirman con un payload de sondeo. La pregunta del árbol es *qué sondear primero*, no *qué existe*. Antes de atacar, mapear la app: [[MOC - Reconocimiento web]].

## Las familias — un grupo de MOCs cada una

Ordenadas de lo clásico a lo avanzado; dentro de cada una, por dependencia conceptual.

**Inyección — el intérprete ejecuta el dato como código**
- [[MOC - SQL injection]] — inyección SQL
- [[MOC - NoSQL injection]] — inyección de operador, extracción ciega, JavaScript
- [[MOC - LDAP injection]] — manipulación del filtro, salto de autenticación, extracción ciega
- [[MOC - XPath injection]] — manipulación de la consulta XML, salto de autenticación, extracción ciega
- [[MOC - Command injection]] — comandos de SO y argument injection
- [[MOC - EL injection]] — Expression Language de Java: SpEL, OGNL, Struts
- [[MOC - SSTI]] — inyección de plantillas del lado del servidor y del cliente
- [[MOC - XSLT injection]] — lectura y SSRF por `document()`, RCE por funciones de extensión
- [[MOC - CSV injection]] — fórmulas en exports que ejecutan en la planilla del analista

**Identidad y control de acceso**
- [[MOC - Autenticación]] — enumeración, credenciales, MFA, recuperación
- [[MOC - Gestión de sesión]] — tokens, fijación, expiración, JWT
- [[MOC - Broken access control]] — IDOR, escalada vertical, mass assignment
- [[MOC - OAuth]] — `redirect_uri`, `state`, `id_token`, PKCE, registro dinámico
- [[MOC - SAML]] — federación: firma no verificada, envoltura, XXE en el parser

**El servidor trae o incluye algo que no debía**
- [[MOC - SSRF]] — petición forzada desde el servidor
- [[MOC - XXE]] — entidades externas XML
- [[MOC - File inclusion]] — LFI / RFI / path traversal
- [[MOC - File upload]] — subida de archivos → RCE

**Lado cliente y confianza del navegador**
- [[MOC - Cross-site scripting]] — XSS
- [[MOC - CSRF]] — token, `SameSite`, doble envío, API con sesión por cookie
- [[MOC - CORS]] — validación de origen permisiva, lectura de respuestas ajenas
- [[MOC - Clickjacking]] — engaño de interfaz por encuadre; defensa por `frame-ancestors`
- [[MOC - Tabnabbing]] — secuestro de la pestaña abridora por `window.opener`; defensa por `noopener`/COOP
- [[MOC - WebSocket]] — secuestro entre sitios (CSWSH) y abuso del canal de mensajes

**Discrepancia de parseo y cabeceras HTTP**
- [[MOC - Request smuggling]] — desincronización entre frente y back de la cadena HTTP
- [[MOC - Web cache]] — envenenamiento y engaño de la caché compartida
- [[MOC - HTTP parameter pollution]] — parámetros duplicados y discrepancia de parseo entre capas
- [[MOC - CRLF injection]] — inyección de cabecera y división de respuesta HTTP
- [[MOC - Email header injection]] — `Bcc` de exfiltración, spam, falsificación de remitente
- [[MOC - Host header]] — reset poisoning, SSRF por enrutamiento, bypass por confianza en cabeceras

**Lógica, estado y objetos**
- [[MOC - Deserialización]] — manipulación de objeto, gadgets, firma
- [[MOC - Prototype pollution]] — contaminación de prototipos en servidor y cliente
- [[MOC - Race conditions]] — superación de límite, colisión, ataque de un solo paquete
- [[MOC - GraphQL]] — introspección, autorización por resolver, lotes, complejidad

## Orden de aprendizaje

El temario de web sigue el orden de las familias de arriba: inyección primero (fija el modelo "el intérprete ejecuta el dato"), después identidad y acceso, luego lo que el servidor trae, el lado cliente, la discrepancia de parseo, y por último lógica y estado —lo más avanzado, porque presupone entender el flujo normal para torcerlo—.

La teoría que casi toda familia presupone —delimitación, conexión, cabeceras, caché, intermediarios— está en [[MOC - HTTP]] y se lee antes que cualquier familia.

## Relación con otros dominios

- **Reconocimiento.** El mapeo de esta misma superficie, antes de elegir familia, en [[MOC - Reconocimiento web]]; y lo que **encuentra** el servidor web (pre-superficie), en [[MOC - Reconocimiento de red]].
- **Post-explotación.** Varios finales de web desembocan en ejecución: [[MOC - Command injection]] y [[MOC - File upload]] terminan en [[MOC - Shells]] (el webshell es el nodo compartido), y desde ahí en [[MOC - Transferencia de archivos]].

## Huecos conocidos

- [x] Las seis familias, con sus 34 MOCs indexados por mecanismo
- [x] Árbol de triage por *dónde falla la app* — el eje raíz del dominio
- [x] Reconocimiento de la superficie separado a [[MOC - Reconocimiento web]]
- [ ] **Web prácticamente agotado** (34 dominios). Quedan nichos si aparecen: GraphQL subscriptions, JWT algorithm confusion en detalle, prototype pollution en Python/Ruby
- [ ] Sin nota de superficie en `450-superficies/` para web — la superficie está implícita en este hub; se abre si alguna vez hace falta el inventario de tecnologías objetivo
