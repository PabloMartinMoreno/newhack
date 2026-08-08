---
tipo: deteccion
tecnicas: ["[[CWE-89 - SQL Injection]]", "[[CWE-98 - File Inclusion]]", "[[CWE-79 - Cross-site Scripting]]"]
telemetria: ["[[Log de acceso del servidor web]]"]
forma: evento
ventana: 
estado: idea
fidelidad: baja
logica: sigma
validada: 
aliases:
  - firma de payload en la URL
tags:
  - dominio/web
---

# Payload de inyección en parámetros de la URL

## Qué detecta

Cadenas características de inyección en la ruta o la cadena de consulta de una petición HTTP.

> [!warning] Fidelidad baja, y a propósito
> Es la única detección de este vault construida sobre **firmas de contenido**, que es exactamente lo que el resto del vault evita. Está acá porque [[Log de acceso del servidor web]] es el artefacto que existe en todos lados y a veces es el único que hay.
>
> No se despliega para alertar: se despliega para **buscar hacia atrás**. Como regla de alerta genera ruido permanente; como consulta de caza sobre una ventana histórica, encuentra el reconocimiento previo a un compromiso ya confirmado.

## Lógica

```yaml
detection:
  selection:
    cs-uri-query|contains:
      - 'UNION SELECT'
      - 'extractvalue('
      - 'sleep('
      - 'benchmark('
      - '../../'
      - '%2e%2e%2f'
      - 'php://filter'
      - 'php://input'
      - 'data://text'
      - '/etc/passwd'
      - '/proc/self/'
      - '<script'
      - 'onerror='
      - 'javascript:'
      - '${IFS}'
      - ';id'
      - '|whoami'
      - 'gopher://'
      - '169.254.169.254'
  condition: selection
```

## Falsos positivos conocidos

Muchísimos, y ese es el punto:

- **Buscadores del propio sitio** — cualquier campo de búsqueda reflejado en la URL contiene texto arbitrario de usuarios.
- **Foros, documentación técnica y gestores de incidencias**, donde hablar de `UNION SELECT` es el contenido legítimo.
- **Escáneres de seguridad autorizados**, que generan miles de coincidencias por hora.
- **Escaneo de fondo de internet** — todo servidor público recibe payloads todo el día sin que eso signifique nada.

## Evasiones conocidas

Todas las de [[SQLi evasión - matriz de referencia]], [[Command injection evasión - matriz de referencia]] y [[XSS evasión - matriz de referencia]]. Es decir: **cualquiera que sepa lo que hace la evade sin esfuerzo** — codificación, comentarios intercalados, mayúsculas alternadas, división en variables.

Y la evasión que no requiere ningún conocimiento: **mandar el payload por POST**. El cuerpo no queda en este artefacto, así que la mitad del tráfico de ataque es invisible para esta regla por construcción.

Por eso las detecciones que valen del lado web son las de efecto —[[Intérprete de comandos como hijo del servidor web]], [[Petición al servicio de metadatos de instancia]]— y no las de firma. Esta regla existe para cuando no hay nada mejor.

## Cómo se prueba

Cualquier variante de los tres dominios enlazados la dispara. Lo que hay que medir no es si dispara sino **cuántas veces dispara sin ataque**: sin una semana de línea base, desplegarla como alerta es garantía de que se va a ignorar.
