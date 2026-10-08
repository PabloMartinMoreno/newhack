---
tipo: teoria
habilita: ["[[Pass-the-hash]]", "[[Relay de NTLM]]", "[[Envenenamiento de resolución de nombres]]"]
relacionadas: ["[[Windows - proceso de autenticación]]", "[[Kerberos - el flujo de tickets]]", "[[SMB - dialectos y firma]]"]
aliases:
  - NTLM
  - net-NTLM
  - NetNTLMv2
  - NTLMv2
tags: []
---

# NTLM - desafío y respuesta

## Cómo funciona

NTLM autentica por **desafío-respuesta**, sin mandar nunca la contraseña:

1. El cliente anuncia que quiere autenticarse (Negotiate).
2. El servidor manda un **desafío**: un número aleatorio (nonce).
3. El cliente responde con `f(NT hash, desafío)` — una función del desafío y su **NT hash** (que es `MD4(contraseña)`, **sin sal**).
4. El servidor valida; si la cuenta es de dominio, reenvía la respuesta al DC por **Netlogon** para que la valide.

El **NT hash** es el secreto de largo plazo (no caduca hasta que cambie la contraseña). La respuesta que viaja por el cable —**net-NTLM**, en versiones **v1** o **v2**— es distinta en cada sesión porque depende del desafío.

## Dónde el diseño abre superficie

- **El NT hash es el secreto, y no tiene sal.** La respuesta se calcula del hash, no del texto plano: por eso tener el hash **es** tener la cuenta. No hace falta crackearlo.
- **net-NTLM ≠ NT hash.** Lo que captura un atacante en la red (Responder) es el **net-NTLMv2**, la respuesta ligada a *ese* desafío. No es el NT hash: no se puede "pasar", solo **crackear offline** o **relayar** a otro servicio en vivo.
- **La respuesta se puede reenviar.** Si el servicio destino no **exige firma**, la respuesta capturada se reenvía y se abre sesión como la víctima. Cruza con [[SMB - dialectos y firma]].
- **NTLMv1 es débil** y se puede reducir al NT hash.

Esta es la confusión que más cuesta y la que el diseño explica: por qué el **NT hash** se pasa (pass-the-hash) pero el **net-NTLMv2** no, y por qué este último se relaya o se crackea.

## Qué habilita

- NT hash sin sal, reusable → [[Pass-the-hash]].
- Respuesta reenviable sin firma → [[Relay de NTLM]].
- Forzar al cliente a autenticar contra vos para capturar el net-NTLM → [[Envenenamiento de resolución de nombres]].

NTLM es además la **alternativa** que elige Negotiate cuando Kerberos no aplica ([[Kerberos - el flujo de tickets]]); que aparezca NTLM donde el dominio usa Kerberos es la anomalía que detecta el lado azul.

## Cómo se ve en la práctica

Un logon NTLM queda en [[Windows 4624 - Successful logon]] (tipo 3, red) y en el `4776` de validación de credencial en el DC. La señal de mayor valor no es el evento suelto sino el **desajuste**: NTLM donde el protocolo esperado es Kerberos — [[Autenticación NTLM donde el dominio usa Kerberos]]. El net-NTLMv2 capturado se lleva a [[Cracking offline - matriz de referencia]] (`-m 5600`).

## Fuente

- MS-NLMP (NT LAN Manager Authentication Protocol).
