---
tipo: deteccion
tecnicas: ["[[T1558 - Steal or Forge Kerberos Tickets]]"]
telemetria: ["[[Windows 4624 - Successful logon]]"]
forma: evento
ventana: 
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - detección de delegación sin restricciones
tags:
  - dominio/ad
---

# Cuenta de alto valor autenticándose a host con delegación

## Qué detecta

Una cuenta de alto valor —un controlador de dominio, una cuenta administrativa, una cuenta en *Protected Users*— autenticándose a un host que tiene **delegación sin restricciones** y no es un controlador de dominio. Es la firma de [[Delegación sin restricciones]] en el momento clave: la coacción que hace que un DC se autentique al host del atacante para que su TGT quede capturado en memoria.

Cierra el hueco de la delegación sin restricciones, que no se detecta por un campo del evento sino por una **relación** —quién se autentica a qué—, y por eso necesita dos listas de activos: los hosts con delegación y las cuentas de alto valor.

## Lógica

```kql
let hostsDelegacion = dynamic(["SRV-DELEG$", "..."]);   // inventario: TRUSTED_FOR_DELEGATION, no-DC
let cuentasAltoValor = dynamic(["DC01$", "DC02$", "Administrator"]);
DeviceLogonEvents
| where Timestamp > ago(1h)
| where LogonType in ("Network", "Kerberos")
| where AccountName in~ (cuentasAltoValor)              // un DC o admin autenticándose
| where DeviceName in~ (hostsDelegacion)                // a un host con delegación sin restricciones
| project Timestamp, AccountName, DeviceName, RemoteIP
```

La regla es una intersección de dos listas: **una cuenta que no debería autenticarse a ese host, en un host que acumula TGT**. Un DC no tiene ninguna razón para autenticarse a un servidor de aplicación cualquiera; que lo haga contra uno con delegación sin restricciones es la coacción en curso.

La lista de hosts con delegación se saca del directorio —el mismo `TRUSTED_FOR_DELEGATION` que el atacante enumera en [[AD enumeración - matriz de referencia]]— y se mantiene: es inventario, no calibración de umbral.

## Por qué la fidelidad es media

Depende por completo de las dos listas. Con un inventario correcto de hosts con delegación y de cuentas de alto valor, la señal es de alta fidelidad —un DC autenticándose ahí no ocurre legítimamente—. Con listas incompletas o desactualizadas, falla en las dos direcciones: pierde ataques (host de delegación no listado) o alerta de más (cuenta de alto valor no reconocida). La regla es tan buena como el inventario.

## Falsos positivos conocidos

- **Delegación sin restricciones legítima** en un servidor que de verdad la necesita y al que un DC se autentica por diseño —raro, pero existe—. Se excluye ese par host+cuenta.
- **Cuentas de servicio de alto privilegio** que tocan esos hosts en flujos conocidos.

## Evasiones conocidas

- **No coaccionar, esperar** a que el DC se autentique solo: igual deja el mismo `4624`, así que la regla lo ve; lo que cambia es que es menos frecuente.
- **Coaccionar a una cuenta de alto valor no listada**: por eso la lista de cuentas sensibles hay que mantenerla amplia.
- **Un host de delegación recién configurado y no inventariado**: cae fuera de la lista. La mitigación real de fondo no es esta regla sino **eliminar la delegación sin restricciones**, que es una configuración obsoleta.

## Cómo se prueba

Disparador: [[Delegación sin restricciones]] en laboratorio, coaccionando un DC a autenticarse a un host con delegación.

Forma `evento`, un disparo la valida —el `4624` se genera siempre—, pero la regla no sirve sin las dos listas de activos curadas primero. El trabajo previo es el inventario, no la lógica.
