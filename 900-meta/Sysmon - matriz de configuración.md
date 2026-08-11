---
tipo: meta
aliases:
  - Sysmon
  - configuración de Sysmon
  - sysmonconfig
tags:
  - meta/referencia
  - plataforma/windows
---

# Sysmon - matriz de configuración

> [!info] Referencia pura, no un zettel
> Cómo se instala y se filtra. Qué ve cada evento y qué cuesta está en [[MOC - Telemetría de Windows]], una nota por identificador.

## 1. Instalar

`sysmon64.exe -accepteula -i sysmonconfig.xml`
`sysmon64.exe -c sysmonconfig.xml`
`sysmon64.exe -c`
`sysmon64.exe -u force`

`-i` instala, `-c` recarga la configuración sin reinstalar, `-c` sin argumento imprime la que está activa. Lo último es el primer comando de cualquier revisión: la configuración en disco y la cargada se separan sin avisar.

Los eventos salen a `Microsoft-Windows-Sysmon/Operational`.

`wevtutil gl Microsoft-Windows-Sysmon/Operational`
`wevtutil sl Microsoft-Windows-Sysmon/Operational /ms:1073741824`

El registro por defecto es chico. Sin subirlo, en un servidor ocupado la retención se mide en horas.

## 2. Los eventos, por relación valor/coste

| EID | Qué registra | Volumen | Nota |
|---|---|---|---|
| 1 | Creación de proceso | Alto | [[Sysmon EID 1 - ProcessCreate]] — el más valioso |
| 3 | Conexión de red | **Muy alto** | [[Sysmon EID 3 - NetworkConnect]] — hay que filtrar sí o sí |
| 7 | Carga de imagen | **Muy alto** | [[Sysmon EID 7 - ImageLoad]] — solo con inclusión explícita |
| 8 | Hilo remoto | Bajo | [[Sysmon EID 8 - CreateRemoteThread]] — barato y raro |
| 10 | Acceso a proceso | Medio | [[Sysmon EID 10 - ProcessAccess]] — la de LSASS |
| 11 | Creación de archivo | Alto | [[Sysmon EID 11 - FileCreate]] |
| 12/13/14 | Registro | Alto | [[Sysmon EID 13 - RegistryValueSet]] |
| 22 | Consulta DNS | **Muy alto** | [[Sysmon EID 22 - DnsQuery]] |
| 15 | Marca de zona en archivo descargado | Bajo | Qué vino de internet |
| 25 | Manipulación de proceso | Bajo | Hollowing y herpaderping |

Los tres marcados "muy alto" son los que hacen que Sysmon tenga fama de caro. Con inclusión en vez de exclusión, dejan de serlo.

## 3. Esqueleto de configuración

```xml
<Sysmon schemaversion="4.90">
  <HashAlgorithms>SHA256</HashAlgorithms>
  <EventFiltering>
    <RuleGroup name="proc" groupRelation="or">
      <ProcessCreate onmatch="exclude">
        <Image condition="is">C:\Windows\System32\SearchIndexer.exe</Image>
      </ProcessCreate>
    </RuleGroup>

    <RuleGroup name="lsass" groupRelation="or">
      <ProcessAccess onmatch="include">
        <TargetImage condition="image">lsass.exe</TargetImage>
      </ProcessAccess>
      <ProcessAccess onmatch="exclude">
        <SourceImage condition="is">C:\Windows\System32\wininit.exe</SourceImage>
      </ProcessAccess>
    </RuleGroup>

    <RuleGroup name="net" groupRelation="or">
      <NetworkConnect onmatch="include">
        <DestinationPort condition="is">4444</DestinationPort>
        <Image condition="image">powershell.exe</Image>
      </NetworkConnect>
    </RuleGroup>
  </EventFiltering>
</Sysmon>
```

> [!warning] `include` y `exclude` no son simétricos
> `onmatch="include"` registra **solo** lo que matchea; `onmatch="exclude"` registra todo menos eso. Para `ProcessCreate` se usa `exclude` porque se quiere todo. Para `NetworkConnect`, `ImageLoad` y `DnsQuery` se usa `include`, porque registrar todo es lo que llena el disco en una tarde. Invertirlos es el error de configuración más caro y no da ningún error: simplemente deja de haber datos, o deja de haber espacio.

Dentro de un mismo `onmatch`, los campos son **OR**. Para exigir dos condiciones a la vez hace falta `<Rule groupRelation="and">`:

```xml
<ProcessAccess onmatch="include">
  <Rule groupRelation="and">
    <TargetImage condition="image">lsass.exe</TargetImage>
    <GrantedAccess condition="is">0x1010</GrantedAccess>
  </Rule>
</ProcessAccess>
```

## 4. Condiciones

| `condition` | Qué hace |
|---|---|
| `is` / `is not` | Igualdad exacta |
| `contains` / `excludes` | Subcadena |
| `contains any` / `contains all` | Lista separada por `;` |
| `begin with` / `end with` | Prefijo, sufijo |
| `image` | Nombre del ejecutable, con o sin ruta. **El que casi siempre se quiere** |
| `is any` | Lista de valores exactos |
| `less than` / `more than` | Comparación léxica, no numérica |

`image` existe porque comparar rutas completas se rompe cuando el binario se copia a otro lado. `condition="image">lsass.exe` matchea igual en `C:\Windows\System32\lsass.exe` que en `C:\Temp\lsass.exe`.

## 5. `GrantedAccess` — los valores que importan

El campo del EID 10 que separa un volcado de LSASS de una consulta inocente.

| Valor | Qué pidió |
|---|---|
| `0x1010` | `VM_READ` + `QUERY_LIMITED` — lectura de memoria. **El volcado** |
| `0x1410` | Lo mismo más `QUERY_INFORMATION` — mimikatz clásico |
| `0x143a` | Acceso amplio, típico de herramientas de volcado |
| `0x1000` | Solo consulta. Ruido: lo hace medio Windows |
| `0x0400` | `QUERY_INFORMATION` sin lectura. Ruido |

Filtrar por `0x1000` y `0x0400` en un `exclude` deja el EID 10 utilizable. Sin eso, la fuente es inservible por volumen. Ver [[Acceso a LSASS desde proceso no firmado]].

Ofuscar el valor es trivial —se pide más acceso del necesario y el número cambia— así que la regla no debe anclar solo ahí: el par imagen de origen + firma es lo que sostiene la detección.

## 6. Configuraciones de referencia

| Base | Enfoque |
|---|---|
| SwiftOnSecurity `sysmon-config` | Exclusión amplia. Buena para empezar, ruidosa en servidores |
| Olaf Hartong `sysmon-modular` | Modular por técnica de ATT&CK, se arma con lo que hace falta |
| Configuración propia | Lo que termina pasando. Se parte de una de las dos y se recorta |

`sysmon-modular` es el que mejor encaja con este vault, porque se compone por técnica y eso es exactamente lo que hay en `500-tecnicas/`.

## 7. Verificar que llega

`Get-WinEvent -LogName Microsoft-Windows-Sysmon/Operational -MaxEvents 10`
`Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational'; ID=10} -MaxEvents 5`
`Get-WinEvent -LogName Microsoft-Windows-Sysmon/Operational | Group-Object Id -NoElement | Sort-Object Count -Descending`

Lo último da la distribución por identificador, que es el diagnóstico de volumen: si el `3` o el `22` se comen el 90%, falta filtro.

> [!danger] Confirmar el evento antes de escribir la regla
> Es el mismo error que documenta [[Replicación de directorio desde un origen no autorizado]] con la auditoría de AD: la fuente figura como habilitada, la regla se escribe, y el evento nunca se generó porque faltaba un segundo paso de configuración. Correr la técnica y **ver el evento** va antes que la lógica. Ver [[Ausencia de alertas no es ausencia de ataque]].

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El registro se llena en horas | EID 3, 7 o 22 en `exclude`. Pasarlos a `include` |
| Una regla no filtra nada | Campos dentro de un `onmatch` son OR. Hace falta `<Rule groupRelation="and">` |
| `Configuration file validation failed` | `schemaversion` distinta de la del binario. `sysmon64.exe -? config` la imprime |
| El EID 10 no aparece nunca | Falta la sección `ProcessAccess`, o `TargetImage` con ruta completa en vez de `condition="image"` |
| Se pierden eventos bajo carga | Registro chico. Subirlo con `wevtutil sl /ms:` |
| Sysmon instalado y sin eventos | El servicio está detenido, o el driver no cargó. `sc query sysmon64` |
| El nombre del ejecutable no matchea | Sysmon se puede instalar renombrado. El nombre del driver también cambia |

## Relacionadas

[[MOC - Telemetría de Windows]] · [[Sigma - matriz de referencia]] · [[KQL - matriz de referencia]] · [[Acceso a LSASS desde proceso no firmado]] · [[La fidelidad se paga en volumen]]
