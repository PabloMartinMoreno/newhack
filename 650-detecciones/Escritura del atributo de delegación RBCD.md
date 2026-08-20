---
tipo: deteccion
tecnicas: ["[[T1558 - Steal or Forge Kerberos Tickets]]"]
telemetria: ["[[Windows 4662 - Directory object operation]]"]
forma: evento
ventana: 
estado: idea
fidelidad: alta
logica: sigma
validada: 
aliases:
  - detección de RBCD
tags:
  - dominio/ad
---

# Escritura del atributo de delegación RBCD

## Qué detecta

Una escritura sobre el atributo `msDS-AllowedToActOnBehalfOfOtherIdentity` de un objeto de máquina. Es la firma de [[Delegación basada en recursos]], y no tiene falsos positivos reales fuera de la administración deliberada de delegación: ese atributo casi nunca se escribe, y una escritura fuera del flujo de administración es el ataque casi con certeza.

Es la contracara azul de la rama de delegación que más rinde del lado rojo, y de las de mayor fidelidad de AD —análoga a la de DCSync, y por el mismo motivo: ancla en una operación de directorio que no tiene explicación legítima común—.

## Lógica

```yaml
detection:
  selection:
    EventID: 4662
    ObjectType|contains: 'computer'
    Properties|contains: '3f78c3e5-f79a-46bd-a0b8-9d18116ddc79'  # msDS-AllowedToActOnBehalfOfOtherIdentity
    AccessMask: '0x20'                                            # WriteProperty
  condition: selection
```

El identificador de `Properties` es el atributo de RBCD. La máscara `0x20` es escritura de propiedad. Una escritura de ese atributo específico es el paso 2 de la cadena de RBCD, el que configura la delegación que el atacante después abusa.

Complemento de mayor cobertura: correlacionar con el `4741` (creación de cuenta de equipo) inmediatamente anterior, que es el paso 1 —crear la cuenta de máquina que se pone en el atributo—. Los dos juntos, en la misma ventana y desde el mismo origen, son la cadena de RBCD completa.

## El requisito previo, que es donde casi siempre falla

> [!important] Esta regla no existe si la fuente no está bien configurada
> [[Windows 4662 - Directory object operation]] solo se genera si la auditoría de acceso al servicio de directorio está **configurada sobre los objetos de máquina** —no solo habilitada por directiva—. Es el mismo segundo paso de configuración que la detección de DCSync, y el mismo punto ciego: sin él, la escritura de RBCD **no deja rastro**.
>
> Verificar que el `4662` se genera para escrituras de atributo es el primer paso, antes de escribir la regla. Es otro caso de [[Ausencia de alertas no es ausencia de ataque]]: la señal de mayor fidelidad de la delegación depende de una auditoría que suele faltar.

## Falsos positivos conocidos

- **Configuración legítima de RBCD** por un administrador —algunas herramientas de gestión la usan para clústeres o para delegación de servicios—. Son pocas, conocidas, y cada una es una relación de delegación que conviene inventariar de todos modos: es exactamente la superficie que el atacante busca.
- La escritura desde una cuenta de administración conocida, en el flujo esperado, se excluye por cuenta.

## Evasiones conocidas

- **La fuente apagada**, igual que en DCSync: es el estado por defecto y la evasión más efectiva, que no controla el atacante.
- **Escribir el atributo con permisos ya delegados** desde una cuenta excluida: por eso las exclusiones hay que tratarlas como privilegiadas.
- Las otras dos ramas de delegación —[[Delegación sin restricciones]] y [[Delegación restringida]]— **no escriben este atributo**, así que esta regla no las cubre. Sus detecciones quedan como huecos declarados en [[MOC - Active Directory]]; RBCD es la única de las tres con una firma de escritura de alta fidelidad.

## Cómo se prueba

Disparador: [[Delegación basada en recursos]] en laboratorio, escribiendo el atributo sobre una máquina.

Forma `evento`, un disparo la valida —después de confirmar que el `4662` se genera con la auditoría sobre los objetos de máquina—.
