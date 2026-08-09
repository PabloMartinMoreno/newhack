---
tipo: telemetria
plataforma: [windows]
producto: Windows Security
identificador: "4769"
por-defecto: true
coste: alto
aliases:
  - TGS-REQ
  - 4769
tags:
  - plataforma/windows
---

# Windows 4769 - Kerberos service ticket requested

## Qué lo genera

Alguien pidió un ticket **para acceder a un servicio concreto**, ya teniendo su ticket inicial. Se registra en el controlador de dominio.

Es la fuente del kerberoasting, que es de las técnicas más usadas contra Active Directory.

## Campos relevantes

| Campo | Para qué sirve |
|---|---|
| `TargetUserName` | Quién pide |
| `ServiceName` | **Para qué servicio** — el campo central |
| `TicketEncryptionType` | Con qué algoritmo se cifró |
| `IpAddress` | Desde dónde |
| `TicketOptions` | Opciones del ticket |
| `Status` | Resultado |

## Por qué esta fuente importa tanto

El ticket de servicio viene cifrado con la contraseña de la cuenta que corre ese servicio. Cualquier usuario del dominio puede pedirlo — es funcionamiento normal de Kerberos. Y una vez que lo tiene, puede **intentar romperlo sin conexión**, sin volver a tocar la red.

Ahí está el problema y la razón de que esta fuente sea crítica: **el ataque ocurre fuera del dominio**. Lo único observable es la petición, que parece legítima porque lo es. Después de eso, silencio.

Es el mismo patrón que [[Deserialización - firma débil]] del lado web: el ataque es fuera de línea, y la única ventana de detección está en la fase de pedir.

Las tres señales:

- **Tipo de cifrado RC4** en un dominio que soporta AES: degradación deliberada, porque se rompe mucho más rápido.
- **Volumen anormal**: una cuenta pidiendo tickets para muchos servicios distintos en poco tiempo. Un usuario normal pide para los pocos servicios que usa.
- **Servicios que corren bajo cuentas de usuario** en vez de cuentas de máquina. Son los únicos que valen la pena romper, porque las cuentas de máquina tienen contraseñas largas y aleatorias que no se rompen.

## Coste de recolección

Alto, más que 4768: cada acceso a cada servicio genera uno. En un dominio activo son muchísimos.

## Cómo se activa

Igual que 4768: auditoría de Kerberos en **todos** los controladores de dominio.

## Limitaciones

- **Volumen muy alto**, y casi todo legítimo.
- **La petición es indistinguible de una legítima**, salvo por el agregado y por el tipo de cifrado.
- **No se ve si el ticket se rompió.** El éxito del ataque ocurre fuera del dominio y no deja rastro; lo siguiente que se ve es un acceso exitoso con esa cuenta, que ya es la fase posterior.
- **Sin línea base, el umbral de volumen es inventado.** Cuántos servicios distintos pide un usuario normal varía muchísimo entre organizaciones.

## Quién lo emite / quién lo consume

Rojo: [[Kerberoasting]] · [[Golden ticket]]
Azul: pendiente — ver [[MOC - Telemetría de Windows]]
