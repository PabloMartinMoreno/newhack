---
tipo: meta
aliases:
  - reconocimiento OAuth
  - well-known openid-configuration
  - flujos de OAuth
tags:
  - meta/referencia
  - dominio/web
---

# OAuth - matriz de reconocimiento

> [!info] Referencia pura, no un zettel
> Identificar el flujo y los parámetros antes de atacar nada. Los payloads están en [[OAuth redirect_uri - matriz de referencia]] y [[OAuth tokens - matriz de referencia]]; el criterio, en [[MOC - OAuth]].

## 1. El documento de descubrimiento

Es la primera petición del dominio y devuelve el mapa entero.

`https://proveedor/.well-known/openid-configuration`
`https://proveedor/.well-known/oauth-authorization-server`

```sh
curl -s https://proveedor/.well-known/openid-configuration | jq
```

| Campo | Para qué sirve |
|---|---|
| `authorization_endpoint` | Donde se manda a la víctima |
| `token_endpoint` | Donde se canjea el código |
| `jwks_uri` | Las claves públicas — para verificar y para forjar |
| `registration_endpoint` | **Si está, hay registro dinámico** → [[OAuth - SSRF por registro dinámico]] |
| `userinfo_endpoint` | Consulta de identidad con el token de acceso |
| `response_types_supported` | Si aparece `token` o `id_token`, hay flujo implícito |
| `code_challenge_methods_supported` | Si falta, no hay PKCE. Si dice `plain`, es degradable |
| `scopes_supported` | Qué se puede pedir de más |
| `token_endpoint_auth_methods_supported` | `none` significa clientes públicos sin secreto |

`jq -r '.registration_endpoint, .code_challenge_methods_supported'`
Los dos que deciden ramas enteras. Vale sacarlos primero.

## 2. Identificar el flujo

Se mira la URL de autorización que arma el cliente.

| `response_type` | Flujo | Qué vuelve y por dónde |
|---|---|---|
| `code` | Código de autorización | Código en la query. El canje es servidor a servidor |
| `token` | Implícito | Token de acceso en el **fragmento** → [[OAuth - flujo implícito y token no verificable]] |
| `id_token` | Implícito de OIDC | `id_token` en el fragmento |
| `id_token token` | Híbrido | Los dos en el fragmento |
| `code id_token` | Híbrido | Código en la query, `id_token` en el fragmento |

Lo que viaja en el **fragmento** no llega al servidor: lo lee JavaScript en el navegador. Esa distinción decide si el ataque es contra el canal o contra el cliente.

## 3. Parámetros de la petición de autorización

```http
GET /authorize
  ?client_id=abc123
  &redirect_uri=https://cliente.com/callback
  &response_type=code
  &scope=openid%20email%20profile
  &state=xyz
  &nonce=789
  &code_challenge=...
  &code_challenge_method=S256
```

| Parámetro | Ausente significa |
|---|---|
| `state` | Sin protección anti-CSRF → [[OAuth - falta de state]] |
| `nonce` | El `id_token` se puede reusar |
| `code_challenge` | Sin PKCE → [[OAuth - PKCE ausente o degradado]] |
| `code_challenge_method` | Por defecto `plain`, que no protege |

Presente pero no validado vale lo mismo que ausente, y se comprueba cambiándole el valor: si el flujo termina bien con un `state` distinto del que se emitió, no se valida.

## 4. Las cinco pruebas de apertura

Cuestan una petición cada una y descartan o abren cada rama.

| Prueba | Si pasa |
|---|---|
| `redirect_uri` a un dominio propio | Validación laxa → [[OAuth - redirect_uri mal validado]] |
| `state` con valor cambiado | No se valida → [[OAuth - falta de state]] |
| `response_type=code` → `token` | Hay flujo implícito disponible |
| `code_challenge_method=S256` → `plain` | PKCE degradable |
| `POST` al registro dinámico | Registro abierto → [[OAuth - SSRF por registro dinámico]] |

```sh
curl -si "https://proveedor/authorize?client_id=abc&redirect_uri=https://mi-host/&response_type=code" | head -20
```

Leer el `Location` de la respuesta: si redirige a `mi-host` con un código, la rama está abierta.

## 5. Alcances — pedir de más

`scope=openid email profile`
Lo normal.

`scope=openid email profile offline_access`
`offline_access` devuelve un token de refresco, que no caduca con la sesión. Vale probarlo siempre: muchos servidores lo conceden sin que el cliente lo pida.

`scope=openid email profile admin`
`scope=openid email profile read:all`

Un alcance concedido que el cliente nunca pide es un hallazgo por sí solo: el consentimiento que ve la víctima no refleja lo que el token permite.

## 6. Dónde vive cada cosa en el tráfico

Al interceptar el flujo completo hay que ubicar cuatro momentos:

1. **El cliente arma la URL de autorización** — acá se ven `redirect_uri`, `state`, PKCE.
2. **La víctima consiente** en el proveedor.
3. **Vuelve al cliente** con el código o el token — acá está lo que se puede desviar.
4. **El cliente canjea** contra el `token_endpoint` — servidor a servidor, no se ve desde el navegador salvo en flujos públicos.

El paso 4 es el que decide si el cliente es confidencial o público. Si el canje pasa por el navegador, es público y no hay secreto que valga.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `invalid_request: redirect_uri mismatch` | Validación estricta. Buscar redirección abierta en el dominio registrado |
| `unauthorized_client` | Ese `response_type` no está habilitado para ese cliente |
| `invalid_scope` | El alcance no existe o no está permitido |
| `invalid_grant` en el canje | El código caducó, ya se usó, o falta `code_verifier` |
| El flujo termina y no hay sesión | El cliente validó algo que el proveedor no. Mirar la petición final del cliente |
| El código no canjea desde otro contexto | Está atado al cliente y a la dirección |
| `.well-known` devuelve `404` | Proveedor sin descubrimiento. Sacar los endpoints del tráfico |
| Todo funciona con `state` cambiado | No se valida. Rama abierta |

## Relacionadas

[[MOC - OAuth]] · [[OAuth redirect_uri - matriz de referencia]] · [[OAuth tokens - matriz de referencia]] · [[JWT - matriz de referencia]]
