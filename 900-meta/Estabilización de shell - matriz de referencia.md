---
tipo: meta
aliases:
  - Estabilizar shell - matriz
  - TTY upgrade
  - upgrade a TTY
  - Mejora de terminal
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Estabilización de shell - matriz de referencia

> [!info] Referencia pura, no un zettel
> Convertir una dumb shell en un TTY completo. Se usa después de cualquier reverse/bind de [[Reverse y bind shells - matriz de referencia]] — el dominio, en [[MOC - Shells]]. El porqué —qué se rompe sin TTY— está en [[Shell - conexión reversa]] § Cómo falla.

Sin TTY no andan `sudo`, `ssh`, `su`, ni nada a pantalla completa (`vim`, `less`, `top`), y un `Ctrl-C` mata la **sesión entera** en vez del comando. Por eso se estabiliza antes de trabajar en serio.

## Paso 1 — conseguir un PTY en el objetivo

| Método | Comando (en la shell remota) | Requiere | Nota |
|---|---|---|---|
| Python | `python3 -c 'import pty;pty.spawn("/bin/bash")'` | `python3` (o `python`) | El más habitual |
| script | `script -qc /bin/bash /dev/null` | `util-linux` (casi siempre) | Alternativa sin Python |
| socat | par de `socat` en ambos lados | `socat` en el objetivo | **Salta los pasos 2-3**: TTY completo de una |
| expect | `expect -c 'spawn /bin/bash;interact'` | `expect` | Raro, pero sirve de fallback |

Si la reversa se lanzó con el one-liner de **Python** o de **socat** de la otra matriz, ya tenés PTY: pasá directo al paso 3.

## Paso 2 — devolver la terminal cruda (lado atacante)
Con el PTY del paso 1 andando, en **tu** terminal (la del listener, no la remota):
```sh
# Ctrl-Z para suspender la shell remota
stty raw -echo; fg
# Enter, y queda la sesión en primer plano con el eco apagado
```
`stty raw -echo` pasa las teclas sin procesar (para que `Ctrl-C`, flechas y tab lleguen a la remota) y apaga el doble eco. Al salir de la sesión, recuperá tu terminal con `stty sane` o `reset`.

## Paso 3 — ajustar el entorno (shell remota)
```sh
export TERM=xterm-256color
export SHELL=/bin/bash
stty rows 50 cols 200
```
Los valores de `rows`/`cols` se sacan de `stty size` en **tu** terminal local. Sin esto, `vim` y `less` dibujan mal y las líneas largas se cortan.

## Atajo — todo en uno

| Herramienta | Cómo | Qué hace |
|---|---|---|
| pwncat-cs | `pwncat-cs -lp PUERTO` como listener | Estabiliza sola al recibir la sesión: PTY, `raw`, `rows`/`cols`, historial |
| socat | par `socat` (ver [[Reverse y bind shells - matriz de referencia]] § listeners) | TTY completo sin pasos 1-3 |


## Windows
Windows no tiene el modelo PTY de Unix, así que estos pasos no aplican. Para una consola interactiva de verdad: subir a **Meterpreter** ([[metasploit]]), usar **WinRM** (`evil-winrm`), o `ConPTY` (`ConPtyShell`). Una reversa de `cmd`/PowerShell cruda funciona para comandos sueltos pero no da línea editable ni maneja programas interactivos.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| Tras `fg` no se ve lo que tecleo | `-echo` funcionando (es lo esperado) | seguir; el eco lo da la remota |
| `vim`/`less` dibujan mal | `TERM` o `rows`/`cols` sin setear | rehacer el paso 3 |
| Mi terminal queda rota al salir | no se restauró | `stty sane` o `reset` |
| `stty: standard input: Inappropriate ioctl` | no hay PTY todavía | falta el paso 1 |

