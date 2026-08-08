---
tipo: telemetria
plataforma: [linux, windows]
producto: auditd / monitor de integridad de archivos / EDR
identificador: "watch sobre el directorio servido"
por-defecto: false
coste: bajo
aliases:
  - FIM de la raíz web
  - archivo nuevo en webroot
tags:
  - dominio/web
---

# Escritura de archivo en la raíz web

## Qué lo genera

Creación o modificación de un archivo dentro del directorio que el servidor web sirve, por un proceso que no es el de despliegue.

Es el artefacto que convierte en visible un conjunto de técnicas que hoy solo dejan rastro indirecto: [[Webshell]], [[File upload - bypass de validación]], [[LFI - de lectura a RCE]], [[SQLi - lectura de archivos en MySQL]] escribiendo con `INTO OUTFILE`, [[SSRF - gopher a servicio interno]] escribiendo vía Redis, y [[Command injection - canal ciego]] dejando su salida en un `.txt` legible.

Todas esas terminan en lo mismo —**un archivo nuevo donde no debería haberlo**— y hasta ahora todas colgaban de [[Log de acceso del servidor web]], que solo ve la petición y no el efecto.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| Ruta creada | Dónde cayó | Dentro de la raíz servida es lo único que importa |
| Extensión | `.php`, `.jsp`, `.aspx` | **Ejecutable en ese servidor** es la condición de alta fidelidad |
| Proceso que escribió | `php-fpm`, `mysqld`, `redis-server` | Un motor de base escribiendo en la raíz web no tiene explicación |
| Usuario | `www-data`, `mysql` | Confirma la identidad del servidor |
| Marca de tiempo | Cuándo | Correlación con la petición que lo creó y con la primera lectura |
| Hash o tamaño | Qué se escribió | Triaje y comparación contra el despliegue conocido |

La fila del proceso es la que da la mejor detección del conjunto: **`mysqld` o `redis-server` creando un archivo en la raíz web** no tiene ningún caso legítimo.

## Coste de recolección

Bajo. Un directorio acotado, y la escritura ahí es rara fuera de los despliegues. Es de los artefactos con mejor relación entre coste y valor de todo el vault: barato de encender, difícil de evadir.

## Cómo se activa

- **Linux con auditd** — una regla de vigilancia sobre el directorio servido, filtrando por escritura. Dos líneas de configuración.
- **Monitor de integridad de archivos** — lo habitual en entornos con cumplimiento normativo; ya suele estar y nadie mira su salida.
- **`inotify`** para una solución propia y liviana.
- **EDR**, que ya lo recolecta.

## Limitaciones

- **Los despliegues generan ruido legítimo**, y mucho. Se domina excluyendo por proceso y por ventana de despliegue, no por ruta.
- **Aplicaciones que escriben en la raíz por diseño** — cachés, imágenes subidas, archivos generados. Frecuente, y obliga a excluir subdirectorios completos. Si el directorio de subidas está dentro de la raíz servida y además ejecuta, ese es un hallazgo antes que un problema de telemetría.
- **No ve la modificación de un archivo existente** si el monitor solo vigila creaciones. [[File upload - sobrescritura por nombre]] pisa archivos que ya estaban.
- **Fuera de la raíz no ve nada** — una webshell escrita en otro directorio incluible por [[LFI - inclusión local]] queda afuera.
- **En contenedores efímeros** el archivo desaparece al reiniciar, junto con la evidencia.

## Quién lo emite / quién lo consume

Rojo: [[Webshell]] · [[File upload - bypass de validación]] · [[File upload + LFI]] · [[File upload - sobrescritura por nombre]] · [[LFI - de lectura a RCE]] · [[SQLi - lectura de archivos en MySQL]] · [[SSRF - gopher a servicio interno]] · [[Command injection - canal ciego]] · [[Argument injection - abuso de flags]]
Azul: [[Archivo creado y solicitado a los segundos]] · [[Archivo ejecutable nuevo en la raíz web]]
