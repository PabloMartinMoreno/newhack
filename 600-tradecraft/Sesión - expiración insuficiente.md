---
tipo: tradecraft
clase: "[[CWE-613 - Insufficient Session Expiration]]"
eje: fallo
implementacion: "Reusar un token que debería haber sido invalidado"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [token-capturado-o-propio]
coste: bajo
alternativas: ["[[Sesión - robo de token]]"]
probado: 2026-08-08
contexto: [web-generica]
aliases:
  - logout que no cierra
  - reuso de token revocado
tags:
  - dominio/web
---

# Sesión - expiración insuficiente

## Cuándo lo elijo

Siempre, como verificación, porque cuesta cinco minutos y se prueba entero con la cuenta propia. No hace falta víctima ni vulnerabilidad previa: se guarda el token, se dispara el evento que debería invalidarlo, y se reusa.

Su valor no está en obtener acceso —eso ya se tiene— sino en **determinar si el acceso obtenido por otra vía sobrevive** a la reacción defensiva. Esa es la pregunta que responde, y es la que decide si un compromiso es un incidente cerrado o uno abierto.

El caso que importa: la víctima sospecha que le robaron la cuenta y cambia la contraseña. Si eso no invalida las sesiones activas, el atacante sigue adentro y el usuario cree que resolvió el problema. La acción defensiva más elemental que existe queda anulada en silencio, y por eso este hallazgo pesa más de lo que su descripción sugiere.

## Por qué funciona

Porque invalidar del lado del servidor exige llevar registro de las sesiones activas y recorrerlo cuando pasa algo. Borrar la cookie del navegador, en cambio, es una línea. La segunda se parece a la primera desde la interfaz —el usuario ve que salió— y no hace nada por la seguridad.

Con JWT sin estado el problema es **estructural, no un descuido**: un token firmado es válido hasta su vencimiento por definición, porque el servidor no consulta nada para aceptarlo. Revocarlo exige agregar el estado que se quiso evitar al elegir el formato. Conviene reportarlo así: es el precio de una decisión de arquitectura, no un error de implementación.

## Cómo falla

- **Invalidación del lado del servidor en los cinco eventos** —cambio de contraseña, cierre de sesión, cambio de MFA, cambio de rol, baja de cuenta—. La mitigación completa.
- **Vencimiento corto** — reduce la ventana aunque la invalidación falte.
- **Rotación del token en cada operación sensible** — el token viejo deja de servir sin necesidad de una lista de revocados.
- **Lista de revocados con JWT** — resuelve el problema estructural a costa de volver el sistema con estado.
- **No se puede capturar un token ajeno** — sin eso, el hallazgo es real y su explotación depende de otra vulnerabilidad.

## Coste

Bajísimo. Es la técnica más barata del vault: guardar un valor, hacer una acción, reusar el valor. Toda la dificultad está en acordarse de probarlo, porque no se parece a un ataque.

## Huella esperada

`opsec: limpio` con la salvedad de siempre: no hay nada anómalo que detectar en el evento. El token es válido y el servidor lo acepta porque efectivamente lo sigue considerando válido.

- [[Log de autenticación de la aplicación]] con **actividad de sesión posterior a un evento de cierre de sesión o de cambio de contraseña** para esa misma cuenta. Es la firma exacta, y depende de que ambos extremos se registren con el identificador de sesión — que es justo lo que suele faltar.
- La detección natural no es una regla sobre un evento sino una **verificación de invariante**: ninguna sesión debería estar activa después del evento que la termina. Es el mismo tipo de detección que pide [[Control de acceso - salto de contexto]], y el cuarto caso del vault que no encaja en el esquema de una regla sobre un artefacto.
- Sin correlación entre el cierre de sesión y el uso posterior, esta variante es invisible.

Las pruebas concretas están en [[Sesión - matriz de referencia]] § Expiración.
