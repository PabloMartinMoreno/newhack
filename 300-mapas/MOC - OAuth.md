---
tipo: moc
dominio: web
aliases:
  - MOC OAuth
  - OIDC
  - OpenID Connect
tags:
  - dominio/web
---

# MOC - OAuth

> [!abstract] Nota de referencia paraguas
> Reconocer el flujo, en [[OAuth - matriz de reconocimiento]]. Acá vive **la decisión**.

Este es el primer dominio del vault que **no tiene CWE propia**. OAuth no es una vulnerabilidad: es un protocolo con seis puntos donde se rompen cosas distintas, y cada uno tiene su clase.

| Fase rota | `clase:` | Nota |
|---|---|---|
| La redirección de vuelta | `CWE-601` | [[OAuth - redirect_uri mal validado]] |
| La protección anti-CSRF del flujo | `CWE-352` | [[OAuth - falta de state]] |
| La confianza en datos no verificables | `CWE-287` | [[OAuth - flujo implícito y token no verificable]] |
| La verificación de la firma | `CWE-347` | [[OAuth - validación del id_token]] |
| La atadura del código a quien lo pidió | `CWE-287` | [[OAuth - PKCE ausente o degradado]] |
| Las descargas del servidor de autorización | `CWE-918` | [[OAuth - SSRF por registro dinámico]] |

Esa tabla **es** la regla 7 del `CLAUDE.md` funcionando: la `clase:` es la vulnerabilidad, no el vector. Solo una técnica hizo falta escribir —[[CWE-601 - URL Redirection to Untrusted Site]]—; las otras cinco ya existían por otros dominios. La navegación no sufre, porque se llega por acá.

| Eje | Valores |
|---|---|
| Fase del flujo | redirección · `state` · datos no verificables · firma · PKCE · registro dinámico |
| Rol atacado | el cliente · el servidor de autorización |
| Flujo | código · implícito · híbrido → matriz |
| Impacto | cuenta ajena · vinculación forzada · red interna del proveedor |

El **flujo va a matriz y no a eje**, mismo criterio que el motor en [[MOC - SQL injection]]: cambia qué parámetros hay y por dónde vuelven los datos, no cambia qué se decide.

## Árbol de decisión — qué fase rompo

```
¿Quién es el objetivo?
├─ El servidor de autorización
│  └─ ¿Hay registration_endpoint en el .well-known?
│     └─ Sí → [[OAuth - SSRF por registro dinámico]]
│             no necesita víctima, y el proveedor suele estar en el interior
└─ El cliente
   │
   ├─ 1. ¿La identidad viaja como parámetro en la petición final?
   │     → [[OAuth - flujo implícito y token no verificable]]   ← PROBAR PRIMERO
   │       una petición, sin interacción de la víctima, sin ruido
   │
   ├─ 2. ¿Falta state, o no se valida?
   │     → [[OAuth - falta de state]]
   │       barato, pero necesita que la víctima abra un enlace
   │
   ├─ 3. ¿redirect_uri acepta algo que no sea la registrada?
   │  ├─ Sí → [[OAuth - redirect_uri mal validado]]
   │  └─ No → ¿hay redirección abierta en el dominio registrado?
   │          └─ Sí → misma nota, vía § 9 de la matriz
   │
   ├─ 4. ¿Hay id_token y el cliente lo procesa a mano?
   │     → [[OAuth - validación del id_token]]
   │
   └─ 5. ¿Hay forma de VER el código?
         ├─ No → PKCE no aplica, la rama es teórica
         └─ Sí → [[OAuth - PKCE ausente o degradado]]
```

Tres cosas que este orden codifica:

**Primero lo que no necesita víctima.** Las ramas 1 y la del servidor de autorización se prueban solas; las ramas 2 y 3 dependen de que alguien abra un enlace, y eso pone un techo a la severidad que hay que reflejar en el informe. Ordenar por impacto en vez de por requisito lleva a construir cadenas que no se pueden demostrar.

**PKCE va último y con una condición previa.** No protege contra el desvío de la redirección: protege el código **en tránsito**. Sin una primitiva para ver el código, la rama no existe. Es la confusión más común del dominio.

**La redirección abierta del propio cliente vale tanto como una validación laxa.** El código llega a la dirección correcta y el cliente lo reenvía. Nadie la busca porque no está en la implementación de OAuth, y en aplicaciones grandes es la vía que más veces resuelve.

## Árbol de decisión — conseguí algo, ¿hasta dónde llega?

```
¿Qué obtuve?
├─ Código de autorización de la víctima
│  ├─ ¿Canjea? → sesión completa de la víctima
│  └─ ¿No canjea? → está atado al cliente. Buscar el secreto o registrar un cliente propio
├─ id_token forjado o ajeno
│  └─ sesión completa, sin contraseña ni segundo factor
├─ Vinculación forzada
│  └─ entro con MI identidad social a SU cuenta. Persistente hasta que la desvinculen
├─ Token de acceso
│  ├─ ¿Qué alcances trae? Mirar la respuesta del canje, no la pantalla de consentimiento
│  └─ ¿Vino offline_access? → token de refresco: sobrevive al cierre de sesión
│                              → [[Sesión - expiración insuficiente]]
└─ SSRF desde el proveedor
   └─ [[MOC - SSRF]]: metadatos de instancia primero, red interna después
```

El token de refresco es el que se subestima. Un `offline_access` concedido sin que el cliente lo pida convierte un acceso momentáneo en persistencia, y la víctima no lo corta cerrando sesión.

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[OAuth - matriz de reconocimiento]] | El documento de descubrimiento, identificar el flujo, las cinco pruebas de apertura, alcances |
| [[OAuth redirect_uri - matriz de referencia]] | Prefijo, sufijo, recorrido, comodín, confusión del analizador, codificación, redirección abierta del cliente |
| [[OAuth tokens - matriz de referencia]] | `id_token` campo por campo, `alg: none`, confusión de algoritmo, `jku`, canje, PKCE, alcances |

## Orden de aprendizaje

1. [[OAuth - matriz de reconocimiento]] — el flujo antes que cualquier ataque, y acá sí va primero la matriz
2. [[OAuth - flujo implícito y token no verificable]] — por qué "vino del proveedor" no significa nada
3. [[OAuth - falta de state]] — CSRF aplicado al flujo, y la inversión de que se **entrega** un código en vez de robarlo
4. [[OAuth - redirect_uri mal validado]] — la rama de mayor impacto
5. [[OAuth - validación del id_token]] — las cinco comprobaciones que casi nadie hace enteras
6. [[OAuth - PKCE ausente o degradado]] — qué protege y qué no
7. [[OAuth - SSRF por registro dinámico]] — el dominio dado vuelta: el proveedor como objetivo

Es el único MOC del vault donde la matriz va **primera** en el orden de lectura. El motivo es que sin identificar el flujo las seis ramas son indistinguibles entre sí, y la lectura de los parámetros es lo que las separa.

## Relación con otros dominios

- [[MOC - CSRF]] — [[OAuth - falta de state]] es literalmente un CSRF, con la misma `clase:` y la misma detección. La única diferencia es qué se consigue.
- [[MOC - Gestión de sesión]] — [[OAuth - validación del id_token]] comparte mecánica con [[Sesión - falsificación de JWT]] y su matriz. El token de refresco se cruza con [[Sesión - expiración insuficiente]].
- [[MOC - SSRF]] — [[OAuth - SSRF por registro dinámico]] entra ahí después del primer paso. El orden de destinos es el de aquel MOC, no el de este.
- [[MOC - Autenticación]] — este dominio es el mecanismo de autenticación cuando la delega a un tercero. Todo lo de contraseñas y segundo factor de allá **se saltea** cuando alguna de estas ramas funciona, y eso conviene decirlo explícito en el informe.
- [[CWE-601 - URL Redirection to Untrusted Site]] — la redirección abierta pasa de hallazgo informativo a crítico según qué transporte la redirección.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| `redirect_uri` mal validado | [[Log de autenticación de la aplicación]] | Ráfaga de autorizaciones con direcciones no registradas — **en el proveedor** |
| `redirect_uri` mal validado | [[Log de acceso del servidor web]] | Canje del código desde un origen inusual |
| Falta de `state` | [[Log de auditoría de la aplicación]] | Identidad externa vinculada sin pasar por configuración |
| Flujo implícito | [[Log de autenticación de la aplicación]] | La identidad autenticada no coincide con la del token — **si se registran las dos** |
| Validación del `id_token` | [[Conexión saliente del servidor de aplicación]] | Descarga de claves desde un servidor que no es el proveedor |
| PKCE degradado | [[Log de autenticación de la aplicación]] | `plain` donde el cliente usa `S256` — necesita línea base |
| SSRF por registro | [[Conexión saliente del servidor de aplicación]] | Petición del proveedor a destino elegido por un tercero |

Dos observaciones que este dominio deja claras, y son incómodas:

**La telemetría útil está en el otro extremo del flujo.** Cuatro de las siete firmas viven en el registro del **proveedor de identidad**, que casi nunca es el sistema auditado. Es el primer dominio del vault donde la mejor fuente pertenece a un tercero, y el informe tiene que decirlo: sin acceso a los registros del proveedor, la mitad del dominio es ciega por construcción.

**Tres ramas dependen de un campo que casi nadie instrumenta.** Detectar el flujo implícito y la validación del `id_token` exige registrar el **sujeto del token junto al usuario autenticado**. Si la aplicación distinguiera ambos valores, no sería vulnerable — o sea que la ausencia del campo es a la vez la vulnerabilidad y el motivo por el que no se detecta. Es el mismo patrón que [[Un log sin identidad es un historial, no una detección]], en su forma más pura.

Ninguna detección propia hizo falta: es el quinto dominio que se cierra reutilizando reglas. [[Cambio de privilegio fuera del flujo administrativo]] cubre la vinculación forzada, [[Misma sesión desde dos orígenes]] el código robado, y [[Petición al servicio de metadatos de instancia]] el SSRF del proveedor.

## Huecos conocidos

- [x] Las seis fases del flujo, cada una con su `clase:` real
- [x] Reconocimiento, `redirect_uri` y tokens — tres matrices
- [x] Cara azul — cubierta por detecciones existentes, sin reglas nuevas
- [ ] **El registro de clientes no está modelado como artefacto.** Una ráfaga de registros dinámicos con direcciones que no pertenecen al cliente declarado es buena señal y ninguna detección la ve, porque `550-telemetria/` no tiene esa fuente
- [ ] SAML como alternativa de federación: mismo lugar en la arquitectura, ejes distintos —firma XML, envoltura, [[MOC - XXE]] por el parser—. Dominio propio
- [ ] Concesión de credenciales de cliente y flujo de dispositivo, que no tienen víctima ni navegador
- [ ] Confusión de proveedor cuando el cliente acepta varios emisores
