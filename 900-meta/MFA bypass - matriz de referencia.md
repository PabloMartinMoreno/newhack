---
tipo: meta
aliases:
  - Payloads de bypass de MFA
  - 2FA bypass - matriz
tags:
  - meta/referencia
  - dominio/web
---

# MFA bypass - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué probar contra un segundo factor, en orden de coste creciente. El criterio está en [[Autenticación - bypass de segundo factor]].

## 0. Buscar el camino sin MFA — antes que nada

Rinde más seguido que atacar el mecanismo, y cuesta reconocimiento, no explotación.

```
/api/v1/login          la API móvil, que a veces autentica distinto
/oauth/token           flujo de token, frecuentemente sin segundo factor
/legacy/  /old/  /v1/  caminos heredados que quedaron en pie
IMAP, SMTP, POP3       protocolos que no soportan MFA por diseño
tokens de aplicación   "contraseñas de aplicación" que lo evitan por definición
```

La pregunta a responder es una sola: **¿existe alguna forma de autenticarse que no pase por el formulario web?** Si existe, probablemente no exige el segundo factor.

## 1. Salto de paso

Lo más barato y lo que más veces funciona.

```
1. POST /login  usuario + contraseña  →  200, y ¿ya viene cookie de sesión?
2. Ignorar /login/2fa
3. GET /dashboard directamente
```

Si el paso 3 responde, la sesión ya era válida y el segundo factor era decorativo.

```http
POST /login/2fa/skip
GET  /login/2fa?skip=true
```

Variantes que a veces existen para pruebas y quedaron.

```
Reenviar la petición del paso 1 y observar qué cambia en la respuesta
si se agrega   "mfa_required": false   o   "step": 2
```

Manipulación de la respuesta del lado del cliente: solo funciona si la decisión se toma en el navegador, cosa que pasa más de lo que debería en aplicaciones de página única.

## 2. Manipular la verificación

```http
POST /login/2fa
{"code": "123456", "user": "victima"}
```

Cambiar la cuenta en la petición de verificación: se verifica el código propio y se emite sesión para otro. Es [[Control de acceso - IDOR]] dentro del flujo de acceso.

```
{"code": ""}
{"code": null}
{"code": []}
{"code": ["123456"]}
```

Valores vacíos y de tipo inesperado. Algunas comparaciones tratan el vacío como coincidencia.

```
{"code": "123456", "code": "000000"}
```

Parámetro duplicado.

## 3. Fuerza bruta del código

```
000000 – 999999    seis dígitos, un millón
0000 – 9999        cuatro dígitos, diez mil — minutos sin control de ritmo
```

Antes de lanzarlo, medir tres cosas:

```
¿Cuántos intentos antes de invalidar el código?
¿Pedir un código nuevo REINICIA el contador de intentos?
¿Cuánto vive el código?
```

La segunda es la que suele romper el control: si pedir un código nuevo reinicia el contador, se alternan pedido e intentos y el límite deja de existir.

## 4. Reutilización y respaldo

```
usar el mismo código dos veces        → ¿se invalida al usarse?
usar un código de hace media hora     → ¿expira de verdad?
códigos de respaldo                    → ¿cuántos? ¿tienen control de ritmo propio?
```

Los códigos de respaldo suelen ser el punto débil: más largos pero sin límite de intentos, porque nadie pensó en ellos como superficie.

```
Cookie de "recordar este dispositivo"
├─ ¿es predecible o adivinable?
├─ ¿está atada a la cuenta?
└─ ¿sirve en otra cuenta?
```

## 5. Bajar de método

Si hay varios factores configurables, se elige el más débil.

```
TOTP  →  SMS  →  correo  →  preguntas
```

Un flujo que ofrezca "probá otro método" y permita elegir sin verificar el actual es un bypass completo: se salta al eslabón más flojo.

## 6. Rodearlo por otro flujo

```
Recuperación de contraseña  →  ¿el reset desactiva o saltea el MFA?
Cambio de correo            →  ¿reenvía el segundo factor al correo nuevo?
Desactivación del MFA       →  ¿pide el factor actual para desactivarlo?
Invitación / delegación     →  ¿la cuenta invitada hereda acceso sin MFA?
```

La primera es la más productiva y tiene nota propia: [[Autenticación - abuso de recuperación de contraseña]]. La tercera es un clásico: desactivar el segundo factor sin exigirlo convierte cualquier robo de sesión en toma permanente.

## 7. Lo que no va acá

> [!danger] La fatiga de MFA es ingeniería social sobre una persona
> Repetir intentos hasta que el usuario acepte una notificación por cansancio **no es una prueba técnica**: es hostigamiento a alguien real, y su resultado depende del estado de ánimo de esa persona, no de la aplicación.
>
> Fuera de alcance salvo autorización explícita del engagement con la persona objetivo al tanto. Lo que se documenta en una prueba técnica es si el mecanismo **permite** el bombardeo —que es un hallazgo válido y se demuestra con dos o tres intentos—, no cuántos aguanta el usuario.
