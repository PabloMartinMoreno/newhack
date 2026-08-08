---
tipo: moc
dominio: web
aliases:
  - MOC autenticación
  - Autenticación
  - Authentication
tags:
  - dominio/web
---

# MOC - Autenticación

> [!abstract] Nota de referencia paraguas
> Las definiciones viven en [[CWE-204 - Observable Response Discrepancy]], [[CWE-307 - Improper Restriction of Excessive Authentication Attempts]], [[CWE-287 - Improper Authentication]] y [[CWE-640 - Weak Password Recovery Mechanism for Forgotten Password]]. Acá vive **la decisión**.
>
> Lo que pasa **después** de entrar es [[MOC - Gestión de sesión]]. Este dominio termina en el momento en que se emite la sesión.

Este dominio se organiza por **fase del ciclo de vida**, no por técnica. La razón es que las fases se encadenan: lo que se obtiene en una es el insumo de la siguiente, y saltearse la primera multiplica el costo de todas las demás.

| Eje | Valores |
|---|---|
| Fase | enumeración · credenciales · segundo factor · recuperación |
| Vector | spraying · stuffing · fuerza bruta · credenciales por defecto |
| Oráculo | mensaje · tiempo · comportamiento |
| Obstáculo | límite por cuenta · límite por origen · CAPTCHA · bloqueo · MFA |
| Impacto | una cuenta · masivo · administrativa |

## Árbol de decisión — la secuencia

```
1. ¿Puedo saber qué cuentas existen?
   └─ Sí → [[Autenticación - enumeración de usuarios]]   ← multiplica todo lo demás

2. ¿Tengo corpus de credenciales filtradas del dominio?
   ├─ Sí → [[Autenticación - credential stuffing]]        ← mayor tasa, no genera fallos
   └─ No → [[Autenticación - password spraying]]          ← una contraseña, muchas cuentas

3. ¿La credencial válida alcanza?
   ├─ Sí → adentro
   └─ No, hay MFA
      ├─ ¿Existe un camino de acceso sin MFA?  → probar ese primero
      ├─ [[Autenticación - bypass de segundo factor]]
      └─ [[Autenticación - abuso de recuperación de contraseña]]  ← rodeo por diseño
```

Tres cosas que este orden codifica y que se hacen mal seguido:

**La enumeración va primero aunque su impacto sea bajo.** No vale por sí misma: vale porque convierte diez mil intentos a ciegas en doscientos dirigidos. Compra sigilo, no información.

**Spraying y stuffing no son lo mismo y la elección no es de gusto.** Depende de un solo dato: si hay corpus. Con corpus, el stuffing gana por lejos —acierta a la primera y no genera fallos—; sin corpus, no existe.

**Contra MFA, buscar el camino que no lo tiene rinde más que atacarlo.** Una API, un cliente móvil o un protocolo heredado sin segundo factor invalidan todo el mecanismo, y encontrarlos es reconocimiento, no explotación.

## Árbol de decisión — el control de ritmo

```
¿Qué te está frenando?
├─ Bloqueo por cuenta       → repartir sobre muchas cuentas → spraying
├─ Límite por IP            → distribuir el origen
├─ CAPTCHA en el formulario → buscar la API, que suele no tenerlo
├─ Retraso progresivo       → bajar el ritmo, no el volumen
└─ MFA                      → cambiar de rama: no es problema de ritmo
```

La primera rama es la clave del dominio entero: **el control habitual está en el eje equivocado**. Contar fallos por cuenta detiene la fuerza bruta clásica y no detiene nada más. Por eso el hallazgo casi nunca es "no hay límite" sino "el límite no cubre este eje", y conviene escribirlo así o se cierra agregando un contador que ya existía.

## Cheatsheets

| Matriz | Cubre |
|---|---|
| [[Autenticación - matriz de referencia]] | Oráculos de enumeración, contraseñas que pagan y cálculo de la ventana, análisis del token de recuperación |
| [[MFA bypass - matriz de referencia]] | Camino sin MFA, salto de paso, manipulación de la verificación, fuerza bruta del código, respaldo, rodeos |

## Orden de aprendizaje

1. [[CWE-204 - Observable Response Discrepancy]] → [[Autenticación - enumeración de usuarios]] — el multiplicador
2. [[CWE-307 - Improper Restriction of Excessive Authentication Attempts]] — por qué el límite suele estar mal puesto
3. [[Autenticación - password spraying]] — el caso base contra el bloqueo por cuenta
4. [[Autenticación - credential stuffing]] — el que no genera fallos, y por qué eso lo cambia todo
5. [[CWE-287 - Improper Authentication]] → [[Autenticación - bypass de segundo factor]]
6. [[CWE-640 - Weak Password Recovery Mechanism for Forgotten Password]] → [[Autenticación - abuso de recuperación de contraseña]] — el rodeo que existe por diseño
7. [[MOC - Gestión de sesión]] — qué pasa después de entrar

El punto 4 es el que reordena la intuición: casi toda la defensa del dominio está construida alrededor de "muchos fallos seguidos", y el ataque de mayor tasa de acierto no produce ninguno.

## Relación con otros dominios

- [[MOC - Gestión de sesión]] — la continuación. Este dominio termina donde se emite la sesión; aquel empieza ahí.
- [[MOC - Broken access control]] — el token de recuperación no atado a la cuenta es [[Control de acceso - IDOR]] dentro de este flujo, y el salto del segundo factor es [[Control de acceso - salto de contexto]] aplicado al acceso. Los fallos estructurales se repiten entre dominios.
- [[MOC - SQL injection]] — el formulario de acceso es un punto de inyección como cualquier otro. Vale probar ambas cosas sobre el mismo campo.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Enumeración | [[Log de autenticación de la aplicación]] | Ráfaga de fallos contra cuentas **mayormente inexistentes** |
| Spraying | [[Log de autenticación de la aplicación]] | Un fallo por cuenta sobre cientos, mismo origen, ventana estrecha |
| Stuffing | [[Log de autenticación de la aplicación]] | **Éxitos**, no fallos: una IP autenticando contra cuentas sin relación |
| Bypass de MFA | [[Log de autenticación de la aplicación]] | Acceso completado sin evento de verificación del segundo factor |
| Recuperación | el usuario | Un correo de restablecimiento que nadie pidió |

Dos cosas que este dominio deja claras y que valen para todo el vault:

**La detección vive en el agregado, no en el evento.** Un fallo de acceso no es nada; la proporción de fallos contra cuentas inexistentes, o la cantidad de cuentas distintas tocadas por un origen, lo son todo. Ninguna regla que mire una petición por vez sirve acá.

**Contar fallos no alcanza.** [[Autenticación - credential stuffing]] acierta a la primera y no genera ni uno. Para esa variante hay que mirar los éxitos anómalos, que es una detección de forma completamente distinta.

Y la fila de recuperación es la única del vault donde el mejor detector no es un artefacto de telemetría: es **una persona que avisa que recibió un correo raro**.

## Huecos conocidos

- [x] Las cuatro fases del ciclo de vida
- [x] Spraying y stuffing como valores distintos del eje vector
- [x] MFA — [[Autenticación - bypass de segundo factor]] y su matriz
- [ ] **Cara azul sin escribir.** [[Log de autenticación de la aplicación]] existe y ninguna detección lo consume
- [ ] **Detección sobre agregados.** Es el tercer caso donde la detección natural no es una regla sobre un evento sino una función sobre una ventana. Junto con [[Control de acceso - salto de contexto]], ya son suficientes para revisar si el esquema de `deteccion` necesita el campo
- [ ] SSO, OAuth y SAML como superficie de autenticación — dominio propio, sin modelar
- [ ] WebAuthn y llaves de acceso: qué cambia cuando el factor no es un secreto compartido
