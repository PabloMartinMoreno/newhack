---
tipo: meta
aliases:
  - xsltproc
  - nmap.xsl
  - XML a HTML
  - lynx
tags:
  - meta/referencia
  - dominio/red
---

# XML de escaneo a HTML

> [!info] Referencia pura, no un zettel
> Cómo se convierte la salida XML de un escaneo en algo que se lee. Sirve para [[nmap]] y para [[masscan]], que emite XML compatible — por eso vive acá y no adentro de la matriz de ninguna de las dos.

## 1. De XML a HTML

Nmap le mete al XML una instrucción `xml-stylesheet` que apunta a `nmap.xsl`. Con eso el informe sale de una línea, sin escribir plantilla:

```sh
xsltproc target.xml -o target.html
lynx target.html
```

Un solo argumento alcanza: xsltproc respeta la instrucción embebida en el propio documento.

| Situación | Comando |
|---|---|
| La hoja está donde el XML dice | `xsltproc target.xml -o target.html` |
| Apuntar a una hoja concreta | `xsltproc -o target.html /usr/share/nmap/nmap.xsl target.xml` |
| Leerlo en la terminal | `lynx target.html` |
| Volcarlo a texto plano | `lynx -dump -nolist target.html` |

## 2. Los dos modos de falla

**`-o` va antes de los posicionales** en la forma explícita. Si no, se lo lee como otro archivo de entrada:

```
$ xsltproc hoja.xsl target.xml -o salida.html
warning: failed to load external entity "-o"
unable to parse -o
```

**La ruta de la hoja viaja adentro del XML.** Si escaneás en una máquina y armás el informe en otra, `nmap.xsl` no existe del otro lado:

```
$ xsltproc target.xml -o target.html
warning: failed to load external entity "nmap.xsl"
xsltParseStylesheetProcess : document is not a stylesheet
$ echo $?
5
```

No falla en silencio, pero corta justo cuando estás cerrando el informe.

## 3. Se resuelve al escanear, no al convertir

| Flag de nmap | Qué deja en el XML |
|---|---|
| `--webxml` | La hoja pública: el HTML se arma en cualquier máquina |
| `--stylesheet ruta` | Una hoja propia, fija |
| `--no-stylesheet` | Ninguna: hay que pasarla a mano al convertir |

`--webxml` es el que conviene cuando el escaneo corre en una máquina comprometida o en un salto, que es casi siempre.

## 4. Por qué no hay entidades acá

`xsltproc` y `lynx` **no implementan ninguna técnica**: son utilitarios de propósito general, como `grep` o `awk`. La regla 6 pide una entidad para la herramienta que implementa técnicas —[[nmap]], [[masscan]]—, no para cada binario que aparece en un pipe.
