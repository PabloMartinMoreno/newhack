---
tipo: deteccion
tecnicas: ["[[T1134.005 - SID-History Injection]]"]
telemetria: ["[[Windows 4765 - SID History added]]"]
forma: evento
ventana: 
estado: idea
fidelidad: alta
logica: sigma
validada: 
aliases:
  - detección de SID History
tags:
  - dominio/ad
---

# SID History agregado a una cuenta

## Qué detecta

La escritura de un SID de grupo privilegiado en el atributo `SIDHistory` de una cuenta. Es la firma de [[Persistencia por SID History]]: agregar el SID de *Domain Admins* o *Enterprise Admins* al historial de una cuenta común la vuelve miembro silencioso de ese grupo, y el evento `4765` registra la escritura con el SID agregado.

No tiene falsos positivos reales fuera de una migración de dominio: escribir `SIDHistory` es rarísimo en un entorno estable, y con un SID administrativo es casi con certeza el ataque. Es de las detecciones de mayor fidelidad de AD, análoga a las de DCSync y RBCD.

## Lógica

```yaml
detection:
  selection:
    EventID: 4765                        # SID History agregado
  privileged_sid:
    SourceSid|endswith:
      - '-512'                           # Domain Admins
      - '-519'                           # Enterprise Admins
      - '-518'                           # Schema Admins
      - '-516'                           # Domain Controllers
  condition: selection and privileged_sid
```

Anclar en el `SourceSid` —el SID agregado— es lo que separa la persistencia del atacante de una migración legítima: una migración copia el historial de grupos de una cuenta real, no inyecta el SID de un grupo administrativo en una cuenta común. Cualquier `4765` con un SID que termina en `-512`/`-519`/`-518` es el ataque.

Complemento de mayor cobertura: alertar **toda** escritura de `SIDHistory` (`4765`) sin restringir el SID, y triarla —fuera de una ventana de migración conocida, ninguna es legítima—. Es viable porque el evento casi no ocurre.

## El requisito previo

> [!important] Requiere auditoría de gestión de cuentas
> [[Windows 4765 - SID History added]] necesita `Audit User Account Management` (éxito y fallo) habilitado por directiva. Es un paso de configuración menos exótico que el `4662` de DCSync, pero igual hay que encenderlo; sin él, la escritura de `SIDHistory` no deja rastro.

## Falsos positivos conocidos

- **Migración de dominio legítima** — el único caso real, y acotado en el tiempo. Durante una migración conocida se suprime o se triaje; fuera de ella, no hay `4765` legítimo.
- Herramientas de migración de identidad que usen el atributo por diseño — se conocen y se excluyen mientras corren.

## Evasiones conocidas

- **La variante de ticket forjado** ([[Escalada intra-bosque por SID History]]) **no escribe el atributo**: inyecta el SID en el PAC del ticket, así que no genera `4765` y esta regla no la ve. La cubre parcialmente la detección de golden; es un hueco distinto, declarado en [[MOC - Active Directory]].
- **La auditoría de gestión de cuentas apagada**: sin ella el evento no existe.
- **Escribir el atributo directamente en la base del directorio** sin pasar por la API que genera el evento (acceso offline a `ntds.dit`): no dispara el `4765`, pero requiere un nivel de acceso que ya es compromiso total.

## Cómo se prueba

Disparador: [[Persistencia por SID History]] en laboratorio —`mimikatz sid::add` o DSInternals sobre una cuenta controlada, con un SID administrativo—.

Forma `evento`, un disparo la valida después de confirmar que el `4765` se genera con la auditoría de gestión de cuentas activa.
