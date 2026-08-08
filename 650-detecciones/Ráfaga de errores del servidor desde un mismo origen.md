---
tipo: deteccion
tecnicas: ["[[CWE-89 - SQL Injection]]", "[[CWE-611 - XML External Entity]]", "[[CWE-434 - Unrestricted File Upload]]"]
telemetria: ["[[Log de errores del servidor web]]", "[[Log de acceso del servidor web]]"]
forma: agregado
ventana: "5m"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - pico de 500
tags:
  - dominio/web
---

# Ráfaga de errores del servidor desde un mismo origen

## Qué detecta

Un aumento anómalo de errores del servidor atribuibles a un mismo origen en una ventana corta.

Es la detección que cubre la **fase de descubrimiento**, que es donde el atacante pasa la mayor parte del tiempo y donde casi todo lo que prueba falla. No identifica una técnica: identifica que alguien está probando cosas. Sirve igual para inyección basada en errores, para recorrido de rutas, para bypass de subida y para XXE.

Su forma es `agregado` porque un error aislado no significa nada: **la señal es la tasa**, y compararla contra la línea base de la aplicación es toda la regla.

## Lógica

Sigma no expresa bien esto; va en el lenguaje del SIEM.

```
errores
| where timestamp > ago(5m)
| summarize
    total = count(),
    rutas = dcount(uri_path),
    tipos = dcount(exception_type)
  by origen = client_ip
| where total > 20 and rutas > 3
```

Refuerzo de fidelidad, y es el que convierte esto en algo accionable: correlacionar con [[Log de acceso del servidor web]] y exigir que las peticiones sean al **mismo endpoint con el mismo parámetro variando**. Eso separa a un atacante de un cliente con un bug.

Refuerzo de altísima fidelidad, específico de [[XXE - canal por error]]: una excepción de parser XML que cita una ruta del sistema de archivos **con contenido de un archivo dentro del mensaje**. Eso no tiene falsos positivos.

## Falsos positivos conocidos

- **Un despliegue roto** genera exactamente este patrón. Es el falso positivo dominante, y se distingue porque afecta a **todos** los orígenes a la vez, no a uno.
- **Un cliente con un bug** reintentando en bucle contra un mismo endpoint.
- **Escáneres autorizados** y monitoreo sintético.
- **Aplicaciones con errores crónicos** por bugs conocidos, que elevan la línea base hasta enterrar la señal.

El umbral de la consulta es un punto de partida, no un valor: **hay que derivarlo de la línea base de cada aplicación**.

## Evasiones conocidas

- **Bajar el ritmo** por debajo del umbral. Es la evasión obvia y funciona: la ventana de cinco minutos define exactamente cuán lento hay que ir.
- **Distribuir el origen**, que anula el agrupamiento por IP. Se mitiga agrupando también por sesión o por huella de cliente.
- **Técnicas que no generan errores** — [[SQLi - canal booleano ciego]] y [[Control de acceso - IDOR]] devuelven `200` siempre.
- **Suprimir errores en producción**, que es una buena práctica y de paso ciega esta regla: los errores llegan al registro pero la aplicación devuelve `200` con una página genérica. La regla sigue funcionando si lee el registro y no el código de estado.

## Cómo se prueba

Disparadores: [[SQLi - canal basado en errores]] y [[XXE - canal por error]] en laboratorio.

**Un disparo no valida nada**, porque es forma `agregado`. Hace falta generar volumen y, sobre todo, tener la línea base de la aplicación sin ataque: sin ese número, el umbral es inventado.
