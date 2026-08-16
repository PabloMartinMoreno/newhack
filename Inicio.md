---
tipo: meta
aliases:
  - Home
tags: []
---

# Inicio

Vault único **rojo + azul**. La técnica agrupa; la telemetría une. Ver [[Estructura del vault]].

## Mapas

**Web**
- [[MOC - SQL injection]] — inyección SQL
- [[MOC - Cross-site scripting]] — XSS
- [[MOC - File inclusion]] — LFI / RFI / path traversal
- [[MOC - File upload]] — subida de archivos → RCE
- [[MOC - Command injection]] — comandos de SO y argument injection
- [[MOC - SSRF]] — petición forzada desde el servidor
- [[MOC - XXE]] — entidades externas XML
- [[MOC - Broken access control]] — IDOR, escalada vertical, mass assignment
- [[MOC - Autenticación]] — enumeración, credenciales, MFA, recuperación
- [[MOC - Gestión de sesión]] — tokens, fijación, expiración, JWT
- [[MOC - Deserialización]] — manipulación de objeto, gadgets, firma
- [[MOC - CSRF]] — token, `SameSite`, doble envío, API con sesión por cookie
- [[MOC - SSTI]] — inyección de plantillas del lado del servidor y del cliente
- [[MOC - OAuth]] — `redirect_uri`, `state`, `id_token`, PKCE, registro dinámico
- [[MOC - Prototype pollution]] — contaminación de prototipos en servidor y cliente
- [[MOC - CORS]] — validación de origen permisiva, lectura de respuestas ajenas
- [[MOC - SAML]] — federación: firma no verificada, envoltura, XXE en el parser
- [[MOC - EL injection]] — Expression Language de Java: SpEL, OGNL, Struts
- [[MOC - Request smuggling]] — desincronización entre frente y back de la cadena HTTP
- [[MOC - Web cache]] — envenenamiento y engaño de la caché compartida
- [[MOC - GraphQL]] — introspección, autorización por resolver, lotes, complejidad
- [[MOC - NoSQL injection]] — inyección de operador, extracción ciega, JavaScript
- [[MOC - Race conditions]] — superación de límite, colisión, ataque de un solo paquete
- [[MOC - WebSocket]] — secuestro entre sitios (CSWSH) y abuso del canal de mensajes
- [[MOC - LDAP injection]] — manipulación del filtro, salto de autenticación, extracción ciega
- [[MOC - XPath injection]] — manipulación de la consulta XML, salto de autenticación, extracción ciega
- [[MOC - Host header]] — reset poisoning, SSRF por enrutamiento, bypass por confianza en cabeceras
- [[MOC - CRLF injection]] — inyección de cabecera y división de respuesta HTTP

**Azul**
- [[MOC - Fundamentos de detección]] — los conceptos transversales. **Empezar acá si venís de rojo**
- [[MOC - Telemetría de Windows]] — qué ve cada fuente, qué cuesta, qué no ve

**Infra / AD**
- [[MOC - Active Directory]] — enumeración, roasting, movimiento lateral, persistencia. Cara azul en Telemetría de Windows

> Al cerrar un dominio nuevo, agregar su MOC acá.

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
