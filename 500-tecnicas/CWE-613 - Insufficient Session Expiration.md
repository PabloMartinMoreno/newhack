---
tipo: tecnica
taxonomia: cwe
identificador: CWE-613
wstg: WSTG-SESS-07
tacticas: []
aliases:
  - CWE-613
  - Insufficient session expiration
  - Expiración insuficiente
tags:
  - dominio/web
---

# CWE-613 - Insufficient Session Expiration

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Gestión de sesión]]; la variante, en [[Sesión - expiración insuficiente]].

## Qué es

La sesión sigue siendo válida cuando ya no debería. Cubre dos cosas distintas que conviene separar porque se arreglan distinto: que la sesión **dure demasiado**, y que **no se invalide** cuando ocurre algo que debería terminarla.

## El segundo caso es el grave

Que una sesión dure ocho horas en vez de dos es una discusión de política de riesgo. Que una sesión siga viva **después de un cambio de contraseña** es una vulnerabilidad concreta, y de las que más importan en un incidente real.

El escenario que lo explica: el usuario sospecha que le robaron la cuenta y cambia la contraseña. Si eso no invalida las sesiones activas, el atacante sigue adentro y el usuario cree que resolvió el problema. La acción defensiva más elemental que existe queda anulada en silencio.

Los cinco eventos que **tienen** que invalidar toda sesión activa:

- Cambio de contraseña, propio o por restablecimiento.
- Cierre de sesión explícito.
- Alta, baja o cambio del segundo factor.
- Revocación de permisos o cambio de rol.
- Baja o suspensión de la cuenta.

## El cierre de sesión que no cierra nada

Un caso propio y frecuentísimo: el botón de salir borra la cookie **del navegador** y no invalida el identificador **en el servidor**. Quien haya capturado ese token antes lo sigue usando después del cierre de sesión.

Se detecta en una prueba: guardar el token, cerrar sesión, reusarlo. Si responde, el cierre es cosmético.

## Con JWT el problema es estructural

Un token firmado y sin estado es válido hasta su vencimiento **por definición**: el servidor no consulta nada para aceptarlo, y por eso no hay dónde revocarlo. La invalidación exige agregar estado —una lista de revocados, o tokens de refresco de vida corta contra un registro consultable—, que es precisamente lo que se quería evitar al elegir JWT.

Es la contrapartida real de esa decisión de arquitectura, y conviene señalarla como tal en un informe: no es un error de implementación, es el precio del diseño. Ver [[Sesión - falsificación de JWT]].

## La mitigación real

Vencimiento absoluto **y** por inactividad, los dos. Invalidación del lado del servidor en los cinco eventos de arriba. Y una pantalla donde el usuario vea sus sesiones activas y pueda cerrarlas — que además es la mejor detección de compromiso que puede tener un usuario.

## Referencias canónicas

- [CWE-613](https://cwe.mitre.org/data/definitions/613.html)
- [CWE-539](https://cwe.mitre.org/data/definitions/539.html) — cookie persistente con datos sensibles
- WSTG-SESS-06, WSTG-SESS-07
