---
tipo: moc
dominio: ad
aliases:
  - MOC AD
tags:
  - dominio/ad
---

# MOC - Active Directory

> [!abstract] Hub del dominio
> Superficie: [[Active Directory]]. Las fuentes de datos, en [[MOC - Telemetría de Windows]]. Los conceptos de detección, en [[MOC - Fundamentos de detección]]. Acá viven el **árbol maestro** (*lo que tenés → qué se abre*) y la **bisagra roja↔azul**; cada fase es un MOC propio, indexados abajo.

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
      ├─ certificado de larga vida   → [[ADCS - certificado con SAN arbitrario]]
      └─ miembro silencioso de un grupo  → [[Persistencia por SID History]]   ← no aparece en las membresías
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

## Las nueve fases — un MOC cada una

Cada fase es un MOC con su árbol de decisión, su cheatsheet (matriz de comandos) y su cara azul. Ordenadas por dependencia:

1. [[MOC - AD envenenamiento y relay]] — sin credencial: el primer hash y el reenvío
2. [[MOC - AD enumeración]] — el directorio como base de datos; **siempre primero** con credencial
3. [[MOC - AD roasting]] — credenciales que se rompen fuera de línea
4. [[MOC - AD volcado de credenciales]] — memoria, disco y el propio directorio
5. [[MOC - AD movimiento lateral]] — moverse con hash o ticket; NTLM contra Kerberos
6. [[MOC - AD delegaciones]] — actuar en nombre de otro: sin restricciones, restringida, RBCD
7. [[MOC - ADCS]] — la PKI que emite identidad
8. [[MOC - AD persistencia]] — volver a entrar tras la rotación
9. [[MOC - AD confianzas]] — del dominio al bosque

Las matrices de comandos viven dentro de cada MOC, en su sección *Cara roja*.

## Cara azul

El mapa completo de qué emite cada técnica y qué la ve. **Esta tabla es la bisagra del dominio** — es lo que conecta cada nota roja con su fuente en `550-telemetria/`. La *firma* —cómo se reconoce en el evento— vive en cada nota de detección; acá va solo el mapeo.

| Técnica | Emite | Detección |
|---|---|---|
| [[Envenenamiento de resolución de nombres]] | [[Sysmon EID 3 - NetworkConnect\|Sysmon 3]] | [[Conexión a host de resolución de nombres no autorizado]] |
| [[Relay de NTLM]] | [[Windows 4624 - Successful logon\|4624]] | [[Autenticación NTLM donde el dominio usa Kerberos]] |
| [[Enumeración LDAP del directorio]] | [[Windows 4624 - Successful logon\|4624]] | punto ciego — tráfico legítimo (a propósito) |
| [[AS-REP roasting]] | [[Windows 4768 - Kerberos TGT requested\|4768]] | [[Solicitud de TGT sin preautenticación]] |
| [[Kerberoasting]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | [[Tickets de servicio con cifrado débil en volumen]] |
| [[LSASS - volcado vía comsvcs.dll MiniDump]] | [[Sysmon EID 10 - ProcessAccess\|Sysmon 10]] | [[Acceso a LSASS desde proceso no firmado]] |
| [[Pass-the-hash]] | [[Windows 4624 - Successful logon\|4624]] | [[Autenticación NTLM donde el dominio usa Kerberos]] |
| [[Pass-the-ticket]] | [[Sysmon EID 10 - ProcessAccess\|Sysmon 10]] | el paso anterior — [[Acceso a LSASS desde proceso no firmado]] |
| [[DCSync]] | [[Windows 4662 - Directory object operation\|4662]] | [[Replicación de directorio desde un origen no autorizado]] |
| [[Golden ticket]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | [[Ticket de servicio sin ticket inicial previo]] |
| [[ADCS - certificado con SAN arbitrario]] · emisión | [[Windows 4887 - Certificate Services issued\|4887]] | [[Certificado emitido con sujeto ajeno al solicitante]] |
| [[ADCS - certificado con SAN arbitrario]] · uso | [[Windows 4768 - Kerberos TGT requested\|4768]] | [[Autenticación por certificado a cuenta privilegiada]] |
| [[ADCS - plantilla abusable por propósito o ACL]] | [[Windows 4662 - Directory object operation\|4662]] | el uso — [[Autenticación por certificado a cuenta privilegiada]] |
| [[ADCS - abuso de la configuración de la CA]] | [[Windows 4624 - Successful logon\|4624]] | ESC8/11 — [[Autenticación NTLM donde el dominio usa Kerberos]] |
| [[Escalada intra-bosque por SID History]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | en parte, la de golden |
| [[Persistencia por SID History]] | [[Windows 4765 - SID History added\|4765]] | [[SID History agregado a una cuenta]] |
| [[Movimiento entre bosques por la clave de confianza]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | sin detección propia |
| [[Delegación sin restricciones]] | [[Windows 4624 - Successful logon\|4624]] | [[Cuenta de alto valor autenticándose a host con delegación]] |
| [[Delegación restringida]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | [[Impersonación por delegación S4U]] |
| [[Delegación basada en recursos]] | [[Windows 4662 - Directory object operation\|4662]] | [[Escritura del atributo de delegación RBCD]] |

Tres lecciones que este dominio deja, y que valen para todo el vault:

**Cuando el ataque es fuera de línea, se detecta la petición, no el ataque.** Kerberoasting y AS-REP roasting rompen el material sin conexión: no hay nada que ver mientras se rompe. La única ventana es el momento de pedir.

**Cuando el uso es invisible, se detecta el paso anterior.** Pasar el ticket es Kerberos legítimo; lo que se ve es el robo del ticket de memoria, que es el mismo acceso a LSASS que ya tiene detección.

**La fidelidad más alta puede no dejar rastro si la fuente no está bien configurada.** [[DCSync]] es de altísima fidelidad y **no emite nada** si la auditoría no está puesta sobre el objeto raíz del dominio — el segundo paso de configuración que nadie hace. Ver [[Ausencia de alertas no es ausencia de ataque]].

**La delegación se detecta por configuración, no por firma, y solo una de las tres tiene señal escribible.** Las tres variantes piden tickets legítimos —no forjan nada—, así que no hay firma criptográfica que las delate. RBCD es la excepción: su paso de configuración es una **escritura de atributo** de altísima fidelidad —[[Escritura del atributo de delegación RBCD]], análoga a la de DCSync—. Las otras dos, sin restricciones y restringida, no escriben nada detectable: su señal es la anomalía de relación (una cuenta de alto valor autenticándose a un host con delegación, un `S4U` con impersonación privilegiada), que necesita línea base y no tiene detección propia escrita.

## Huecos conocidos

- [x] Dominio partido en **nueve MOCs por fase**, 1:1 con las matrices; este maestro queda de hub con el árbol *lo que tenés* y la bisagra roja↔azul
- [x] Enumeración, las dos técnicas de roasting, volcado de credenciales, movimiento lateral por hash y ticket, DCSync, dos persistencias
- [x] Cada técnica enlaza su artefacto de Windows — la cara azul de la tabla está completa
- [x] Cara azul — trece detecciones: [[Solicitud de TGT sin preautenticación]], [[Tickets de servicio con cifrado débil en volumen]], [[Replicación de directorio desde un origen no autorizado]], [[Autenticación NTLM donde el dominio usa Kerberos]], [[Ticket de servicio sin ticket inicial previo]], [[Acceso a LSASS desde proceso no firmado]], [[Escritura del atributo de delegación RBCD]], [[Conexión a host de resolución de nombres no autorizado]], [[Autenticación por certificado a cuenta privilegiada]], [[Impersonación por delegación S4U]], [[Certificado emitido con sujeto ajeno al solicitante]], [[Cuenta de alto valor autenticándose a host con delegación]] y [[SID History agregado a una cuenta]]
- [x] Delegaciones: sin restricciones, restringida, RBCD — [[T1558 - Steal or Forge Kerberos Tickets]] con tres tradecraft y su matriz. RBCD cierra su ciclo rojo↔azul; las otras dos quedan con detección declarada como hueco
- [x] La rama **sin credencial** — [[T1557.001 - LLMNR NBT-NS Poisoning and SMB Relay]] con captura ([[Envenenamiento de resolución de nombres]]) y relay ([[Relay de NTLM]]), su matriz, y la detección [[Conexión a host de resolución de nombres no autorizado]] que estrena [[Sysmon EID 3 - NetworkConnect]]. El relay converge en detecciones existentes (NTLM anómalo, escritura de RBCD)
- [ ] **[[Enumeración LDAP del directorio]] queda sin detección a propósito.** Tráfico legítimo indistinguible; es el punto ciego del dominio y se declara, no se esconde
- [x] Detección de delegación **restringida** — [[Impersonación por delegación S4U]] ancla en el `4769` con `Transited Services` e impersonación privilegiada
- [x] Detección de delegación **sin restricciones** — [[Cuenta de alto valor autenticándose a host con delegación]], una intersección de dos listas de activos (hosts con `TRUSTED_FOR_DELEGATION` × cuentas de alto valor) sobre el `4624`. Escribible, pero la fidelidad depende del inventario, no de un campo
- [ ] Ninguna detección está validada en laboratorio. Es el trabajo que HTB alimenta directo
- [ ] Envenenamiento de nombres (LLMNR/NBT-NS) + relay NTLM — la rama "sin credencial" que falta
- [x] ADCS más allá de ESC1 — [[ADCS - plantilla abusable por propósito o ACL]] (ESC2/3/4/13/15) y [[ADCS - abuso de la configuración de la CA]] (ESC6/7/8/11), con el catálogo completo en [[ADCS - matriz de referencia]]. ESC8/11 cruzan con [[Relay de NTLM]]
- [x] Detección de ADCS en dos fases: la **emisión** con [[Certificado emitido con sujeto ajeno al solicitante]] (SAN ≠ solicitante, sobre el nuevo artefacto [[Windows 4887 - Certificate Services issued]]) y el **uso** con [[Autenticación por certificado a cuenta privilegiada]] (`4768` PKINIT). La de emisión es de alta fidelidad y llega a tiempo; ambas necesitan la auditoría de AD CS encendida, el mismo punto ciego que el `4662` de DCSync
- [x] Confianzas entre dominios y bosques — [[T1134.005 - SID-History Injection]] con [[Escalada intra-bosque por SID History]] (hijo → raíz del bosque) y [[Movimiento entre bosques por la clave de confianza]] (TGT inter-reino), y su matriz. El principio "el límite es el bosque, no el dominio" queda escrito
- [x] Abuso de SID History por sus dos caras — **escalada** ([[Escalada intra-bosque por SID History]], SID en el PAC de un ticket forjado, cubierta en parte por la de golden) y **persistencia** ([[Persistencia por SID History]], escritura del atributo, cubierta por [[SID History agregado a una cuenta]] sobre el nuevo artefacto [[Windows 4765 - SID History added]]). La variante de ticket forjado sigue sin firma de escritura por diseño —no toca el directorio—; es un límite de la técnica, no un hueco de contenido
- [x] **Ciclo rojo↔azul de AD cerrado.** Cada rama roja tiene su artefacto y, salvo el ticket forjado que no deja escritura, su detección. Lo que queda es validación en laboratorio y afinado de las reglas de línea base por entorno, no contenido nuevo
