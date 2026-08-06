---
tipo: meta
visibilidad: publica
creado: 2026-08-05
aliases:
  - Frontmatter
  - Propiedades
tags:
  - meta/esquema
---

# Esquema de frontmatter

Un solo esquema para todo el vault. La fusión rojo/azul depende de que **ambos lados apunten a los mismos destinos con el mismo nombre de campo**.

> [!important] Campo unificado
> El campo se llama `telemetria:` en los dos lados. No `huella:` en rojo y `fuentes-log:` en azul. Simplifica toda consulta que se escriba después.

## Campos comunes a toda nota

```yaml
tipo:          # zettel | tradecraft | deteccion | telemetria | tecnica
               # superficie | entidad | fuente | hallazgo | moc | procedimiento | meta
visibilidad:   # publica | privada
creado:        # YYYY-MM-DD
aliases: []
tags: []
```

### `visibilidad:` desde el día uno

Un grafo con tradecraft anotado por estado de OPSEC y cobertura de EDR es **inteligencia sobre vos**. Si alguna vez se publica una versión para alumnos, esto ya está separado. Es mucho más barato poner el campo ahora que auditar 400 notas después.

- `privada` por defecto en `600-tradecraft/`, `650-detecciones/` y `750-hallazgos/`.
- `publica` para zettels conceptuales, técnicas, telemetría y MOCs.

## Por tipo

### `tradecraft` — lado rojo

```yaml
---
tipo: tradecraft
clase: "[[T1055.012 - Process Hollowing]]"   # técnica o CWE: bisagra taxonómica
eje: canal-de-extraccion                     # solo si la clase se descompone en ejes
implementacion: "Process hollowing vía NtUnmapViewOfSection"
opsec: quemado                               # limpio | ruidoso | requiere-bypass | quemado
telemetria: ["[[Sysmon EID 8 - CreateRemoteThread]]"]
requisitos: [admin-local]
coste: medio                                 # bajo | medio | alto
alternativas: ["[[SQLi - canal fuera de banda]]"]
probado: 2026-02-14
contexto: [win11-defender, win2019-crowdstrike]
visibilidad: privada
---
```

`opsec`, `probado` y `contexto` son **innegociables**. Sin ellos el vault acumula técnicas muertas con apariencia de vigentes.

Cuerpo: cuatro secciones fijas — **Cuándo lo elijo · Por qué funciona · Cómo falla · Coste**. Ninguna contiene sintaxis; la sintaxis vive en las matrices de referencia.

### `deteccion` — lado azul

```yaml
---
tipo: deteccion
tecnicas: ["[[T1003.001 - LSASS Memory]]"]
telemetria: ["[[Sysmon EID 10 - ProcessAccess]]"]
estado: produccion            # idea | borrador | produccion | retirada
fidelidad: media              # alta | media | baja
logica: sigma                 # sigma | kql | spl | eql | yara | suricata
validada: 2026-06-02
visibilidad: privada
---
```

Cuerpo: **Qué detecta · Lógica · Falsos positivos conocidos · Evasiones conocidas · Cómo se prueba**.

### `telemetria` — la bisagra operativa

```yaml
---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 10"
por-defecto: false            # ¿viene activado sin configurar nada?
coste: alto                   # volumen/ingesta: bajo | medio | alto
visibilidad: publica
---
```

Cuerpo: **Qué lo genera · Campos relevantes · Coste de recolección · Cómo se activa · Limitaciones**.

### `tecnica` — la bisagra taxonómica

```yaml
---
tipo: tecnica
taxonomia: attack             # attack | cwe | wstg | capec
identificador: T1003.001
tacticas: [credential-access]
visibilidad: publica
---
```

Nota paraguas: qué es, por qué existe, a qué apunta. **Sin contenido operativo** — eso vive en tradecraft.

> [!tip] Web usa CWE + WSTG, no ATT&CK
> Para web, ATT&CK es demasiado grueso: todo SQLi cae en `T1190` y no sirve de nada. El identificador canónico es **CWE-89 + WSTG** (`WSTG-INPV-05`). Misma lógica que ATT&CK en infra: no inventar taxonomía propia si ya existe una compartida.

### `hallazgo` — biblioteca de informes

```yaml
---
tipo: hallazgo
severidad: alta               # critica | alta | media | baja | informativa
cvss: 8.8
vector-cvss: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
clase: "[[CWE-89 - SQL Injection]]"
esfuerzo-remediacion: medio   # bajo | medio | alto
visibilidad: privada
---
```

Cuerpo: **Descripción · Impacto · Evidencia (genérica, sin datos de cliente) · Remediación · Referencias**. El informe se arma enlazando, no reescribiendo. Cada finding se pule entre iteraciones en vez de reescribirse apurado a las dos de la mañana.

### `zettel`, `moc`, `superficie`, `entidad`, `fuente`, `procedimiento`

```yaml
tipo: zettel
relacionadas: ["[[...]]"]

tipo: moc
dominio: web

tipo: superficie
plataforma: [windows]
tecnicas: ["[[...]]"]

tipo: entidad
clase-entidad: herramienta    # herramienta | actor | malware
tecnicas: ["[[...]]"]

tipo: fuente
autor: ""
url: ""
formato: writeup              # paper | writeup | charla | repo | curso | libro
leido: 2026-08-05

tipo: procedimiento
fase: post-explotacion
```

## Tabla de equivalencias rojo ↔ azul

| Tradecraft | Detección | Destino compartido |
|---|---|---|
| `clase: "[[T1003.001]]"` | `tecnicas: ["[[T1003.001]]"]` | `500-tecnicas/` |
| `telemetria: ["[[Sysmon EID 10]]"]` | `telemetria: ["[[Sysmon EID 10]]"]` | `550-telemetria/` |
| `opsec: quemado` | `estado: produccion` | — |
| `probado: 2026-06-02` | `validada: 2026-06-02` | — |

## Relacionadas

[[Estructura del vault]] · [[Convenciones de nombres]] · [[Consultas del vault]]
