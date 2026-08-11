---
tipo: meta
aliases:
  - KQL
  - Kusto
  - Defender advanced hunting
tags:
  - meta/referencia
---

# KQL - matriz de referencia

> [!info] Referencia pura, no un zettel
> La sintaxis del lenguaje en el que están escritas las detecciones de `logica: kql`. Qué construcción corresponde a cada forma de detección está en [[Detección por forma - matriz de referencia]].

## 1. Tablas — dónde está cada cosa

Defender y Sentinel comparten lenguaje y no comparten esquema. Es el primer motivo por el que una consulta copiada no corre.

**Microsoft Defender XDR** (`advanced hunting`):

| Tabla | Qué trae |
|---|---|
| `DeviceProcessEvents` | Creación de procesos. Equivale a [[Sysmon EID 1 - ProcessCreate]] |
| `DeviceNetworkEvents` | Conexiones salientes |
| `DeviceFileEvents` | Creación, modificación y borrado de archivos |
| `DeviceRegistryEvents` | Cambios en el registro |
| `DeviceImageLoadEvents` | Carga de DLL |
| `DeviceLogonEvents` | Inicios de sesión |
| `DeviceEvents` | El cajón de sastre — acceso a LSASS cae acá, como `AntivirusDetection` y otros |
| `IdentityLogonEvents` | Autenticación vista desde el directorio |
| `IdentityDirectoryEvents` | Cambios en AD, incluida la replicación |

**Sentinel** (Log Analytics):

| Tabla | Qué trae |
|---|---|
| `SecurityEvent` | El registro de seguridad de Windows: `4624`, `4768`, `4769`, `4662` |
| `Event` | Sysmon y todo lo demás del registro de eventos |
| `SigninLogs` | Autenticación de Entra ID |
| `AuditLogs` | Cambios administrativos en el tenant |
| `W3CIISLog` | [[Log de acceso del servidor web]] en IIS |
| `Syslog` | Linux |

El mismo dato tiene nombre distinto según la tabla: la imagen del proceso es `FolderPath` en `DeviceProcessEvents`, `NewProcessName` en `SecurityEvent` y `Image` en Sysmon crudo.

## 2. Operadores base

```kql
DeviceProcessEvents
| where Timestamp > ago(24h)
| where FileName in~ ("cmd.exe", "powershell.exe")
| where InitiatingProcessFileName =~ "w3wp.exe"
| project Timestamp, DeviceName, AccountName, ProcessCommandLine
| order by Timestamp desc
| take 100
```

| Operador | Qué hace |
|---|---|
| `where` | Filtra. Va lo antes posible en la consulta |
| `project` | Elige columnas. `project-away` quita |
| `extend` | Columna calculada |
| `summarize` | Agrega |
| `join` | Une dos tablas |
| `union` | Concatena |
| `distinct` | Valores únicos |
| `top N by campo` | Los N mayores |
| `mv-expand` | Una fila por elemento de un array |

Comparación de cadenas:

| Forma | Sensible a mayúsculas | Nota |
|---|---|---|
| `==` | Sí | La más rápida |
| `=~` | No | La que casi siempre se quiere |
| `has` | No | Palabra completa, **indexada** |
| `contains` | No | Subcadena, lenta |
| `startswith` `endswith` | No | |
| `matches regex` | Sí | La más cara |
| `in` / `in~` | `in~` no | Lista |

> [!tip] `has` contra `contains`
> `has` usa el índice de términos y `contains` recorre el texto. Sobre volumen la diferencia es de minutos a segundos. `contains` solo hace falta cuando lo que se busca está pegado a otra cosa —parte de una ruta, o dentro de un parámetro—; para una palabra suelta, `has` siempre.

## 3. Tiempo

```kql
| where Timestamp between (ago(7d) .. ago(1d))
| summarize count() by bin(Timestamp, 1h)
| extend delta = datetime_diff('minute', Timestamp2, Timestamp1)
```

`bin()` es lo que convierte una serie de eventos en una ventana. Es la pieza de toda detección de `forma: agregado`.

## 4. Agregación

```kql
DeviceLogonEvents
| where Timestamp > ago(1h)
| summarize
    intentos = count(),
    cuentas  = dcount(AccountName),
    exitos   = countif(ActionType == "LogonSuccess")
  by RemoteIP, bin(Timestamp, 10m)
| where cuentas > 20 and exitos <= 2
```

| Función | Qué devuelve |
|---|---|
| `count()` | Filas |
| `dcount(x)` | Valores distintos, aproximado |
| `countif(cond)` | Filas que cumplen |
| `make_set(x)` | Conjunto de valores |
| `arg_max(t, *)` | La fila del mayor `t`, con todas sus columnas |
| `percentile(x, 95)` | Percentil |

`dcount` es aproximado por diseño. Para umbrales bajos —"más de tres cuentas"— usar `dcount(x, 4)` sube la precisión, o directamente `count(distinct)` vía `summarize by`.

La combinación `muchas cuentas / pocos éxitos` de arriba es password spraying; invertida —**pocas cuentas, muchos éxitos**— es credential stuffing. Es el mismo esqueleto de consulta y la diferencia está en dos umbrales. Ver [[Fallos de acceso contra cuentas inexistentes]].

## 5. `join` — correlacionar dos fuentes

```kql
let escrituras =
    DeviceFileEvents
    | where FolderPath has "wwwroot"
    | where FileName endswith ".aspx"
    | project DeviceName, FileName, tEscritura = Timestamp;
W3CIISLog
| where csUriStem has_any (escrituras)
| join kind=inner escrituras on $left.Computer == $right.DeviceName
| where Timestamp between (tEscritura .. tEscritura + 5m)
```

| `kind=` | Qué devuelve |
|---|---|
| `inner` | Solo lo que está en las dos. El que se quiere casi siempre |
| `leftouter` | Todo lo de la izquierda, con nulos donde no hay par |
| `leftanti` | **Lo de la izquierda que NO tiene par** |
| `rightanti` | Al revés |

`leftanti` es el operador de las detecciones de `forma: invariante`: "ticket de servicio sin ticket inicial previo" es literalmente un `leftanti` de `4769` contra `4768`. Ver [[Ticket de servicio sin ticket inicial previo]].

La tabla más chica va a la izquierda: KQL la carga en memoria.

## 6. Línea base

```kql
let base =
    DeviceNetworkEvents
    | where Timestamp between (ago(30d) .. ago(1d))
    | summarize vistos = dcount(RemoteUrl) by DeviceName;
DeviceNetworkEvents
| where Timestamp > ago(1d)
| summarize hoy = dcount(RemoteUrl) by DeviceName
| join kind=inner base on DeviceName
| where hoy > vistos * 3
```

Comparar contra el propio pasado en vez de contra un umbral fijo. Es lo que separa una regla portable de una que hay que calibrar por cliente — ver [[Sin línea base no hay anomalía]].

```kql
| summarize p95 = percentile(duracion, 95) by endpoint
```

## 7. Cosas que ahorran tiempo

```kql
let sospechosos = dynamic(["cmd.exe","powershell.exe","wscript.exe"]);
| where FileName has_any (sospechosos)

| where ProcessCommandLine matches regex @"(?i)-e(nc(odedcommand)?)?\s+[A-Za-z0-9+/=]{50,}"

| extend claro = base64_decode_tostring(tostring(split(ProcessCommandLine, " ")[-1]))

| extend h = hash_sha256(RemoteUrl)
| summarize by tostring(parse_json(AdditionalFields).LogonId)

| evaluate bag_unpack(parse_json(AdditionalFields))
```

`parse_json` sobre `AdditionalFields` es obligatorio en Defender: la mitad de los campos interesantes de `DeviceEvents` viven ahí adentro y no como columna.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `Unknown function` o columna inexistente | Consulta de Sentinel corriendo en Defender, o al revés. El esquema no es el mismo |
| La consulta tarda o corta por timeout | Falta un `where Timestamp` arriba de todo, o hay `contains` donde iba `has` |
| `join` devuelve menos de lo esperado | `kind=inner` descarta lo que no tiene par. Para eso está `leftouter` |
| `dcount` devuelve un número raro y bajo | Es aproximado. Pasar `dcount(x, 4)` |
| Un campo aparece siempre vacío | Está anidado en `AdditionalFields`. `parse_json` primero |
| `Query exceeds allowed result size` | Falta `summarize` o `take` |
| El regex no matchea nada | Falta `(?i)`, o falta el `@` que evita interpretar las barras |
| Comparación de cadenas que falla sin motivo | `==` es sensible a mayúsculas. Usar `=~` |

## Relacionadas

[[Detección por forma - matriz de referencia]] · [[Sigma - matriz de referencia]] · [[MOC - Fundamentos de detección]] · [[La detección vive en el agregado, no en el evento]]
