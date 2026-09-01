---
tipo: meta
aliases:
  - Nombres
  - Naming
tags:
  - meta/convenciones
---

# Convenciones de nombres

El nombre de archivo es el identificador del enlace. Cambiarlo después cuesta; elegirlo bien la primera vez es gratis.

## Patrones por carpeta

| Carpeta | Patrón | Ejemplo |
|---|---|---|
| `050-teoria/` | `<sistema> - <pieza>` | `HTTP - delimitación del cuerpo` |
| `100-notas/` | Frase declarativa, no sustantivo suelto | `La latencia como canal de datos` |
| `200-fuentes/` | `@` + slug del origen | `@portswigger-sqli-labs` |
| `300-mapas/` | `MOC - <dominio>` | `MOC - SQL injection` |
| `400-entidades/` | Nombre propio de la entidad | `sqlmap`, `APT29`, `Cobalt Strike` |
| `450-superficies/` | Nombre del producto/tecnología | `Active Directory`, `Entra ID` |
| `500-tecnicas/` | `<ID> - <nombre>` | `T1003.001 - LSASS Memory`, `CWE-89 - SQL Injection` |
| `550-telemetria/` | `<producto> <id> - <nombre>` | `Sysmon EID 10 - ProcessAccess` |
| `600-tradecraft/` | `<clase> - <variante>` | `SQLi - canal temporal ciego` |
| `650-detecciones/` | Frase que describe lo observado | `Acceso a LSASS desde proceso no firmado` |
| `700-procedimientos/` | Sustantivo de acción | `Validación de tradecraft en laboratorio` |
| `750-hallazgos/` | Título tal como iría en el informe | `Inyección SQL en parámetro de búsqueda` |
| `900-meta/` | Descriptivo. Matrices: `<tema> - matriz de referencia` | `Dialectos SQL - matriz de referencia` |
| `999-plantillas/` | `Plantilla - <tipo>` | `Plantilla - tradecraft` |

## Idioma: la regla del corpus externo

> [!important] El criterio no es "español o inglés"
> **Si el término aparece literal en una fuente que vas a volver a leer** — ATT&CK, CWE, WSTG, docs de vendor, reglas Sigma, writeups — **va en inglés. Si el término lo escribiste vos, va en español.**

Traducir un término de la industria crea una cadena que no existe en ningún corpus: no se puede grepear contra una fuente, no la busca un alumno, no aparece en un informe de vendor. "Vaciado de proceso" no lo escribió nadie nunca. Al revés también: escribir en inglés lo que es tuyo no compra nada, porque no hay nada externo con lo que alinearlo.

| Capa | Idioma | Ejemplo |
|---|---|---|
| IDs canónicos | Inglés, intocable | `T1003.001`, `CWE-89`, `WSTG-INPV-05`, `EID 10` |
| Nombres propios de la industria | **Inglés** | Kerberoasting, process hollowing, pass-the-hash, DCSync, golden ticket, slow query log |
| Herramientas y productos | Inglés | `sqlmap`, `Sysmon`, `Active Directory` |
| Descripciones y conceptos propios | **Español** | `Acceso a LSASS desde proceso no firmado`, `La latencia como canal de datos` |
| Cuerpo de nota y secciones | Español | — |
| Estructura: carpetas, claves, valores de enum | Español | `opsec: quemado`, `estado: produccion` |

Casos límite resueltos:

- **`500-tecnicas/` usa el nombre oficial en inglés, sin excepción.** Esa carpeta existe solo para ser el ancla compartida con ATT&CK y CWE; si el nombre no coincide con el oficial, deja de ser ancla. El nombre en español va de alias.
- **`600-tradecraft/` va en español cuando el nombre describe tu descomposición por ejes.** `SQLi - canal temporal ciego` es tuyo — PortSwigger no lo llama así. Su alias `time-based blind` cubre la búsqueda.
- **La estructura es la capa reversible**: cambiar `opsec` por `burn_state` es un `sed`. Cambiar nombres de archivo mueve identificadores de enlace. Por eso la estructura se decide una vez y no se revisa.

### Los aliases son la costura

**Título en el idioma en que pensás, alias en el idioma en que buscás.** Cuesta una línea de frontmatter y elimina el conflicto: `[[time-based blind]]` resuelve a `SQLi - canal temporal ciego`. Obsidian, `obsidian.nvim` y [[Consultas del vault]] resuelven los tres por alias.

Con una salvedad de implementación: el `quick_switch` que trae `obsidian.nvim` es un picker de archivos y **no** lee frontmatter, así que por sí solo no encuentra por alias. Por eso `<leader>oq` no lo usa — ver [[Recorrido del vault en nvim]].

Toda nota cuyo título esté en un idioma **debe** llevar el término del otro idioma como alias, siempre que ese término exista.

## Reglas

- **Prefijo de clase en tradecraft.** `SQLi - canal temporal ciego`, no `Canal temporal ciego`. Agrupa alfabéticamente y desambigua el autocompletado.
- **Prefijo de sistema en teoría**, por la misma razón. El sistema va en inglés porque es de corpus externo (`HTTP`, `TLS`, `Kerberos`); la pieza en español porque es tu descomposición. Los nombres de campo y de cabecera se escriben con su capitalización oficial dentro del cuerpo: `Transfer-Encoding`, no `transfer encoding`. La distinción con `100-notas/` es de género: la teoría **describe un sistema externo**, el zettel **afirma un principio propio**. Si el título es una frase declarativa que podrías defender vos, es zettel.
- **Un alias, una nota dueña.** Ningún alias puede vivir en dos notas: Obsidian resuelve `[[alias]]` arbitrariamente y los links se rompen en silencio. Dueña = la nota cuyo nombre **es** esa cosa.
- **Aliases obligatorios** donde el nombre canónico no es el que se escribe al enlazar: en `T1003.001 - LSASS Memory` van `T1003.001` y `Volcado de memoria de LSASS`.
- **Tildes en nombres de archivo**: sin problema en Linux y con `rg`. El único escenario que las rompe es sincronizar a macOS, que normaliza Unicode distinto y duplica archivos. Si eso nunca entra en juego, no son un tema.
- **Enlaces por wikilink**, siempre. Obsidian sigue los renombres. Markdown link solo para URLs externas.
- **Referencias a bloques por `^block-id`**, no por `#Heading` — los `^id` sobreviven al renombre del título, los headings no.

## Tags

Los tags no reemplazan carpetas ni frontmatter. Se usan solo para cortes transversales que el `tipo:` no captura:

```
#cert/oscp  #cert/crto  #clase/modulo-ad  #lab/pendiente  #dominio/cloud
```

Nada de `#red` / `#blue`: eso ya lo dice el `tipo:`.

## Relacionadas

[[Estructura del vault]] · [[Esquema de frontmatter]]
