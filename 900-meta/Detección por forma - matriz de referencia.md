---
tipo: meta
aliases:
  - Forma de detección
  - evento correlacion agregado invariante
tags:
  - meta/referencia
---

# Detección por forma - matriz de referencia

> [!info] Referencia pura, no un zettel
> `forma:` es el campo propio del vault. Acá está la traducción de cada valor a una consulta concreta. El concepto está en [[La detección vive en el agregado, no en el evento]]; la sintaxis suelta, en [[KQL - matriz de referencia]] y [[Sigma - matriz de referencia]].

## 0. Las cuatro, de un vistazo

| `forma:` | Qué evalúa | Necesita `ventana:` | Sigma | Cuántas hay |
|---|---|---|---|---|
| `evento` | Un registro en aislamiento | No | Sí, nativo | 7 |
| `correlacion` | Dos o más registros que hay que unir | No | Sí, `temporal` | 3 |
| `agregado` | Una función sobre una ventana | **Sí** | Sí, `event_count` / `value_count` | 10 |
| `invariante` | Una condición que no debería violarse nunca | **Sí** | **No** | 3 |

El campo no es taxonomía: cambia el lenguaje que alcanza, cambia el coste de ejecución y **cambia cómo se valida**. Un disparo único valida una regla de `evento` y no dice absolutamente nada de una de `agregado`, que necesita volumen y línea base.

## 1. `evento`

Un solo registro contiene toda la evidencia. Es la forma más barata: sin estado, sin ventana, evaluable en el momento en que el evento llega.

```kql
DeviceProcessEvents
| where InitiatingProcessFileName in~ ("w3wp.exe","php-fpm","nginx")
| where FileName in~ ("cmd.exe","powershell.exe","sh","bash")
```

```yaml
detection:
  selection:
    ParentImage|endswith: ['/php-fpm', '\w3wp.exe']
    Image|endswith: ['/sh', '\cmd.exe']
  condition: selection
```

Rinde cuando la condición **no tiene explicación legítima**: un servidor de aplicación no es padre de una shell, un TGT sin preautenticación no lo pide nadie por accidente. Ver [[Intérprete de comandos como hijo del servidor web]] y [[Solicitud de TGT sin preautenticación]].

No rinde cuando la condición es común y lo raro es la cantidad. Ahí la forma correcta es `agregado`, y forzarla a `evento` produce una regla que alerta doscientas veces por día.

## 2. `correlacion`

La evidencia está repartida en dos fuentes o dos eventos, y ninguno solo es sospechoso. La escritura de un archivo es normal; que se pida por HTTP tres segundos después, no.

```kql
let escritura =
    DeviceFileEvents
    | where Timestamp > ago(1d)
    | where FolderPath has "wwwroot" and FileName endswith ".aspx"
    | project DeviceName, FileName, tEscritura = Timestamp;
W3CIISLog
| where TimeGenerated > ago(1d)
| join kind=inner escritura on $left.Computer == $right.DeviceName
| where csUriStem has FileName
| where TimeGenerated between (tEscritura .. tEscritura + 5m)
```

```yaml
correlation:
  type: temporal
  rules: [escritura_en_raiz_web, peticion_al_archivo]
  group-by: [Computer]
  timespan: 5m
```

El `between` sobre la diferencia de tiempos es lo que hace la regla: sin él, el `join` casa la escritura de hace un mes con la petición de hoy. Ver [[Archivo creado y solicitado a los segundos]].

`temporal_ordered` en Sigma agrega que el orden importe, que en este caso importa: la petición después de la escritura es un webshell, al revés es un `404`.

## 3. `agregado`

La señal es una función sobre una ventana: tasa, cardinalidad o proporción. Ningún evento suelto significa nada.

```kql
DeviceLogonEvents
| where Timestamp > ago(1h)
| summarize
    intentos = count(),
    cuentas  = dcount(AccountName),
    exitos   = countif(ActionType == "LogonSuccess")
  by RemoteIP, bin(Timestamp, 5m)
| where cuentas > 20 and exitos <= 2
```

```yaml
correlation:
  type: value_count
  rules: [fallo_de_login]
  group-by: [SourceIp]
  timespan: 5m
  condition:
    field: TargetUserName
    gte: 20
```

| Qué se mide | Función | Detección del vault |
|---|---|---|
| Tasa — cuántos por minuto | `count()` | [[Ráfaga de errores del servidor desde un mismo origen]] |
| Cardinalidad — cuántos distintos | `dcount()` | [[Barrido de puertos internos desde el servidor de aplicación]] |
| Proporción — qué fracción cumple | `countif() / count()` | [[Fallos de acceso contra cuentas inexistentes]] |
| Distribución — dos modas donde hay una | `percentile()` | [[Latencia bimodal en un endpoint]] |

`ventana:` es obligatorio y no es un detalle de implementación: **la misma regla con ventana de un minuto o de una hora detecta cosas distintas**. Un spraying lento pasa por debajo de una ventana corta, y una ventana larga sepulta la ráfaga en el ruido del día.

> [!warning] Un agregado no se valida con un disparo
> Correr la técnica una vez produce un evento, y un evento no cruza ningún umbral. Validar una regla de `agregado` exige generar volumen **y** tener línea base con la que comparar. Es el trabajo caro de [[Validación de tradecraft en laboratorio]], y la razón por la que las diez del vault siguen en `estado: idea`.

## 4. `invariante`

Una condición que el sistema no debería violar nunca. No se busca lo malo: se comprueba que lo que tiene que valer, vale.

```kql
let inicios =
    SecurityEvent
    | where EventID == 4768
    | project Cuenta = TargetUserName, tTGT = TimeGenerated;
SecurityEvent
| where EventID == 4769
| join kind=leftanti inicios on $left.TargetUserName == $right.Cuenta
```

`leftanti` es el operador de esta forma: devuelve lo de la izquierda **que no tiene par**. Un ticket de servicio sin TGT previo no es una anomalía estadística, es una imposibilidad — salvo que el TGT esté forjado. Ver [[Ticket de servicio sin ticket inicial previo]].

Otros dos invariantes del vault, con la misma estructura:

- Ninguna sesión activa después del evento que la cierra — [[Actividad de sesión posterior a su cierre]].
- Ningún cambio de privilegio fuera del flujo administrativo — [[Cambio de privilegio fuera del flujo administrativo]].

`ventana:` acá no es un tiempo: es el **alcance sobre el que el invariante tiene que valer**. En el vault son `por sesión`, `por objeto` y `por sesión de ticket`. Fuera de ese alcance la comparación no significa nada.

**Sigma no expresa esta forma.** No hay `type` de correlación que diga "esto no debería existir sin aquello". Es la razón concreta por la que `logica:` es un campo por detección y no una constante del vault.

## 5. Cómo elegir la forma

Tres preguntas, en orden:

1. **¿Un solo registro alcanza para decidir?** → `evento`. Es la más barata; si alcanza, no hay nada que discutir.
2. **¿Lo que importa es que dos cosas pasen juntas?** → `correlacion`.
3. **¿Lo raro es cuánto, no qué?** → `agregado`, y hay que fijar `ventana:`.
4. Si ninguna cierra, probablemente lo que se quiere comprobar es que algo **nunca** pase → `invariante`.

El error caro es empezar por 3 cuando alcanzaba 1: un agregado cuesta estado, ventana, línea base y calibración por cliente. El otro error, más silencioso, es escribir `evento` sobre una condición común y aceptar que la regla alerte todo el día — ver [[La fidelidad se paga en volumen]].

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| La regla alerta cientos de veces por día | Es `evento` y debería ser `agregado` |
| La regla no alerta nunca en laboratorio | Es `agregado` y la probaste con un disparo. Necesita volumen |
| El `join` casa eventos de días distintos | Falta acotar la diferencia de tiempo, no solo la ventana de consulta |
| Sigma no traduce la regla | Si es `invariante`, no hay forma. Reescribir en KQL |
| `higiene` marca `forma=agregado sin ventana` | Falta el campo. No es opcional: sin él la regla no está especificada |
| El umbral funciona en un cliente y no en otro | Umbral absoluto donde hacía falta línea base. Ver [[Sin línea base no hay anomalía]] |

## Relacionadas

[[MOC - Fundamentos de detección]] · [[KQL - matriz de referencia]] · [[Sigma - matriz de referencia]] · [[La detección vive en el agregado, no en el evento]] · [[Esquema de frontmatter]]
