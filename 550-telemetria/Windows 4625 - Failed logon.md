---
tipo: telemetria
plataforma: [windows]
producto: Windows Security
identificador: "4625"
por-defecto: true
coste: bajo
aliases:
  - inicio de sesión fallido
  - 4625
tags:
  - plataforma/windows
---

# Windows 4625 - Failed logon

## Qué lo genera

Un intento de inicio de sesión que falló. Es el par de [[Windows 4624 - Successful logon]] y, para detectar ataques de credenciales, el más útil de los dos.

## El campo que casi nadie usa

`SubStatus` dice **por qué** falló, y esa distinción es exactamente la que separa dos ataques distintos:

| Código | Qué significa |
|---|---|
| `0xC0000064` | **El usuario no existe** |
| `0xC000006A` | El usuario existe, la contraseña está mal |
| `0xC0000234` | La cuenta está bloqueada |
| `0xC0000072` | La cuenta está deshabilitada |
| `0xC0000071` | La contraseña expiró |
| `0xC0000070` | Restricción de estación de trabajo |
| `0xC00000193` | La cuenta expiró |

Los dos primeros son todo el asunto: **muchos `0xC0000064` es enumeración de cuentas** —alguien probando nombres que en su mayoría no existen— y **muchos `0xC000006A` repartidos entre cuentas reales es rociado de contraseñas**.

Es la misma distinción que hace [[Fallos de acceso contra cuentas inexistentes]] del lado web con el motivo del fallo. Acá el campo **ya existe y viene por defecto**, cosa que del lado web casi nunca pasa.

## Otros campos relevantes

| Campo | Para qué sirve |
|---|---|
| `TargetUserName` | Contra qué cuenta |
| `IpAddress` / `WorkstationName` | Desde dónde |
| `LogonType` | Mismos tipos que en 4624 |
| `AuthenticationPackageName` | Kerberos o NTLM |

## Coste de recolección

Bajo. Los fallos son mucho menos frecuentes que los éxitos en operación normal, así que el volumen es manejable y se puede retener mucho tiempo barato.

Esa asimetría es interesante: **la fuente que más sirve para detectar ataques de credenciales es la más barata de guardar**.

## Cómo se activa

Por defecto en la mayoría de las configuraciones, junto con la auditoría de accesos exitosos.

## Limitaciones

- **No ve lo que acierta a la primera.** Un ataque con credenciales válidas robadas no genera ningún fallo — mismo punto ciego que [[Autenticación - credential stuffing]] del lado web. Para eso hay que mirar los **éxitos** anómalos de 4624.
- **Un evento aislado no dice nada.** Todo el valor está en la agregación: tasa, cantidad de cuentas distintas, proporción por código de estado.
- **Contraseñas viejas en clientes y servicios** generan fallos crónicos que elevan la línea base y hay que conocer.
- **No cubre autenticación Kerberos pura**, que deja su rastro en [[Windows 4768 - Kerberos TGT requested]] con sus propios códigos.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
