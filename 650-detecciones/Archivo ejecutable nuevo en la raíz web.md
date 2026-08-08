---
tipo: deteccion
tecnicas: ["[[CWE-434 - Unrestricted File Upload]]", "[[CWE-98 - File Inclusion]]", "[[CWE-78 - OS Command Injection]]"]
telemetria: ["[[Escritura de archivo en la raíz web]]"]
forma: evento
ventana: 
estado: idea
fidelidad: alta
logica: sigma
validada: 
aliases:
  - webshell en disco
tags:
  - dominio/web
---

# Archivo ejecutable nuevo en la raíz web

## Qué detecta

Creación de un archivo con extensión ejecutable por el servidor, dentro del directorio servido, por un proceso que no es el de despliegue.

Es la detección de **efecto** de media docena de técnicas que llegan por caminos distintos y terminan en el mismo lugar: [[Webshell]], [[File upload - bypass de validación]], [[LFI - de lectura a RCE]], [[SQLi - lectura de archivos en MySQL]] escribiendo con `INTO OUTFILE`, [[SSRF - gopher a servicio interno]] escribiendo vía Redis, [[Command injection - canal ciego]] dejando salida en disco.

Ninguna de esas comparte payload, firma ni vector. Todas comparten el efecto, y por eso una sola regla las cubre a las seis — que es exactamente el argumento de por qué las detecciones de efecto valen más que las de firma.

## Lógica

```yaml
detection:
  selection:
    EventType: 'filecreate'
    TargetFilename|startswith:
      - '/var/www/'
      - '/usr/share/nginx/html/'
      - 'C:\inetpub\wwwroot\'
    TargetFilename|endswith:
      - '.php'
      - '.phtml'
      - '.phar'
      - '.jsp'
      - '.jspx'
      - '.aspx'
      - '.ashx'
  filter_despliegue:
    Image|endswith:
      - '/git'
      - '/rsync'
      - '/dpkg'
      - '/composer'
  condition: selection and not filter_despliegue
```

Refuerzo de fidelidad casi perfecta, y no necesita lista de extensiones: **el proceso que escribe**. `mysqld`, `redis-server` o `postgres` creando cualquier archivo dentro de la raíz web no tiene un solo caso legítimo.

```yaml
  selection_proceso:
    TargetFilename|startswith: '/var/www/'
    Image|endswith:
      - '/mysqld'
      - '/redis-server'
      - '/postgres'
```

## Falsos positivos conocidos

- **Despliegues.** El falso positivo dominante y el más fácil de resolver: se excluye por proceso, no por ruta, y se complementa con una ventana de despliegue conocida.
- **Cachés compiladas** — plantillas y contenedores de inyección de dependencias que generan `.php` en tiempo de ejecución. Muy común en marcos de trabajo PHP, y obliga a excluir el directorio de caché concreto.
- **Actualizaciones de la aplicación** desde su propio panel, en gestores de contenido que se actualizan solos.
- **Directorios de subida legítimos** dentro de la raíz. Si además ejecutan, eso es un hallazgo de configuración antes que un falso positivo: ver [[MOC - File upload]].

## Evasiones conocidas

- **Escribir fuera de la raíz servida** y llegar por [[LFI - inclusión local]]. La regla no ve nada, y es la evasión natural para quien conozca el despliegue.
- **Extensión no listada** que igual ejecute por configuración del servidor — un `.php7` o un `AddHandler` sobre una extensión rara. Se mitiga alertando por **cualquier** archivo nuevo, con la lista blanca de extensiones inofensivas, que es la forma correcta y más ruidosa.
- **Sobrescribir un archivo existente** en vez de crear uno. [[File upload - sobrescritura por nombre]] hace exactamente eso, y una regla que solo vigile creaciones lo pierde entero.
- **Contenedor efímero**: el archivo y su registro desaparecen al reiniciar.
- **Ejecución sin tocar disco** — [[LFI - phar deserialization]] y los wrappers de memoria no escriben nada.

## Cómo se prueba

Disparadores: [[Webshell]] escrita por [[File upload - bypass de validación]], y también por [[Command injection - canal directo]]. Un disparo la valida, porque es forma `evento`.

Lo que un disparo no valida es la lista de exclusiones, que depende del marco de trabajo de cada aplicación — y en aplicaciones con caché compilada esa lista es el trabajo entero.
