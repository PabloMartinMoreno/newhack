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
│  ├─ ¿Cuentas sin preautenticación?  → [[AS-REP roasting]]   ← no necesita credencial
│  └─ envenenamiento de nombres + relay  (sin nota propia todavía)
├─ Una credencial de dominio cualquiera
│  ├─ SIEMPRE PRIMERO          → [[Enumeración LDAP del directorio]]
│  ├─ ¿Cuentas de servicio con SPN?  → [[Kerberoasting]]
│  ├─ ¿Plantilla de certificado abusable?  → [[ADCS - certificado con SAN arbitrario]]
│  └─ ¿Cadena de permisos hacia un objetivo?  → cadenas del grafo (en la enumeración)
├─ Admin local en un host
│  ├─ ¿Sesiones de otros en memoria?
│  │  ├─ hash NTLM   → [[LSASS - volcado vía comsvcs.dll MiniDump]] → [[Pass-the-hash]]
│  │  └─ ticket      → robar de memoria → [[Pass-the-ticket]]
│  └─ reutilización de admin local → [[Pass-the-hash]] en masa
└─ Admin de dominio (o derechos delegados)
   ├─ los secretos de todo el dominio  → [[DCSync]]
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

## Cara azul

El mapa completo de qué emite cada técnica y qué la ve. **Esta tabla es la bisagra del dominio** — es lo que conecta cada nota roja con su fuente en `550-telemetria/`.

| Técnica | Telemetría | Firma |
|---|---|---|
| [[Enumeración LDAP del directorio]] | [[Windows 4624 - Successful logon]] | Casi nada: es tráfico legítimo. El punto ciego de AD |
| [[AS-REP roasting]] | [[Windows 4768 - Kerberos TGT requested]] | Ticket inicial con preautenticación en cero — casi sin falsos positivos |
| [[Kerberoasting]] | [[Windows 4769 - Kerberos service ticket requested]] | Cifrado RC4, y volumen anormal de servicios pedidos |
| [[LSASS - volcado vía comsvcs.dll MiniDump]] | [[Sysmon EID 10 - ProcessAccess]] | Acceso a memoria de LSASS — [[Acceso a LSASS desde proceso no firmado]] |
| [[Pass-the-hash]] | [[Windows 4624 - Successful logon]] | Tipo 3 + NTLM donde debería haber Kerberos |
| [[Pass-the-ticket]] | [[Sysmon EID 10 - ProcessAccess]] | El robo del ticket, no el uso: se detecta el paso anterior |
| [[DCSync]] | [[Windows 4662 - Directory object operation]] | Derechos de replicación desde algo que no es un DC |
| [[Golden ticket]] | [[Windows 4769 - Kerberos service ticket requested]] | Ticket de servicio sin ticket inicial previo; cuenta inexistente |
| [[ADCS - certificado con SAN arbitrario]] | [[Windows 4768 - Kerberos TGT requested]] | Certificado a nombre ajeno; persistencia casi indetectable |

Tres lecciones que este dominio deja, y que valen para todo el vault:

**Cuando el ataque es fuera de línea, se detecta la petición, no el ataque.** Kerberoasting y AS-REP roasting rompen el material sin conexión: no hay nada que ver mientras se rompe. La única ventana es el momento de pedir.

**Cuando el uso es invisible, se detecta el paso anterior.** Pasar el ticket es Kerberos legítimo; lo que se ve es el robo del ticket de memoria, que es el mismo acceso a LSASS que ya tiene detección.

**La fidelidad más alta puede no dejar rastro si la fuente no está bien configurada.** [[DCSync]] es de altísima fidelidad y **no emite nada** si la auditoría no está puesta sobre el objeto raíz del dominio — el segundo paso de configuración que nadie hace. Ver [[Ausencia de alertas no es ausencia de ataque]].

## Huecos conocidos

- [x] Enumeración, las dos técnicas de roasting, volcado de credenciales, movimiento lateral por hash y ticket, DCSync, dos persistencias
- [x] Cada técnica enlaza su artefacto de Windows — la cara azul de la tabla está completa
- [ ] **Ninguna detección de AD escrita todavía.** La telemetría está mapeada; las reglas de `650-detecciones/` no existen salvo la de LSASS. Es el trabajo que sigue, y el que HTB va a alimentar
- [ ] Envenenamiento de nombres (LLMNR/NBT-NS) + relay NTLM — la rama "sin credencial" que falta
- [ ] Delegaciones: constrained, unconstrained, RBCD — un eje propio de escalada
- [ ] ADCS más allá de la plantilla de sujeto arbitrario — hay muchas otras configuraciones abusables
- [ ] Confianzas entre dominios y bosques
