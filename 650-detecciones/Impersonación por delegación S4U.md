---
tipo: deteccion
tecnicas: ["[[T1558 - Steal or Forge Kerberos Tickets]]"]
telemetria: ["[[Windows 4769 - Kerberos service ticket requested]]"]
forma: evento
ventana: 
estado: idea
fidelidad: media
logica: sigma
validada: 
aliases:
  - detección de S4U2Proxy
  - detección de delegación restringida
tags:
  - dominio/ad
---

# Impersonación por delegación S4U

## Qué detecta

Una solicitud de ticket de servicio que **impersona a un usuario vía S4U2Proxy** —la extensión de Kerberos que la delegación restringida y la RBCD usan para pedir un ticket en nombre de otro—. Es la firma de [[Delegación restringida]] y [[Delegación basada en recursos]] en el momento del abuso: la cadena `S4U2Self`/`S4U2Proxy` deja un `4769` con un campo que una petición normal no tiene.

Cierra parcialmente el hueco de delegación restringida del dominio. No ve la configuración —eso lo ve [[Escritura del atributo de delegación RBCD]] para RBCD—, ve el **uso**: el momento en que la delegación se abusa para impersonar.

## Lógica

```yaml
detection:
  selection:
    EventID: 4769
    TransmittedServices|exists: true      # el campo "Transited Services" no vacío = S4U2Proxy
  impersonation:
    # el usuario del ticket (TargetUserName) es privilegiado
    TargetUserName|contains:
      - 'Administrator'
      - 'Admin'
  filter_legit:
    # excluir las cuentas que hacen delegación legítima por diseño
    ServiceName|endswith: '$'             # ajustar a las cuentas de servicio conocidas
  condition: selection and impersonation and not filter_legit
```

El campo `Transited Services` (o `Transmitted Services`) no vacío es lo que marca S4U2Proxy: una petición de ticket normal no lo lleva. Que el usuario impersonado sea privilegiado es lo que separa la delegación legítima —que impersona usuarios comunes hacia su servicio— del abuso —que impersona a un administrador—.

Refinamiento: correlacionar con la cuenta que **hace** la petición. La delegación legítima la hace la cuenta de servicio configurada; una petición S4U desde una cuenta que no tiene delegación configurada —el caso de RBCD recién escrito— es más anómala todavía.

## Falsos positivos conocidos

- **Delegación restringida legítima** — un servidor web que impersona al usuario final contra la base de datos usa S4U2Proxy por diseño. Son las cuentas con `msDS-AllowedToDelegateTo` configurado, se conocen, y se excluyen. Que existan es un inventario útil: cada una es una cuenta cuyo compromiso da impersonación.
- **Protocol transition** en aplicaciones que lo usan correctamente.

## Evasiones conocidas

- **Impersonar una cuenta privilegiada que no matchee la lista de nombres**: por eso conviene el filtro por SID de grupos privilegiados, no por nombre.
- **La configuración de RBCD** (la escritura del atributo) es anterior y la ve [[Escritura del atributo de delegación RBCD]]; si esa se evadió (auditoría apagada), esta detección del uso es la segunda oportunidad.
- **Delegación sin restricciones** no usa S4U2Proxy —captura el TGT directo—, así que esta regla no la cubre: queda como hueco declarado en [[MOC - Active Directory]].

## Cómo se prueba

Disparador: [[Delegación restringida]] o [[Delegación basada en recursos]] en laboratorio, hasta la cadena `S4U2Self`/`S4U2Proxy` impersonando a un administrador.

Forma `evento`, un disparo la valida — el `4769` con `Transited Services` se genera siempre que se use S4U2Proxy, sin auditoría especial.
