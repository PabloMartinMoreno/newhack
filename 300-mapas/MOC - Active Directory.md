---
tipo: moc
dominio: ad
aliases:
  - MOC AD
tags:
  - dominio/ad
---

# MOC - Active Directory

> [!abstract] Nota de referencia paraguas
> Superficie: [[Active Directory]]. Las fuentes de datos, en [[MOC - Telemetría de Windows]]. Los conceptos de detección, en [[MOC - Fundamentos de detección]]. Acá vive **la decisión**.

Active Directory no se ataca por un servicio: se ataca por las **relaciones**. Quién puede hacer qué sobre quién, y qué credenciales quedan en memoria en cada máquina como consecuencia. Por eso el dominio se organiza por **lo que tenés** —qué credencial, qué acceso— y no por técnica: cada nivel de acceso abre unas ramas y cierra otras.

| Eje | Valores |
|---|---|
| Lo que tengo | nada (solo red) · una credencial · admin local · admin de dominio |
| Fase | enumeración · acceso a credenciales · movimiento lateral · persistencia |
| Protocolo | NTLM · Kerberos · replicación · certificados |
| Dónde ocurre el ataque | en un endpoint · fuera de línea · en el controlador |

## Árbol de decisión — qué tengo y qué quiero

```
¿Qué credencial tengo?
├─ Ninguna (solo red)
│  ├─ Responder a la escucha  → [[Envenenamiento de resolución de nombres]]   ← el primer hash del pentest
│  │  └─ ¿el hash no rompe? ¿hay objetivos sin firma?  → [[Relay de NTLM]] (no depende de romper)
│  └─ ¿Cuentas sin preautenticación?  → [[AS-REP roasting]]   ← tampoco necesita credencial
├─ Una credencial de dominio cualquiera
│  ├─ SIEMPRE PRIMERO          → [[Enumeración LDAP del directorio]]
│  ├─ ¿Cuentas de servicio con SPN?  → [[Kerberoasting]]
│  ├─ ¿PKI mal configurada?  → certipy find
│  │  ├─ plantilla deja poner el SAN  → [[ADCS - certificado con SAN arbitrario]] (ESC1)
│  │  ├─ plantilla mal por EKU/agente/ACL  → [[ADCS - plantilla abusable por propósito o ACL]] (ESC2/3/4)
│  │  └─ la CA misma (bandera/ACL/relay)  → [[ADCS - abuso de la configuración de la CA]] (ESC6/7/8)
│  ├─ ¿Escritura sobre una máquina?  → [[Delegación basada en recursos]]   ← la que más rinde hoy
│  ├─ ¿Controlo una cuenta con msDS-AllowedToDelegateTo?  → [[Delegación restringida]]
│  └─ ¿Cadena de permisos hacia un objetivo?  → cadenas del grafo (en la enumeración)
├─ Admin local en un host
│  ├─ ¿El host tiene delegación sin restricciones?  → [[Delegación sin restricciones]] → coacción → TGT del DC
│  ├─ ¿Sesiones de otros en memoria?
│  │  ├─ hash NTLM   → [[LSASS - volcado vía comsvcs.dll MiniDump]] → [[Pass-the-hash]]
│  │  └─ ticket      → robar de memoria → [[Pass-the-ticket]]
│  └─ reutilización de admin local → [[Pass-the-hash]] en masa
└─ Admin de dominio (o derechos delegados)
   ├─ los secretos de todo el dominio  → [[DCSync]]
   ├─ ¿el dominio NO es la raíz del bosque?  → [[Escalada intra-bosque por SID History]]   ← el límite es el bosque, no el dominio
   ├─ ¿hay una confianza a otro bosque?  → [[Movimiento entre bosques por la clave de confianza]]
   └─ persistencia
      ├─ forjar identidad            → [[Golden ticket]]
      └─ certificado de larga vida   → [[ADCS - certificado con SAN arbitrario]]
```

El orden dentro de cada nivel importa: **enumerar antes que explotar**, siempre. Todo lo demás se elige mirando lo que [[Enumeración LDAP del directorio]] devolvió.

## Árbol de decisión — moverme a otra máquina, ¿con qué?

```
¿Qué material tengo del objetivo?
├─ Hash NTLM
│  ├─ ¿NTLM habilitado?  → [[Pass-the-hash]]
│  └─ ¿solo Kerberos?    → usar el hash para pedir un ticket, y pasar a la fila de abajo
├─ Ticket de Kerberos
│  ├─ en memoria de un host que controlo  → [[Pass-the-ticket]]
│  └─ puedo forjarlo (tengo el secreto de firma)  → [[Golden ticket]]
└─ Certificado
   └─ [[ADCS - certificado con SAN arbitrario]]   ← el que sobrevive al cambio de contraseña
```

Dos cosas que este árbol codifica:

**NTLM contra Kerberos no es solo sintaxis.** Pasar el hash genera NTLM donde el dominio usa Kerberos, y ese desajuste es una señal. Pasar el ticket es Kerberos, o sea invisible a nivel de protocolo. La elección tiene consecuencia defensiva directa.

**El certificado es la peor persistencia** porque no se invalida cambiando la contraseña. Vale por años y sobrevive a la respuesta a incidentes que rota credenciales y cierra el caso.

## Orden de aprendizaje

Este es el temario del módulo, y sigue la ruta de un ataque real.

1. Modelo de autenticación: **NTLM contra Kerberos** — sin esto nada más se entiende
2. [[Enumeración LDAP del directorio]] — el directorio es una base de datos legible; el mapa lo decide todo
3. [[AS-REP roasting]] → [[Kerberoasting]] — credenciales sin privilegios, atacadas fuera de línea
4. [[LSASS - volcado vía comsvcs.dll MiniDump]] — dónde viven las credenciales en memoria
5. [[Pass-the-hash]] → [[Pass-the-ticket]] — movimiento lateral, y qué autentica cada protocolo
6. [[DCSync]] — los secretos del dominio sin tocar un endpoint
7. [[Golden ticket]] y [[ADCS - certificado con SAN arbitrario]] — persistencia que sobrevive a la limpieza

El punto 1 va primero y no es negociable: casi todas las técnicas del dominio son consecuencia de cómo funcionan esos dos protocolos, no de un fallo.

## Cheatsheets — entrada directa a los comandos

Cuando ya sabés qué hacer y solo querés la invocación, sin pasar por las notas de criterio:

| Matriz | Cubre |
|---|---|
| [[AD enumeración - matriz de referencia]] | Sin credencial y con credencial, consultas LDAP puntuales, BloodHound, la máscara de bits de `userAccountControl` |
| [[AD roasting - matriz de referencia]] | AS-REP y Kerberoast: pedir, formatos, modos de hashcat, silver ticket como atajo |
| [[AD volcado de credenciales - matriz de referencia]] | LSASS, SAM, LSA Secrets, NTDS, DPAPI — y qué permite cada formato |
| [[AD movimiento lateral - matriz de referencia]] | Pass-the-hash, pass-the-ticket, overpass, los cinco métodos de ejecución remota y su ruido |
| [[AD persistencia - matriz de referencia]] | Golden, silver, diamond, ADCS de `ESC1` a `ESC8`, ACL, y por qué `krbtgt` se rota dos veces |
| [[AD delegaciones - matriz de referencia]] | Sin restricciones (coacción + captura de TGT), restringida (`S4U`), RBCD (escribir el atributo + `S4U`) |
| [[AD envenenamiento y relay - matriz de referencia]] | Responder, romper NetNTLMv2, comprobar firma, `ntlmrelayx` a SMB/LDAP/ADCS, coacción |
| [[ADCS - matriz de referencia]] | El catálogo `ESC1`–`ESC15` con el comando de cada uno, THEFT, Shadow Credentials, `certipy` |
| [[AD confianzas - matriz de referencia]] | Enumerar confianzas, SID History a la raíz del bosque, clave de confianza inter-reino, filtrado de SID |

## Cara azul

El mapa completo de qué emite cada técnica y qué la ve. **Esta tabla es la bisagra del dominio** — es lo que conecta cada nota roja con su fuente en `550-telemetria/`.

| Técnica | Telemetría | Firma |
|---|---|---|
| [[Envenenamiento de resolución de nombres]] | [[Sysmon EID 3 - NetworkConnect]] | Endpoint conectándose a un host de resolución no autorizado — [[Conexión a host de resolución de nombres no autorizado]] |
| [[Relay de NTLM]] | [[Windows 4624 - Successful logon]] | Logon NTLM de la víctima desde un origen ajeno — lo cubre [[Autenticación NTLM donde el dominio usa Kerberos]] |
| [[Enumeración LDAP del directorio]] | [[Windows 4624 - Successful logon]] | Casi nada: es tráfico legítimo. El punto ciego de AD |
| [[AS-REP roasting]] | [[Windows 4768 - Kerberos TGT requested]] | Ticket inicial con preautenticación en cero — casi sin falsos positivos |
| [[Kerberoasting]] | [[Windows 4769 - Kerberos service ticket requested]] | Cifrado RC4, y volumen anormal de servicios pedidos |
| [[LSASS - volcado vía comsvcs.dll MiniDump]] | [[Sysmon EID 10 - ProcessAccess]] | Acceso a memoria de LSASS — [[Acceso a LSASS desde proceso no firmado]] |
| [[Pass-the-hash]] | [[Windows 4624 - Successful logon]] | Tipo 3 + NTLM donde debería haber Kerberos |
| [[Pass-the-ticket]] | [[Sysmon EID 10 - ProcessAccess]] | El robo del ticket, no el uso: se detecta el paso anterior |
| [[DCSync]] | [[Windows 4662 - Directory object operation]] | Derechos de replicación desde algo que no es un DC |
| [[Golden ticket]] | [[Windows 4769 - Kerberos service ticket requested]] | Ticket de servicio sin ticket inicial previo; cuenta inexistente |
| [[ADCS - certificado con SAN arbitrario]] | [[Windows 4887 - Certificate Services issued]] · [[Windows 4768 - Kerberos TGT requested]] | SAN que no corresponde al solicitante en la emisión — [[Certificado emitido con sujeto ajeno al solicitante]]; el uso, [[Autenticación por certificado a cuenta privilegiada]] |
| [[ADCS - plantilla abusable por propósito o ACL]] | [[Windows 4662 - Directory object operation]] | Modificación de plantilla (ESC4/13) — firma escribible; el uso del cert lo ve la de PKINIT |
| [[ADCS - abuso de la configuración de la CA]] | [[Windows 4624 - Successful logon]] | ESC8/11 son relay → NTLM anómalo; ESC7 modifica la CA → escritura en `4662` |
| [[Escalada intra-bosque por SID History]] | [[Windows 4769 - Kerberos service ticket requested]] | SID de otro dominio en el PAC; `SIDHistory` en reposo — sin detección propia |
| [[Movimiento entre bosques por la clave de confianza]] | [[Windows 4769 - Kerberos service ticket requested]] | Ticket inter-reino anómalo por dirección o cuenta — sin detección propia |
| [[Delegación sin restricciones]] | [[Windows 4768 - Kerberos TGT requested]] | Cuenta de alto valor autenticándose a un host con delegación — sin detección propia |
| [[Delegación restringida]] | [[Windows 4769 - Kerberos service ticket requested]] | Ticket `S4U` con `Transited Services` e impersonación privilegiada — [[Impersonación por delegación S4U]] |
| [[Delegación basada en recursos]] | [[Windows 4662 - Directory object operation]] | Escritura de `msDS-AllowedToActOnBehalfOfOtherIdentity` — [[Escritura del atributo de delegación RBCD]] |

Tres lecciones que este dominio deja, y que valen para todo el vault:

**Cuando el ataque es fuera de línea, se detecta la petición, no el ataque.** Kerberoasting y AS-REP roasting rompen el material sin conexión: no hay nada que ver mientras se rompe. La única ventana es el momento de pedir.

**Cuando el uso es invisible, se detecta el paso anterior.** Pasar el ticket es Kerberos legítimo; lo que se ve es el robo del ticket de memoria, que es el mismo acceso a LSASS que ya tiene detección.

**La fidelidad más alta puede no dejar rastro si la fuente no está bien configurada.** [[DCSync]] es de altísima fidelidad y **no emite nada** si la auditoría no está puesta sobre el objeto raíz del dominio — el segundo paso de configuración que nadie hace. Ver [[Ausencia de alertas no es ausencia de ataque]].

**La delegación se detecta por configuración, no por firma, y solo una de las tres tiene señal escribible.** Las tres variantes piden tickets legítimos —no forjan nada—, así que no hay firma criptográfica que las delate. RBCD es la excepción: su paso de configuración es una **escritura de atributo** de altísima fidelidad —[[Escritura del atributo de delegación RBCD]], análoga a la de DCSync—. Las otras dos, sin restricciones y restringida, no escriben nada detectable: su señal es la anomalía de relación (una cuenta de alto valor autenticándose a un host con delegación, un `S4U` con impersonación privilegiada), que necesita línea base y no tiene detección propia escrita.

## Huecos conocidos

- [x] Enumeración, las dos técnicas de roasting, volcado de credenciales, movimiento lateral por hash y ticket, DCSync, dos persistencias
- [x] Cada técnica enlaza su artefacto de Windows — la cara azul de la tabla está completa
- [x] Cara azul — once detecciones: [[Solicitud de TGT sin preautenticación]], [[Tickets de servicio con cifrado débil en volumen]], [[Replicación de directorio desde un origen no autorizado]], [[Autenticación NTLM donde el dominio usa Kerberos]], [[Ticket de servicio sin ticket inicial previo]], [[Acceso a LSASS desde proceso no firmado]], [[Escritura del atributo de delegación RBCD]], [[Conexión a host de resolución de nombres no autorizado]], [[Autenticación por certificado a cuenta privilegiada]], [[Impersonación por delegación S4U]] y [[Certificado emitido con sujeto ajeno al solicitante]]
- [x] Delegaciones: sin restricciones, restringida, RBCD — [[T1558 - Steal or Forge Kerberos Tickets]] con tres tradecraft y su matriz. RBCD cierra su ciclo rojo↔azul; las otras dos quedan con detección declarada como hueco
- [x] La rama **sin credencial** — [[T1557.001 - LLMNR NBT-NS Poisoning and SMB Relay]] con captura ([[Envenenamiento de resolución de nombres]]) y relay ([[Relay de NTLM]]), su matriz, y la detección [[Conexión a host de resolución de nombres no autorizado]] que estrena [[Sysmon EID 3 - NetworkConnect]]. El relay converge en detecciones existentes (NTLM anómalo, escritura de RBCD)
- [ ] **[[Enumeración LDAP del directorio]] queda sin detección a propósito.** Tráfico legítimo indistinguible; es el punto ciego del dominio y se declara, no se esconde
- [x] Detección de delegación **restringida** — [[Impersonación por delegación S4U]] ancla en el `4769` con `Transited Services` e impersonación privilegiada
- [ ] **Detección de delegación sin restricciones** — sigue abierta: su señal es una anomalía de relación (cuenta de alto valor autenticándose a un host con `TRUSTED_FOR_DELEGATION`) que necesita línea base y lista de hosts con delegación, no un campo de un evento
- [ ] Ninguna detección está validada en laboratorio. Es el trabajo que HTB alimenta directo
- [ ] Envenenamiento de nombres (LLMNR/NBT-NS) + relay NTLM — la rama "sin credencial" que falta
- [x] ADCS más allá de ESC1 — [[ADCS - plantilla abusable por propósito o ACL]] (ESC2/3/4/13/15) y [[ADCS - abuso de la configuración de la CA]] (ESC6/7/8/11), con el catálogo completo en [[ADCS - matriz de referencia]]. ESC8/11 cruzan con [[Relay de NTLM]]
- [x] Detección de ADCS en dos fases: la **emisión** con [[Certificado emitido con sujeto ajeno al solicitante]] (SAN ≠ solicitante, sobre el nuevo artefacto [[Windows 4887 - Certificate Services issued]]) y el **uso** con [[Autenticación por certificado a cuenta privilegiada]] (`4768` PKINIT). La de emisión es de alta fidelidad y llega a tiempo; ambas necesitan la auditoría de AD CS encendida, el mismo punto ciego que el `4662` de DCSync
- [x] Confianzas entre dominios y bosques — [[T1134.005 - SID-History Injection]] con [[Escalada intra-bosque por SID History]] (hijo → raíz del bosque) y [[Movimiento entre bosques por la clave de confianza]] (TGT inter-reino), y su matriz. El principio "el límite es el bosque, no el dominio" queda escrito
- [ ] **Detección de abuso de confianza.** El `4769` inter-reino y el SID inyectado se consumen por las reglas de golden, pero ninguna distingue el SID de escalada ni el ticket que cruza mal. La señal en reposo de mayor retorno es auditar el atributo `SIDHistory`
