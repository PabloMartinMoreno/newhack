---
tipo: deteccion
tecnicas: ["[[CWE-78 - OS Command Injection]]"]
telemetria: ["[[Proceso hijo del servidor web]]"]
forma: evento
ventana: 
estado: idea
fidelidad: alta
logica: sigma
validada: 
aliases:
  - shell hija de php-fpm
tags:
  - dominio/web
---

# Intérprete de comandos como hijo del servidor web

## Qué detecta

Creación de un proceso intérprete —`sh`, `bash`, `powershell`, `cmd`— cuyo padre o ancestro es el servidor web o el intérprete de la aplicación.

Detecta **la relación padre-hijo**, no el comando. Esa es la razón de anclar en el par imagen/padre y no en el contenido de la línea de comandos: la evasión de [[Command injection evasión - matriz de referencia]] destroza cualquier firma sobre el texto del comando y no puede evitar que el proceso nazca.

Es la detección de mayor fidelidad del lado web. Un servidor de aplicación no tiene ninguna razón legítima para ser padre de una shell en medio de una petición de usuario.

## Lógica

```yaml
detection:
  selection:
    ParentImage|endswith:
      - '/php-fpm'
      - '/httpd'
      - '/nginx'
      - '/apache2'
      - '\w3wp.exe'
    Image|endswith:
      - '/sh'
      - '/bash'
      - '/dash'
      - '\cmd.exe'
      - '\powershell.exe'
  condition: selection
```

Refuerzo de fidelidad, para separar ejecución de despliegue: exigir que el proceso viva menos que el tiempo de espera de la petición, o que la línea de comandos contenga redirección a descriptor de red — que es la firma de [[Command injection - a shell interactiva]].

## Falsos positivos conocidos

- **Scripts de despliegue y de mantenimiento** que corren bajo el mismo usuario del servidor. Se separan por ancestro: los de despliegue cuelgan de `cron` o de un agente, no de una petición.
- **Aplicaciones que invocan binarios por diseño** — conversión de imágenes, generación de PDF, `git`. Estas invocan el binario **sin shell** cuando están bien escritas; cuando usan shell, generan ruido permanente y hay que excluirlas por línea de comandos concreta.
- **Herramientas de monitoreo** que ejecutan comprobaciones desde el contexto del servidor.

La exclusión es específica de cada aplicación. La regla no es portable tal cual.

## Evasiones conocidas

- **[[Argument injection - abuso de flags]]** — la evade por completo y por diseño. No hay shell: el servidor invoca exactamente el binario que siempre invoca. Es el punto ciego declarado de [[Proceso hijo del servidor web]] y no se cierra con esta regla.
- **Ejecución sin proceso** — `eval` de PHP, SSTI y deserialización se resuelven dentro del intérprete y no crean nada.
- **Reutilización de una shell ya existente**, si el atacante logró persistencia previa.

## Cómo se prueba

Disparador de referencia: [[Command injection - canal directo]] contra una aplicación de laboratorio. Un solo disparo la valida, porque es forma `evento`.

Lo que un disparo **no** valida es la lista de exclusiones, que necesita una semana de línea base de la aplicación real.
