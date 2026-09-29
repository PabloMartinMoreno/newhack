---
tipo: meta
aliases:
  - escalada con Python SUID
  - python privesc
  - cap_setuid python
  - Python setuid a root
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Python SUID y setuid capability - matriz de referencia

> [!info] Referencia pura, no un zettel
> Escalar a root cuando la enumeración ([[Enumeración de privesc Linux - matriz de referencia]]) encuentra un `python` **con bit SUID** o **con la capability `cap_setuid`**. Los dos casos usan el mismo payload; cambia sólo de dónde sale el privilegio. El catálogo general de binarios abusables, en [gtfobins.github.io](https://gtfobins.github.io); acá el foco es Python y el porqué.

`python3` en los ejemplos; con `python`/`python2` es idéntico salvo el nombre.

## Los dos orígenes del privilegio

| Origen | Cómo se ve en la enum | Cómo se abusa |
|---|---|---|
| Bit SUID (dueño root) | `find / -perm -4000 -type f 2>/dev/null` → `-rwsr-xr-x root ... python3` | correr el binario: arranca con **euid=0** |
| Capability `cap_setuid` | `getcap -r / 2>/dev/null` → `python3 = cap_setuid+ep` | el binario puede llamar a `setuid()` aunque **no** tenga bit SUID |

La capability es el caso **invisible**: no aparece en `find -perm -4000`, y sobrevive a un montaje `nosuid` que anularía el bit. Por eso `getcap` es un paso propio en la enumeración.

## El payload
```sh
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```
Sirve **igual** para SUID y para `cap_setuid`: en ambos Python puede llamar `setuid(0)`. Pone `ruid=euid=suid=0` y recién ahí abre la shell — que ya nace como root.

## Por qué `os.setuid(0)` y no sólo `os.system("/bin/bash")`
Es el error clásico y vale entenderlo:

- Un binario SUID arranca con **euid=0 (root) pero ruid=tu usuario**. No sos root del todo: tenés privilegio *efectivo*, no *real*.
- `bash`/`sh` modernos, al arrancar, **si detectan `euid ≠ ruid` sueltan el privilegio** (vuelven euid=ruid) por seguridad. Resultado: `os.system("/bin/bash")` a secas te da una shell de tu usuario, no de root.
- `os.setuid(0)` iguala los tres uids a 0 **antes** de lanzar la shell → cuando bash arranca no hay nada que soltar. Por eso el orden importa.

Alternativa equivalente: `os.system("/bin/bash -p")` — el `-p` le dice a bash que **no** suelte el privilegio, así que anda sin el `setuid(0)`. Pero `os.setuid(0)` es más limpio y no depende de la bandera.

## Variantes

| Situación | Payload |
|---|---|
| Estándar (SUID o cap) | `python3 -c 'import os;os.setuid(0);os.system("/bin/bash")'` |
| Mantener privilegio sin setuid | `python3 -c 'import os;os.system("/bin/bash -p")'` |
| Sin `os.system` disponible | `python3 -c 'import os;os.setuid(0);os.execl("/bin/bash","bash")'` |
| Reforzar todos los uids/gids | `python3 -c 'import os;os.setresuid(0,0,0);os.setresgid(0,0,0);os.system("/bin/bash")'` |

El mismo patrón en otros intérpretes privilegiados (misma enum, mismo GTFOBins):

| Intérprete | Payload |
|---|---|
| perl | `perl -e 'use POSIX qw(setuid);setuid(0);exec "/bin/bash";'` |
| ruby | `ruby -e 'Process::Sys.setuid(0);exec "/bin/bash"'` |


## Por qué un intérprete privilegiado es root seguro

Un binario SUID acotado (por ej. `passwd`) hace una cosa y no te deja salir. Un **intérprete** con el mismo privilegio ejecuta *código arbitrario* con ese privilegio: puede llamar `setuid(0)` y `exec` de una shell. Por eso `python`/`perl`/`ruby` con SUID o `cap_setuid` son escalada directa, mientras que la mayoría de los SUID legítimos no lo son. La enum marca el intérprete como el hallazgo de mayor valor por esto.

## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| La shell sigue siendo de mi usuario | falté el `os.setuid(0)`, bash soltó privilegio | agregar `os.setuid(0)` antes, o usar `-p` |
| `OperationNotPermitted` en `setuid` | el python **no** era SUID ni tenía `cap_setuid` | re-verificar con `find -perm -4000` y `getcap -r /` |
| `euid=0` pero `id` sigue mostrando tu uid | tenés euid root sin ruid | `os.setuid(0)` lo arregla |
| Es `python2`, no `python3` | mismo código | cambiar el nombre del binario nada más |
| Anda con `-p` pero no con `setuid(0)` | el binario tiene cap distinta (ej. sólo `cap_setuid` efectiva parcial) | usar `-p`, o `setresuid` |
