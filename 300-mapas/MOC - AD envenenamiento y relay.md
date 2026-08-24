---
tipo: moc
dominio: ad
aliases:
  - MOC AD envenenamiento y relay
tags:
  - dominio/ad
---

# MOC - AD envenenamiento y relay

> [!abstract] Fase de la kill chain de AD
> El primer material sin tener **ninguna** credencial. Hub del dominio: [[MOC - Active Directory]]. Cheatsheet: [[AD envenenamiento y relay - matriz de referencia]]. Clase: [[T1557.001 - LLMNR NBT-NS Poisoning and SMB Relay]].

Sin credencial y en la red, el AD todavía habla. Dos vías, y la segunda no depende de la primera.

## Árbol de decisión

```
Estoy en la red, sin credencial
├─ ¿Hay resolución de nombres por difusión (LLMNR/NBT-NS/mDNS)?
│  └─ Respondo a la escucha  → [[Envenenamiento de resolución de nombres]]   ← el primer hash del pentest
│     ├─ el hash rompe offline  → credencial → [[MOC - AD enumeración]]
│     └─ no rompe, o querés no depender de romperlo ↓
└─ ¿Hay objetivos SMB/LDAP sin firma obligatoria?
   └─ Reenvío la autenticación capturada  → [[Relay de NTLM]]   ← no necesita romper nada
      ├─ a SMB       → ejecución en el destino
      ├─ a LDAP      → escribir RBCD → [[MOC - AD delegaciones]]
      └─ a AD CS     → certificado → [[MOC - ADCS]] (ESC8)
```

La decisión de fondo: **capturar y romper** contra **capturar y reenviar**. Romper depende de que la contraseña sea débil; reenviar depende de que falte la firma. Cuando el objetivo no firma, el relay es superior porque no toca la contraseña.

## Orden de aprendizaje

1. [[Envenenamiento de resolución de nombres]] — de dónde sale el primer NetNTLMv2
2. [[Relay de NTLM]] — por qué reenviar gana cuando romper no alcanza

## Cara roja

- [[Envenenamiento de resolución de nombres]] · [[Relay de NTLM]]
- Comandos: [[AD envenenamiento y relay - matriz de referencia]] — Responder, romper NetNTLMv2, comprobar firma, `ntlmrelayx` a SMB/LDAP/ADCS, coacción.

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[Envenenamiento de resolución de nombres]] | [[Sysmon EID 3 - NetworkConnect\|Sysmon 3]] | [[Conexión a host de resolución de nombres no autorizado]] |
| [[Relay de NTLM]] | [[Windows 4624 - Successful logon\|4624]] | [[Autenticación NTLM donde el dominio usa Kerberos]] |

## Huecos conocidos

- [x] Captura y relay, con detección de la captura y convergencia del relay en NTLM anómalo
- [ ] Coacción (`PetitPotam`, `PrinterBug`) como disparador del relay — está en la matriz, sin nota de criterio propia
- [ ] Relay a HTTP/AD CS (ESC8) cruza con [[MOC - ADCS]]; el detalle vive allá
