---
tipo: meta
aliases:
  - Sigma
  - reglas Sigma
  - sigmac
tags:
  - meta/referencia
---

# Sigma - matriz de referencia

> [!info] Referencia pura, no un zettel
> La sintaxis del formato en el que se escriben las detecciones de `logica: sigma`. Qué forma de detección soporta y cuál no está en [[Detección por forma - matriz de referencia]].

## 1. Esqueleto

```yaml
title: Intérprete de comandos como hijo del servidor web
id: 8f2e1a44-0000-0000-0000-000000000000
status: experimental
description: Un servidor de aplicación no tiene razón para ser padre de una shell
references:
  - https://attack.mitre.org/techniques/T1059/
author: v
date: 2026/08/09
tags:
  - attack.execution
  - attack.t1059
logsource:
  category: process_creation
  product: linux
detection:
  selection:
    ParentImage|endswith:
      - '/php-fpm'
      - '/nginx'
    Image|endswith:
      - '/sh'
      - '/bash'
  condition: selection
falsepositives:
  - Scripts de despliegue que corren bajo el usuario del servidor web
level: high
```

`title`, `logsource`, `detection` y `condition` son lo único obligatorio. El resto es metadato, y el que más rinde es `falsepositives`: una regla sin falsos positivos declarados no se puede triar.

## 2. `logsource` — de dónde salen los eventos

Es lo que decide a qué se traduce la regla. Un `logsource` mal puesto produce una consulta sintácticamente válida que no mira nada.

| Campo | Ejemplos |
|---|---|
| `category` | `process_creation` `network_connection` `file_event` `registry_set` `dns_query` `image_load` `ps_script` |
| `product` | `windows` `linux` `macos` `zeek` `aws` `azure` |
| `service` | `security` `sysmon` `powershell` `sshd` `webserver` |

Combinaciones que se usan seguido:

```yaml
logsource:
  product: windows
  service: security          # el registro de seguridad: 4624, 4768, 4769…
```
```yaml
logsource:
  category: process_creation
  product: windows           # Sysmon EID 1 o Windows 4688, según el backend
```

Esa última es la que hace valiosa la abstracción: la misma regla sale contra [[Sysmon EID 1 - ProcessCreate]] o contra [[Windows 4688 - Process creation]] según qué recolecte el cliente.

## 3. Modificadores de campo

| Modificador | Qué hace | Ejemplo |
|---|---|---|
| `contains` | Subcadena | `CommandLine|contains: 'whoami'` |
| `startswith` | Prefijo | `Image|startswith: 'C:\Users\'` |
| `endswith` | Sufijo | `Image|endswith: '\cmd.exe'` |
| `re` | Expresión regular | `CommandLine|re: '\s-[eE][nNcC]'` |
| `all` | Exige **todos** los valores de la lista, no uno | `CommandLine|contains|all:` |
| `base64offset|contains` | Busca el texto codificado en las tres alineaciones posibles | Payloads en `-EncodedCommand` |
| `windash` | Prueba `-` y `/` como prefijo de flag | `CommandLine|windash|contains: '-enc'` |
| `cidr` | Rango de red | `DestinationIp|cidr: '169.254.0.0/16'` |
| `lt` `lte` `gt` `gte` | Comparación numérica | `TicketEncryptionType|gte: 23` |

Sin `all`, una lista de valores es un **OR**. Es el error más frecuente al escribir una regla que quería exigir dos cosas a la vez.

`base64offset` existe porque una cadena codificada en base64 se ve distinta según en qué byte empiece dentro del bloque. Buscar una sola de las tres variantes falla dos de cada tres veces.

## 4. `condition`

```yaml
condition: selection                          # simple
condition: selection and not filtro           # con exclusión
condition: seleccion1 or seleccion2
condition: all of selection_*                 # comodín sobre nombres
condition: 1 of seleccion_* and not 1 of filtro_*
condition: selection | count() > 10           # agregación, ver abajo
```

Convención: lo que busca se llama `selection*`, lo que excluye `filter*`. No es obligatorio pero todos los repositorios lo siguen y los comodines dependen de eso.

## 5. Nulos y campos ausentes

```yaml
detection:
  selection:
    ParentImage: null           # el campo no existe o está vacío
  filtro:
    User|exists: false
```

Un campo ausente **no** es lo mismo que un campo vacío en la mayoría de los backends. Es la fuente de falsos negativos silenciosos: la regla se traduce bien y no matchea nunca.

## 6. Traducir a un backend

`sigma convert -t splunk regla.yml`
`sigma convert -t microsoft365defender regla.yml`
`sigma convert -t elasticsearch -f dsl_lucene regla.yml`
`sigma convert -t esql regla.yml`

`sigma check regla.yml`
Valida la sintaxis antes de traducir.

`sigma list targets`
`sigma plugin install splunk`

El comando viejo `sigmac` está reemplazado por `sigma convert` de `pySigma`. Las reglas siguen siendo compatibles; la línea de comandos no.

> [!warning] La traducción no es una garantía
> Que la regla convierta no significa que el campo exista en el destino. `ParentImage` es de Sysmon: en `Windows 4688` el campo se llama `ParentProcessName` y en Defender `InitiatingProcessFileName`. Los mapeos los trae el pipeline del backend, y donde falta un mapeo la consulta sale con el nombre crudo y devuelve cero para siempre. Ver [[Un log sin identidad es un historial, no una detección]].

`sigma convert -t splunk -p sysmon regla.yml`
El `-p` aplica el pipeline de mapeo. Sin él, la mitad de las reglas de Windows salen mal traducidas.

## 7. Correlaciones — lo que Sigma no hacía

La especificación de correlaciones cubre tres de las cuatro formas del vault:

```yaml
title: Fallos contra cuentas inexistentes
correlation:
  type: event_count
  rules:
    - fallo_de_login
  group-by:
    - SourceIp
  timespan: 5m
  condition:
    gte: 20
```

| `type` | Qué evalúa | `forma:` equivalente |
|---|---|---|
| `event_count` | Cuántos eventos en la ventana | `agregado` |
| `value_count` | Cuántos valores distintos de un campo | `agregado` |
| `temporal` | Varios tipos de evento dentro de una ventana | `correlacion` |
| `temporal_ordered` | Lo mismo, en orden | `correlacion` |

**No hay tipo para `invariante`.** Una condición que nunca debería violarse sobre una secuencia —una sesión activa después de su cierre— no se expresa en Sigma. Esas reglas del vault van directo en KQL. Es la razón por la que `logica:` es un campo y no una constante.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| La regla convierte y no matchea nunca | Nombre de campo del backend equivocado, o falta `-p pipeline` |
| Matchea de más | Una lista donde hacía falta `|all` — las listas son OR |
| `Sigma rule must have a detection` | Falta la clave `condition` dentro de `detection` |
| `Unknown identifier` en `condition` | El nombre de la selección no coincide, o el comodín `selection_*` no agarra nada |
| El backend rechaza `re:` | No todos soportan expresiones regulares. Reescribir con `contains` |
| Payload codificado que no aparece | Falta `base64offset|contains` |
| `count() > N` no traduce | El backend no soporta agregación. Es el límite real de Sigma |

## Relacionadas

[[Detección por forma - matriz de referencia]] · [[KQL - matriz de referencia]] · [[Sysmon - matriz de configuración]] · [[MOC - Fundamentos de detección]]
