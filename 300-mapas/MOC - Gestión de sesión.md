---
tipo: moc
dominio: web
aliases:
  - MOC sesión
  - Session management
tags:
  - dominio/web
---

# MOC - Gestión de sesión

> [!abstract] Nota de referencia paraguas
> Las definiciones viven en [[CWE-384 - Session Fixation]], [[CWE-330 - Use of Insufficiently Random Values]], [[CWE-613 - Insufficient Session Expiration]], [[CWE-522 - Insufficiently Protected Credentials]] y [[CWE-347 - Improper Verification of Cryptographic Signature]]. Acá vive **la decisión**.
>
> Lo que pasa **antes** de entrar es [[MOC - Autenticación]]. Este dominio empieza en el momento en que se emite la sesión.

Todo el dominio se apoya en una sola premisa: **el token es la identidad**. El servidor no distingue quién lo presenta; cualquiera que lo tenga es el usuario. Las cuatro ramas del árbol son las cuatro formas de conseguir un token que el servidor acepte.

| Eje | Valores |
|---|---|
| Mecanismo | cookie opaca de servidor · JWT sin estado · token en almacenamiento del navegador |
| Fallo | predecible · fijable · robable · no expira · firma no verificada |
| Vector de robo | XSS · red · referencia y registros · subdominio |
| Obstáculo | `HttpOnly` · `Secure` · `SameSite` · prefijos · rotación · vinculación |
| Impacto | suplantación · persistencia tras la reacción defensiva · escalada |

## Árbol de decisión — cómo consigo un token válido

```
¿Qué tipo de token es?
├─ JWT
│  ├─ ¿Se verifica la firma? → [[Sesión - falsificación de JWT]]   ← da CUALQUIER cuenta
│  └─ Sí, bien → tratarlo como opaco, seguir abajo
└─ Opaco
   ├─ ¿Tiene estructura predecible? → [[Sesión - token predecible]]  ← no necesita víctima
   ├─ ¿Es alcanzable? (XSS, red, URL, subdominio) → [[Sesión - robo de token]]
   └─ ¿No rota al autenticar? → [[Sesión - fijación]]
```

El orden es por **independencia de la víctima**, que es lo que decide la viabilidad real:

**Falsificar no necesita a nadie** y da cualquier cuenta, incluidas las administrativas. Es la rama de mayor impacto.

**Predecir tampoco necesita víctima** y escala sola: quien predice una, predice todas. Sale pocas veces, y por eso se descarta rápido con una muestra chica.

**Robar necesita otra vulnerabilidad** — es el impacto de un XSS más que una técnica propia.

**Fijar necesita que la víctima se autentique después**, lo que implica ingeniería social y una ventana de tiempo. Es la más cara de las cuatro en la práctica.

## Árbol de decisión — ya tengo el token, ¿cuánto dura?

```
¿Qué sobrevive?
├─ ¿El cierre de sesión?          → [[Sesión - expiración insuficiente]]
├─ ¿El cambio de contraseña?      → el caso grave
├─ ¿El cambio de rol o de MFA?    → privilegio congelado
└─ ¿Hay vencimiento absoluto?
```

Esta rama no da acceso: da **permanencia**, y por eso se prueba siempre aunque el acceso venga de otro lado. La pregunta que responde es si el compromiso sobrevive a la reacción de la víctima.

El caso del cambio de contraseña es el que hay que destacar en un informe: si no invalida las sesiones activas, la acción defensiva más elemental que existe queda anulada **en silencio**. El usuario cree que cerró el problema y el atacante sigue adentro.

## Árbol de decisión — el token es un JWT

```
Orden por coste de descarte:
├─ ¿se verifica la firma?   1 petición
├─ alg: none                1 petición
├─ confusión HS/RS          necesita la clave pública
├─ jwk / jku / kid          necesita infraestructura o inyección
├─ afirmaciones (exp/iss/aud)  1 petición cada una
└─ secreto débil            caro, fuera de línea, último
```

Las tres primeras son tres peticiones y cubren la mayor parte de lo explotable. Si fallan y la biblioteca es moderna, lo que queda son las **afirmaciones** — donde más veces hay algo y donde menos gente mira: un token legítimo emitido para otra aplicación del mismo proveedor de identidad es un token legítimo.

## Cheatsheets

| Matriz | Cubre |
|---|---|
| [[Sesión - matriz de referencia]] | Atributos de cookie y prefijos, análisis del token, pruebas de fijación, expiración y concurrencia |
| [[JWT - matriz de referencia]] | Lectura del token, `none`, confusión de algoritmo, claves provistas, `kid` como inyección, afirmaciones, secreto débil |

## Orden de aprendizaje

1. [[MOC - Autenticación]] — de dónde viene la sesión
2. [[CWE-522 - Insufficiently Protected Credentials]] → [[Sesión - robo de token]] — la premisa: el token es la identidad
3. [[CWE-384 - Session Fixation]] → [[Sesión - fijación]] — el ciclo de vida, no la confidencialidad
4. [[CWE-330 - Use of Insufficiently Random Values]] → [[Sesión - token predecible]]
5. [[CWE-347 - Improper Verification of Cryptographic Signature]] → [[Sesión - falsificación de JWT]]
6. [[CWE-613 - Insufficient Session Expiration]] → [[Sesión - expiración insuficiente]] — permanencia, no acceso

El punto 3 va temprano porque rompe una intuición: los atributos de cookie protegen la **confidencialidad** del token y no hacen nada contra un ataque sobre su **ciclo de vida**. `HttpOnly` impide leer la cookie; no impide ponerla.

## Relación con otros dominios

- [[MOC - Autenticación]] — el par encadenado. Aquel termina donde se emite la sesión; este empieza ahí.
- [[MOC - Cross-site scripting]] — es la fuente principal de [[Sesión - robo de token]]. El robo es el impacto y el XSS la causa: se reportan encadenados.
- [[MOC - Broken access control]] — el token de recuperación no atado a la cuenta y el JWT con `sub` alterado son el mismo fallo de autorización visto desde otro lado.
- [[MOC - SQL injection]] y [[MOC - File inclusion]] — la cabecera `kid` de un JWT suele terminar en una consulta o en una ruta de archivo. Es un punto de inyección que casi nadie prueba.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Robo | [[Log de autenticación de la aplicación]] | **La misma sesión desde dos orígenes** — la detección de mayor retorno |
| Fijación | [[Log de autenticación de la aplicación]] | Acceso exitoso con un identificador que ya existía antes |
| Predicción | [[Log de autenticación de la aplicación]] | Solo la **recolección**: muchas sesiones nuevas desde un origen. El uso es invisible |
| JWT falsificado | [[Log de autenticación de la aplicación]] | Actividad de una cuenta **sin ningún evento de acceso previo** |
| Expiración | [[Log de autenticación de la aplicación]] | Actividad posterior al cierre de sesión o al cambio de contraseña |

Todo el dominio cuelga de un solo artefacto, y eso lo vuelve el punto único de fallo defensivo más claro del vault — vale correr `consultas.py spof` después de escribir las detecciones.

Dos observaciones que valen más que la tabla:

**La detección por origen es la única que funciona sin instrumentar nada nuevo.** Un identificador de sesión que aparece desde dos países en cinco minutos no tiene explicación legítima, y no distingue robo de fijación — cosa que al defensor no le importa. Es lo primero que conviene recomendar.

**Contra la predicción, la única ventana está en la recolección.** Un token predicho es indistinguible de uno legítimo: no hay nada que detectar en su uso. Si la detección no está puesta sobre la fase de pedir muchas sesiones, no está en ningún lado.

## Huecos conocidos

- [x] Los cinco fallos del ciclo de vida
- [x] JWT — [[Sesión - falsificación de JWT]] y su matriz
- [x] Atributos y vectores de robo — en [[Sesión - matriz de referencia]]
- [x] Cara azul — [[Misma sesión desde dos orígenes]] (`correlacion`) y [[Actividad de sesión posterior a su cierre]] (`invariante`)
- [x] Cuarto caso de detección que no es una regla sobre un evento — resuelto con `forma:` e implementado en [[Actividad de sesión posterior a su cierre]]
- [ ] **Todo el dominio sigue colgando de [[Log de autenticación de la aplicación]].** Es el punto único de fallo defensivo más claro del vault: si el cliente no lo recolecta, el dominio entero se apaga. Correr `consultas.py spof`
- [ ] OAuth y OIDC como mecanismo de sesión — tokens de refresco, alcances, `redirect_uri`. Dominio propio, sin modelar
- [ ] Sesión en aplicaciones de página única y en móvil: dónde vive el token cuando no hay cookie
