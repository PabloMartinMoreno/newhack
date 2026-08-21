---
tipo: telemetria
plataforma: [windows]
producto: Windows Security
identificador: "4765"
por-defecto: false
coste: bajo
aliases:
  - 4765
  - 4766
  - SID History agregado
tags:
  - plataforma/windows
---

# Windows 4765 - SID History added

## Qué lo genera

Que se **agregue un SID al atributo `SIDHistory`** de una cuenta. `4765` es la operación exitosa; `4766` es el intento fallido. Es el único evento que ve la escritura de `SIDHistory` —el atributo que Windows trata como pertenencia a grupos a efectos de autorización—, y por lo tanto la única fuente de la variante de persistencia de [[T1134.005 - SID-History Injection]].

Es distinto del uso de un SID inyectado en un **ticket forjado**: aquella variante ([[Escalada intra-bosque por SID History]]) mete el SID en el PAC del ticket y no toca el atributo, así que no genera este evento. `4765` ve la otra variante: la que **escribe el atributo** para persistir.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `TargetSid` / `TargetUserName` | La cuenta a la que se le agregó | Dónde quedó la persistencia |
| `SourceSid` | El SID agregado al historial | **El campo del ataque**: un SID de grupo privilegiado |
| `SubjectUserName` | Quién hizo la escritura | La cuenta que ejecutó el ataque |

El `SourceSid` es lo que decide: un SID de un grupo administrativo —Domain Admins (`-512`), Enterprise Admins (`-519`)— agregado al historial de una cuenta común es la firma. Ese SID convierte a la cuenta en miembro silencioso del grupo, sin aparecer en la lista de membresías.

## Coste de recolección

Bajo. La escritura de `SIDHistory` es rarísima —solo ocurre en migraciones de dominio reales—, así que el evento casi no se genera en un entorno estable. Es de los artefactos más baratos y de mayor señal.

## Cómo se activa

No viene por defecto. Requiere **auditoría de administración de cuentas de usuario** (`Audit User Account Management`, éxito y fallo) por directiva. Es un paso de configuración menos exótico que la auditoría de directorio del `4662`, pero igual hay que encenderlo.

## Limitaciones

- **No viene activado** por defecto; sin la auditoría de gestión de cuentas, la escritura no deja rastro.
- **No ve el SID inyectado en un ticket forjado** —esa variante no toca el atributo—: para eso haría falta inspeccionar el PAC, sin artefacto propio.
- **La migración legítima** genera este evento por diseño; la señal está en el SID agregado (privilegiado o no) y en el contexto (¿hay una migración en curso?), no en la mera escritura.

## Quién lo emite / quién lo consume

Rojo: [[Persistencia por SID History]] — la escritura del atributo con el SID de un grupo privilegiado.
Azul: [[SID History agregado a una cuenta]] — ancla en el `SourceSid` de un grupo administrativo.
