---
tipo: telemetria
plataforma: [windows]
producto: Windows Security
identificador: "4768"
por-defecto: true
coste: alto
aliases:
  - AS-REQ
  - 4768
tags:
  - plataforma/windows
---

# Windows 4768 - Kerberos TGT requested

## Qué lo genera

Alguien pidió un **ticket inicial** de Kerberos, que es el primer paso de autenticarse en un dominio. Se registra en el controlador de dominio.

En un dominio, este evento y [[Windows 4769 - Kerberos service ticket requested]] son la autenticación de verdad. [[Windows 4624 - Successful logon]] cuenta lo que pasó en la máquina destino; estos dos cuentan lo que pasó en el controlador, que es donde se ve todo el dominio junto.

## Campos relevantes

| Campo | Para qué sirve |
|---|---|
| `TargetUserName` | Quién pide |
| `ServiceName` | Siempre el servicio de emisión de tickets |
| `IpAddress` | Desde dónde |
| `TicketEncryptionType` | **El campo clave** |
| `PreAuthType` | Si hubo preautenticación |
| `Status` | Éxito o motivo del fallo |

## Las dos cosas que se ven acá

**Preautenticación deshabilitada.** Kerberos normalmente exige probar que conocés la contraseña antes de emitir el ticket. Si una cuenta tiene eso desactivado, cualquiera puede pedir un ticket a su nombre y recibir material cifrado con su contraseña, para romperlo sin conexión. `PreAuthType` en cero es la señal, y la técnica se llama *AS-REP roasting*.

**Tipo de cifrado degradado.** El valor de `TicketEncryptionType` dice con qué algoritmo se cifró. El valor que corresponde a RC4 en un dominio que soporta AES es señal de degradación deliberada, porque **RC4 es mucho más rápido de romper sin conexión**. Es el mismo indicador que aparece en 4769 para el kerberoasting.

Y una tercera, de forma `agregado`: **muchos fallos contra muchas cuentas** desde un origen es rociado de contraseñas contra Kerberos, que no genera [[Windows 4625 - Failed logon]] en ninguna máquina destino porque nunca llega a haber sesión.

## Coste de recolección

Alto: en un dominio activo, cada usuario pide su ticket al empezar el día y lo renueva. En un controlador grande, el volumen es considerable.

## Cómo se activa

Auditoría de Kerberos habilitada en los controladores de dominio. Suele estar por defecto, pero conviene verificarlo — **y verificar que se recolecta de todos los controladores**, porque el atacante va a hablar con uno solo y no necesariamente con el que se está mirando.

## Limitaciones

- **Solo en controladores de dominio.** Si no se recolectan, esta fuente no existe.
- **Recolectar de uno solo deja huecos.** Es el error operativo más común con esta fuente.
- **Volumen alto** y muy repetitivo.
- **No dice qué se hizo con el ticket.** Para eso hay que seguir a 4769 y a los accesos.
- **Los tipos de cifrado dependen de la configuración del dominio.** Sin conocer la línea base, RC4 puede ser normal en un dominio viejo. Ver [[Sin línea base no hay anomalía]].

## Quién lo emite / quién lo consume

Rojo: [[AS-REP roasting]] · [[Golden ticket]] · [[ADCS - certificado con SAN arbitrario]]
Azul: pendiente — ver [[MOC - Telemetría de Windows]]
