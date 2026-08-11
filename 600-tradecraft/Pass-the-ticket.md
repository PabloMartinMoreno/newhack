---
tipo: tradecraft
clase: "[[T1550.003 - Pass the Ticket]]"
eje: movimiento-lateral
implementacion: "Robar un ticket Kerberos de memoria y usarlo desde otra máquina"
opsec: requiere-bypass
telemetria: ["[[Windows 4624 - Successful logon]]", "[[Sysmon EID 10 - ProcessAccess]]"]
requisitos: [ticket-en-memoria, admin-local-en-el-host-origen]
coste: medio
alternativas: ["[[Pass-the-hash]]", "[[Golden ticket]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - PtT
tags:
  - dominio/ad
---

# Pass-the-ticket

## Cuándo lo elijo

Cuando el movimiento tiene que ser por Kerberos —porque NTLM está restringido, o porque no quiero generar el desajuste de protocolo de [[Pass-the-hash]]— y hay un ticket aprovechable en la memoria de una máquina donde ya soy administrador local.

Un ticket inicial vale más que uno de servicio: el primero sirve para pedir acceso a cualquier cosa, el segundo a un solo servicio. Se busca el mejor disponible.

## Por qué funciona

Porque un ticket de Kerberos es portátil por diseño: es un objeto autocontenido que prueba una identidad y no está atado al equipo que lo pidió. Se copia de memoria, se carga en otra máquina, y sirve hasta que vence. Ver [[T1550.003 - Pass the Ticket]].

La gran ventaja sobre pasar el hash: **es Kerberos, o sea el protocolo normal del dominio**. No genera ninguna anomalía de protocolo. Se ve como autenticación estándar.

## Cómo falla

- **El ticket caduca.** Es la limitación estructural: un ticket inicial dura horas. Pone un reloj sobre el acceso que el hash no tiene, y obliga a robar de una sesión activa.
- **No hay ticket valioso en memoria** — si en el host comprometido no inició sesión nadie interesante, no hay nada que robar. La separación de niveles administrativos es lo que garantiza eso.
- **Protección del proceso de credenciales** dificulta extraer el ticket, y ese paso previo —acceder a la memoria— es la parte detectable.
- **Cuentas protegidas** con tickets de vida más corta y sin delegación reducen la ventana.

## Coste

Medio. Robar el ticket requiere administrador local y acceder a la memoria del proceso de credenciales — que es la parte cara y ruidosa. Usarlo después es limpio.

## Huella esperada

El uso es sigiloso; el robo no. Ahí está la asimetría que define la detección.

- **Robar el ticket** deja [[Sysmon EID 10 - ProcessAccess]]: un acceso a la memoria del proceso de credenciales, igual que en [[LSASS - volcado vía comsvcs.dll MiniDump]]. Es la ventana de detección real, y es la misma que ya tiene detección propia en el vault.
- **Usar el ticket** deja [[Windows 4624 - Successful logon]] por Kerberos, indistinguible de un acceso legítimo salvo por el contexto — origen inusual para esa cuenta, horario, un equipo al que nunca entró.
- Anomalías finas del ticket —vigencia rara, cifrado que no corresponde— existen pero requieren inspección que casi nadie hace.

La lección del dominio: **cuando el uso es invisible, hay que detectar el paso anterior**. Acá el paso anterior es tocar la memoria de credenciales, y eso sí se ve.
