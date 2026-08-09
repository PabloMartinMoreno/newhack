---
tipo: deteccion
tecnicas: ["[[T1550.002 - Pass the Hash]]"]
telemetria: ["[[Windows 4624 - Successful logon]]", "[[Windows 5145 - Network share access]]"]
forma: agregado
ventana: "1h"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - detección de pass-the-hash
tags:
  - dominio/ad
---

# Autenticación NTLM donde el dominio usa Kerberos

## Qué detecta

Accesos por NTLM en un entorno que normalmente usa Kerberos, especialmente con una cuenta administrativa y hacia muchas máquinas. Es la firma de [[Pass-the-hash]], que no puede usar Kerberos y por eso deja NTLM donde no debería haberlo.

## Lógica

Ninguna condición sola alcanza — NTLM legítimo existe. La señal está en la **combinación**, y por eso es de forma `agregado`.

```
logons
| where EventID == 4624
| where LogonType == 3                          // red
| where AuthenticationPackageName == 'NTLM'
| summarize maquinas = dcount(Computer), total = count()
    by TargetUserName, IpAddress
| where maquinas > 5
```

Lo que convierte esto en detección es cruzarlo con el contexto:

- **Cuenta administrativa** usando NTLM de red. Los administradores deberían autenticar por Kerberos; NTLM de una cuenta privilegiada es de las señales más fuertes.
- **Muchas máquinas destino** desde un mismo origen en poco tiempo — la firma del movimiento lateral masivo por reutilización de administrador local.
- **Combinación de cuenta y equipo sin precedente**: un administrador local entrando a una máquina a la que nunca entró. Requiere histórico por cuenta, y es lo que mejor discrimina.

Complemento por efecto: [[Windows 5145 - Network share access]] a los recursos administrativos ocultos desde el mismo origen, que es lo que el atacante hace después de autenticar.

## Falsos positivos conocidos

- **Aplicaciones y sistemas viejos que solo hablan NTLM** — son el falso positivo dominante, y en muchos dominios son bastantes. Elevan la línea base de NTLM y hay que conocerlos.
- **Acceso por dirección IP en vez de por nombre** fuerza NTLM aunque Kerberos esté disponible, porque Kerberos necesita el nombre. Un administrador que se conecta por IP genera esto legítimamente.
- **Escáneres y herramientas de administración** que usan NTLM.
- **Dominios que todavía dependen mucho de NTLM** — ahí la condición de protocolo casi no discrimina, y hay que apoyarse en el volumen y en el histórico por cuenta.

La calidad de esta regla depende por completo de cuánto NTLM legítimo haya en el entorno. En un dominio que ya restringió NTLM es de alta fidelidad; en uno que no, es de baja. Ver [[La fidelidad se paga en volumen]].

## Evasiones conocidas

- **[[Pass-the-ticket]] en vez de pass-the-hash** — usa Kerberos, o sea el protocolo esperado, y evade esta regla por completo. Por diseño: es la razón por la que un atacante que puede robar tickets prefiere el ticket al hash. Su detección es otra — el robo del ticket de memoria.
- **Autenticar a una sola máquina** — no cruza el umbral de volumen. El movimiento puntual pasa.
- **Usar una cuenta que legítimamente usa NTLM** — cae en la línea base.

## Cómo se prueba

Disparador: [[Pass-the-hash]] en laboratorio, autenticando a varias máquinas con un hash de administrador local reutilizado.

Forma `agregado`: necesita volumen y, sobre todo, la **línea base de NTLM legítimo del entorno**, que es la que decide si la regla sirve. Sin ese dato, el umbral es inventado.
