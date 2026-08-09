---
tipo: deteccion
tecnicas: ["[[T1003.006 - DCSync]]"]
telemetria: ["[[Windows 4662 - Directory object operation]]"]
forma: evento
ventana: 
estado: idea
fidelidad: alta
logica: sigma
validada: 
aliases:
  - detección de DCSync
tags:
  - dominio/ad
---

# Replicación de directorio desde un origen no autorizado

## Qué detecta

Una operación que invoca los **derechos extendidos de replicación** del directorio, desde una cuenta que no es un controlador de dominio. Es la firma de [[DCSync]], y no tiene falsos positivos reales: fuera de los controladores hablando entre sí, nada pide replicación legítimamente.

## Lógica

```yaml
detection:
  selection:
    EventID: 4662
    Properties|contains:
      - '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2'   # DS-Replication-Get-Changes
      - '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'   # DS-Replication-Get-Changes-All
      - '89e95b76-444d-4c62-991a-0facbeda640c'   # Get-Changes-In-Filtered-Set
  filter_dc:
    SubjectUserName|endswith: '$'                # cuentas de máquina (los DC)
  condition: selection and not filter_dc
```

Los identificadores de `Properties` son los derechos de replicación. El filtro por `$` excluye las cuentas de máquina — que son las de los controladores legítimos. Lo que queda es una cuenta de usuario pidiendo replicar, que es exactamente el ataque.

Refinamiento de mayor precisión todavía: en vez de excluir todas las cuentas de máquina, mantener una **lista blanca de los controladores conocidos** por nombre. Un controlador falso agregado por un atacante también termina en `$`, y esa variante la lista blanca sí la atrapa.

## El requisito previo, que es donde casi siempre falla

> [!important] Esta regla no existe si la fuente no está bien configurada
> [[Windows 4662 - Directory object operation]] solo se genera si la auditoría de acceso al servicio de directorio está **configurada sobre el objeto raíz del dominio** — no solo habilitada por directiva. Es un segundo paso de configuración, sobre el objeto, que casi nadie hace.
>
> Sin ese paso, DCSync **no deja rastro** y el panel en cero se lee como "no pasó nada". Es el caso más claro de [[Ausencia de alertas no es ausencia de ataque]] en el vault: la detección de mayor fidelidad del dominio depende por completo de una configuración que suele faltar.
>
> Verificar que el evento se genera es el primer paso, antes de escribir la regla. Si no se genera, el trabajo es configurar la auditoría, no ajustar la lógica.

## Falsos positivos conocidos

- **Cuentas de sincronización legítimas** — algunas herramientas de sincronización de identidad con la nube usan estos derechos por diseño. Son el único falso positivo real, se conocen, y se excluyen por cuenta. Que existan es en sí mismo un dato: cada una es una cuenta que puede hacer DCSync, y hay que saber cuáles son.
- **Un controlador recién promovido** replicando por primera vez.

## Evasiones conocidas

- **La fuente apagada.** No es una evasión que haga el atacante: es el estado por defecto del entorno. Es la "evasión" más efectiva y la más común, y no la controla el atacante.
- **Comprometer una cuenta de sincronización ya excluida** y usarla para el DCSync. Cae en la exclusión y no dispara. Por eso las exclusiones de esta regla hay que tratarlas como cuentas privilegiadas, no como ruido.
- **Leer la base del directorio de otra forma** —copia de la base, o acceso físico al controlador— no pasa por el protocolo de replicación y no genera este evento.

## Cómo se prueba

Disparador: [[DCSync]] en laboratorio, con una cuenta que tenga los derechos delegados.

Forma `evento`, un disparo la valida — **pero solo después de confirmar que el evento 4662 se genera** con la auditoría sobre el objeto raíz. Ese es el paso que decide si la regla es escribible o si el trabajo es configurar la fuente primero.
