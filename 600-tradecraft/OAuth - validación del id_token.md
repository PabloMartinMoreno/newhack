---
tipo: tradecraft
clase: "[[CWE-347 - Improper Verification of Cryptographic Signature]]"
eje: fase-del-flujo
implementacion: "Forjar o reusar un id_token que el cliente acepta por no comprobar firma, emisor, audiencia o nonce"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Conexión saliente del servidor de aplicación]]"]
requisitos: [openid-connect, validacion-incompleta-en-el-cliente]
coste: medio
alternativas: ["[[OAuth - flujo implícito y token no verificable]]", "[[Sesión - falsificación de JWT]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - id_token
  - OIDC validation bypass
tags:
  - dominio/web
---

# OAuth - validación del id_token

## Cuándo lo elijo

Cuando el flujo es OpenID Connect —hay un `id_token`, no solo un token de acceso— y el cliente lo procesa por su cuenta en vez de delegarlo a una biblioteca conocida. La señal es que el `id_token` aparece en el tráfico y sus campos se reflejan en la sesión resultante.

Va después de [[OAuth - flujo implícito y token no verificable]], porque aquella cuesta una petición y esta cuesta varias. Si el cliente no verifica nada en absoluto, se resuelve allá.

## Por qué funciona

Un `id_token` es un JWT firmado por el proveedor, y verificarlo bien exige **cinco comprobaciones**, no una. Las bibliotecas serias las hacen todas; las integraciones a mano hacen dos o tres.

| Comprobación | Qué pasa si falta |
|---|---|
| Firma válida | Se forja el token entero. `alg: none`, o firmar con la clave pública como secreto |
| `iss` — emisor | Se acepta un token de otro proveedor, incluido uno del atacante |
| `aud` — audiencia | Se acepta un token emitido para otra aplicación |
| `nonce` | Se reusa un token capturado. Es la protección contra repetición |
| `exp` — expiración | Se reusa un token viejo indefinidamente |

Las tres primeras son las que dan cuenta ajena directamente. La mecánica de forjar la firma es la misma que en [[Sesión - falsificación de JWT]] y su matriz cubre los payloads; lo específico de este dominio son las otras dos.

Hay además una vía que no depende de romper la firma y que rinde más de lo que parece: **el campo `jku` o `jwks_uri`**. Si el cliente descarga la clave pública desde una dirección que viene en el propio token, se le puede indicar un servidor del atacante, firmar con una clave propia y quedar con un token técnicamente válido. Del lado del servidor, esa misma descarga es un SSRF — ver [[OAuth - SSRF por registro dinámico]].

Y la más aburrida y más frecuente: **confiar en `email` sin mirar `email_verified`**. Se registra una cuenta en el proveedor con el correo de la víctima sin verificarlo, y el cliente la trata como la misma persona.

## Cómo falla

Falla contra cualquier biblioteca de OpenID Connect mantenida, que hace las cinco comprobaciones y descarga las claves del documento de descubrimiento en vez de del token.

Falla contra `alg` fijado del lado del cliente, que es la mitigación correcta contra la confusión de algoritmo: no aceptar el que el token propone.

Y falla cuando el proveedor es uno de los grandes y el cliente usa su SDK oficial. Esta rama rinde en integraciones propias, en proveedores internos y en aplicaciones que implementaron OIDC "porque son cuatro campos".

## Coste

Medio. Cada comprobación se prueba con un token modificado y una petición, así que son cinco o seis peticiones bien dirigidas. Preparar los tokens lleva más tiempo que mandarlos.

El coste sube si hay que montar un servidor de claves propio para la vía de `jku`, que es media hora de trabajo y solo vale la pena si las cinco comprobaciones básicas ya fallaron.

## Huella esperada

Casi nada del lado del cliente, y de ahí el `opsec: limpio`. Un token forjado que el cliente acepta produce un inicio de sesión indistinguible de uno legítimo: el registro dice que la persona se autenticó con OpenID Connect, porque desde el punto de vista de la aplicación eso fue lo que pasó.

La única señal aprovechable es un desajuste que exige guardar más de lo que se guarda: **un `id_token` cuyo emisor o audiencia no son los esperados**, o un `nonce` repetido. Vale lo mismo que en [[OAuth - flujo implícito y token no verificable]] — si la aplicación registrara esos campos, probablemente los estaría validando.

Hay un caso que sí deja rastro y conviene buscar: la vía de `jku` genera una **conexión saliente del cliente hacia un servidor de claves que no es el del proveedor**. Eso lo ve [[Conexión saliente del servidor de aplicación]] y lo cubre la misma detección de barrido y destinos anómalos, sin saber que hubo un JWT de por medio.

Del lado del proveedor no queda nada: el token forjado nunca se le pidió.
