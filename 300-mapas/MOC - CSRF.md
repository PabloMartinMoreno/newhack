---
tipo: moc
dominio: web
aliases:
  - MOC CSRF
  - falsificación de petición
tags:
  - dominio/web
---

# MOC - CSRF

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-352 - Cross-Site Request Forgery]]. Los payloads, en [[CSRF entrega - matriz de referencia]]. Acá vive **la decisión**.

Este dominio tiene fama de estar muerto, y esa fama hace perder hallazgos. Lo que mató `SameSite` por defecto fue el CSRF **por `POST` desde otro sitio**, que era la única forma que se enseñaba. Las cuatro que quedaron vivas —`GET`, cookies con `SameSite=None`, subdominios y API con sesión por cookie— son justo las que aparecen en aplicaciones modernas.

| Eje | Valores |
|---|---|
| Defensa presente | ninguna · token · doble envío · `SameSite` · `Origin`/`Referer` · tipo de contenido |
| Entrega | `GET` · `POST` autoenviado · `text/plain` con JSON · multipart → matriz |
| Impacto | cambio de estado · toma de cuenta · CSRF de inicio de sesión |

**La entrega va a matriz y no a eje**, mismo criterio que la shell en [[MOC - Command injection]] y el formato en [[MOC - Deserialización]]: cambia el HTML, no cambia ninguna decisión. Lo único que decide es **qué defensa hay que romper**, y por eso el eje de defensa es el único que genera notas.

## Árbol de decisión — qué defensa tengo enfrente

```
¿La sesión viaja por cookie?
├─ No (cabecera Authorization) → no hay CSRF por esta vía
│                                 → mirá CORS reflejado y [[Control de acceso - IDOR]]
└─ Sí
   ├─ ¿Hay token en la petición?
   │  ├─ Sí, y coincide con una cookie del mismo valor
   │  │     → [[CSRF - double submit y cookie inyectada]]
   │  └─ Sí → probá las cinco: sin token, token ajeno, método, vacío, caducado
   │        → [[CSRF - token ausente o no ligado]]      ← SIEMPRE PRIMERO
   ├─ ¿Sin token, y sin Referer pasa?
   │     → [[CSRF - bypass de validación de origen]]
   ├─ ¿El endpoint recibe JSON?
   │     → [[CSRF - endpoint que espera JSON]]
   └─ ¿Nada de lo anterior? La defensa es la cookie
         → [[CSRF - bypass de SameSite]]
```

Tres cosas que este orden codifica:

**La primera pregunta descarta el dominio entero.** Si la sesión no viaja por cookie, el navegador no adjunta nada solo y no hay ataque. Cuesta una petición averiguarlo y evita perder una tarde.

**El token va antes que todo lo demás.** Sus cinco fallos son de implementación y se prueban en cinco peticiones. `SameSite` va último porque romperlo cuesta encontrar un subdominio o cronometrar una ventana.

**`SameSite` no es la primera defensa, es la última.** Se llega ahí cuando la aplicación no implementó nada y lo único que la protege es el comportamiento por defecto del navegador. Es el caso más común hoy y el más frágil de explotar.

## Árbol de decisión — qué vale la pena atacar

```
Encontré la acción vulnerable. ¿Sirve de algo?
├─ Cambia el correo o la contraseña sin pedir la actual  → toma de cuenta
├─ Agrega un segundo factor o una llave de acceso        → toma de cuenta persistente
├─ Cambia permisos o agrega un usuario                   → escalada, ver [[MOC - Broken access control]]
├─ Autentica a la víctima en MI cuenta                   → CSRF de inicio de sesión
│                                                          la actividad queda registrada donde yo la leo
└─ Cambia una preferencia                                → informativo, no lo reportes como crítico
```

El segundo árbol importa más que el primero en este dominio. **La vulnerabilidad es la misma y la severidad va de informativa a crítica según qué acción alcance**, y esa distancia es más grande acá que en cualquier otro dominio del vault. Un CSRF es siempre el mismo fallo; lo que se reporta es la acción.

El CSRF de inicio de sesión es el que más veces se pasa por alto porque parece inofensivo: autenticar a alguien no le saca nada. Lo que hace es que la víctima siga usando la aplicación creyendo que es su cuenta, y todo lo que cargue ahí —una tarjeta, un documento, un historial de búsqueda— queda en una cuenta que el atacante lee cuando quiere.

## Cheatsheets — entrada directa a los payloads

- [[CSRF entrega - matriz de referencia]] — El conjunto de peticiones simples, `GET`, autoenvío, el truco de `text/plain`, `fetch` con credenciales
- [[CSRF bypass - matriz de referencia]] — Qué probar contra cada defensa en orden de coste, y qué recomendar en el informe

## Orden de aprendizaje

1. [[CWE-352 - Cross-Site Request Forgery]] — por qué la intención no viaja en el protocolo
2. [[CSRF - token ausente o no ligado]] — los cinco fallos del token, que son el 80% de los hallazgos
3. [[CSRF entrega - matriz de referencia]] — qué manda el navegador sin pedir permiso, que es el límite real del dominio
4. [[CSRF - bypass de validación de origen]] — la defensa de segunda línea usada como primera
5. [[CSRF - bypass de SameSite]] — qué queda vivo con el comportamiento por defecto de 2026
6. [[CSRF - double submit y cookie inyectada]] — por qué las cookies no respetan el mismo origen
7. [[CSRF - endpoint que espera JSON]] — la forma que toma el dominio en aplicaciones de página única

El punto 3 va en el medio y no al final a propósito: sin entender qué peticiones el navegador manda sin preguntar, las cuatro ramas siguientes parecen trucos sueltos en vez de consecuencias de una sola regla.

## Relación con otros dominios

- [[MOC - Cross-site scripting]] — **un XSS en el mismo origen anula toda defensa de CSRF**. El token se lee del DOM, la cookie viaja porque la petición ya no es cruzada, y `SameSite` no aplica. Si hay XSS, no hace falta este dominio; y al revés, la única defensa que sobrevive a un XSS es la reautenticación.
- [[MOC - Broken access control]] — son el mismo problema visto de dos lados: allá la petición la manda quien no debe, acá la manda quien debe pero no quiso. La telemetría es la misma y las dos dependen de [[Log de auditoría de la aplicación]].
- [[MOC - Gestión de sesión]] — el CSRF de inicio de sesión es primo de [[Sesión - fijación]]: en los dos casos la víctima termina operando en una sesión que eligió el atacante.
- [[MOC - File upload]] — un CSRF con `multipart/form-data` llega a un endpoint de subida sin que la víctima elija el archivo.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Token ausente o no ligado | [[Log de acceso del servidor web]] | Ráfaga de `403` con token inválido durante la prueba |
| Bypass de `SameSite` | [[Log de acceso del servidor web]] | Acción que cambia estado servida por `GET`, con `Referer` externo |
| Bypass de origen | [[Log de acceso del servidor web]] | `Referer` ausente sobre acción de escritura — **fidelidad baja por sí sola** |
| Doble envío | [[Log de acceso del servidor web]] | Petición al subdominio inmediatamente antes de la acción |
| Endpoint JSON | [[Registro del WAF]] | Tipo de contenido que el cliente propio nunca manda |
| Todas | [[Log de auditoría de la aplicación]] | La acción **sin la navegación previa que siempre la precede** |

Dos observaciones que este dominio deja claras:

**Ninguna detección propia hizo falta.** Es el tercer dominio que se cierra reutilizando reglas existentes: [[Cambio de privilegio fuera del flujo administrativo]] cubre el impacto que importa, porque un CSRF exitoso produce exactamente eso — un cambio de estado sin el flujo que debería precederlo. La regla no sabe que hubo CSRF y no le hace falta.

**La única firma propia del dominio es una ausencia**, y las ausencias detectan mal. Un `Referer` faltante es normal en marcadores, clientes de correo y configuraciones de privacidad. Sola no alerta; combinada con "acción de escritura sin navegación previa" pasa a ser un invariante sobre la secuencia, y esa es la forma correcta. Ver [[Detección por forma - matriz de referencia]] § 4.

## Huecos conocidos

- [x] Las cinco defensas y cómo se rompe cada una
- [x] Entrega y payloads — en [[CSRF entrega - matriz de referencia]]
- [x] Cara azul — cubierta por [[Cambio de privilegio fuera del flujo administrativo]], sin reglas nuevas
- [ ] **La rama de `SameSite` caduca.** Depende del navegador, no de la aplicación. La ventana de gracia ya se recortó una vez y está anunciada para desaparecer — reconfirmar antes de usarla
- [ ] CORS mal configurado como dominio propio: origen reflejado, `null` aceptado, comparación por subcadena. Es el vecino de este MOC y responde otra pregunta —leer en vez de escribir—, así que va aparte
- [x] CSRF sobre WebSocket — [[MOC - WebSocket]], con `CWE-1385` propia. Es el secuestro del handshake, donde no hay control previo ni `SameSite` que valga, y el canal queda bidireccional
