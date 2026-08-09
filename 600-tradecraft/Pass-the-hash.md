---
tipo: tradecraft
clase: "[[T1550.002 - Pass the Hash]]"
eje: movimiento-lateral
implementacion: "Autenticarse por NTLM con el hash robado, sin la contraseña en claro"
opsec: ruidoso
telemetria: ["[[Windows 4624 - Successful logon]]", "[[Windows 5145 - Network share access]]"]
requisitos: [hash-NTLM, NTLM-habilitado]
coste: bajo
alternativas: ["[[Pass-the-ticket]]"]
probado: 2026-08-08
contexto: [lab-ad]
aliases:
  - PtH
tags:
  - dominio/ad
---

# Pass-the-hash

## Cuándo lo elijo

Cuando hay un hash NTLM —de [[LSASS - volcado vía comsvcs.dll MiniDump]] o de otra fuente— y hace falta moverse a otra máquina. Es la vía directa cuando NTLM está habilitado, que sigue siendo lo habitual.

El caso que lo vuelve devastador: **una cuenta de administrador local con la misma contraseña en muchas máquinas**. Un hash sirve entonces en cientos de equipos, y el movimiento lateral es casi gratis.

## Por qué funciona

Porque NTLM nunca envía la contraseña: envía una respuesta calculada a partir del hash. **El hash es el secreto**, y quien lo tiene puede autenticarse sin conocer ni romper la contraseña. Ver [[T1550.002 - Pass the Hash]].

No funciona contra Kerberos, que es lo que el dominio prefiere. Por eso su uso genera NTLM donde el entorno normalmente usaría Kerberos — y ese desajuste de protocolo es una señal en sí mismo.

## Cómo falla

- **Contraseña de administrador local única por máquina y rotada** — corta el movimiento masivo de raíz. El hash sirve en un solo equipo. Es la mitigación que más cambia el resultado.
- **NTLM deshabilitado o restringido** — cierra la técnica; hay que pasar a [[Pass-the-ticket]].
- **Separación de niveles administrativos** — si las credenciales valiosas no se cargan nunca en máquinas de usuario, el hash que se roba no vale para nada importante.
- **Cuentas privilegiadas protegidas** y restringidas para acceso de red.
- **La cuenta no es administrador en el destino** — el hash autentica pero no habilita nada.

## Coste

Bajo. Con el hash, autenticarse es inmediato. Lo caro fue conseguir el hash, que es otra técnica.

## Huella esperada

- [[Windows 4624 - Successful logon]] con **tipo 3 (red)** y paquete de autenticación **NTLM**. NTLM donde el dominio usa Kerberos es la señal más clara, y solo se ve si se compara contra la línea base del entorno.
- [[Windows 5145 - Network share access]] a los recursos administrativos ocultos desde un origen inusual, que es el efecto de usar el acceso para ejecutar algo remoto.
- **El mismo origen autenticando contra muchas máquinas** en poco tiempo es la firma del movimiento masivo, de forma `agregado`.
- Combinación de cuenta y equipo que **nunca ocurrió antes**: un administrador local entrando a una máquina a la que nunca entró. Requiere histórico por cuenta.

La detección puntual es débil porque un acceso legítimo por NTLM se ve igual. La fuerza está en el patrón: origen, protocolo contra la línea base, y cuentas-equipos que no tienen precedente.
