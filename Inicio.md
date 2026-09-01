---
tipo: meta
aliases:
  - Home
tags: []
---

# Inicio

Vault único **rojo + azul**. La técnica agrupa; la telemetría une. Ver [[Estructura del vault]].

## Mapas

### Fundamentos

El sustrato que los ataques presuponen. Va primero porque casi ningún dominio ataca al protocolo: atacan el desacuerdo entre dos lecturas del mismo mensaje, y ese desacuerdo no se ve sin la teoría. Se leen de abajo hacia arriba.
- [[MOC - Red]] — ARP, ICMP y TCP: el segmento como frontera, y de dónde sale cada estado del escaneo
- [[MOC - HTTP]] — delimitación, conexión, cabeceras, caché, intermediarios

### Web

Dentro de web, los MOCs están por **mecanismo**, no por nombre: la pregunta que abre cada familia es dónde falla la aplicación, no cómo se llama el bug. El orden va de lo clásico a lo avanzado.

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

### Active Directory

Una sola kill chain. El [[MOC - Active Directory]] es el **hub** —el árbol *lo que tenés → qué se abre* y la bisagra roja↔azul—; cada fase es un MOC propio, con su matriz de comandos adentro.
- [[MOC - Active Directory]] — el hub: árbol maestro y cara azul
- [[MOC - AD envenenamiento y relay]] — sin credencial: primer hash y reenvío
- [[MOC - AD enumeración]] — el directorio como base de datos; siempre primero
- [[MOC - AD roasting]] — AS-REP y Kerberoast, se rompen fuera de línea
- [[MOC - AD volcado de credenciales]] — LSASS, SAM, NTDS, DCSync
- [[MOC - AD movimiento lateral]] — pass-the-hash / ticket; NTLM contra Kerberos
- [[MOC - AD delegaciones]] — sin restricciones, restringida, RBCD
- [[MOC - ADCS]] — la PKI que emite identidad, `ESC1`–`ESC15`
- [[MOC - AD persistencia]] — golden, SID History, certificado
- [[MOC - AD confianzas]] — del dominio al bosque

### Azul

La técnica agrupa el rojo; acá se agrupa por lo que la *ve*.
- [[MOC - Fundamentos de detección]] — los conceptos transversales. **Empezar acá si venís de rojo**
- [[MOC - Telemetría de Windows]] — qué ve cada fuente, qué cuesta, qué no ve. Cara azul de AD

> Al cerrar un dominio nuevo, agregar su MOC a la familia que corresponda.

## Estado del vault

Las consultas cruzadas no se leen acá: se corren. `<leader>oc` abre el menú, o desde la terminal:

```sh
900-meta/consultas.py todo
```

Las dos de rutina:

| Comando | Responde |
|---|---|
| `revalidacion` | Qué tradecraft lleva más de seis meses sin probar |
| `higiene` | Frontmatter inválido y enlaces rotos |

Las siete están explicadas en [[Consultas del vault]].

## Cómo se usa esto

[[Recorrido del vault en nvim]] — entrar, encontrar, leer, escribir, mantener.

## Administración

[[Estructura del vault]] · [[Esquema de frontmatter]] · [[Convenciones de nombres]] · [[Consultas del vault]] · [[Puesta a punto de Obsidian]] · [[Avances]]
