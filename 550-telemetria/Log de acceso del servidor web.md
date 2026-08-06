---
tipo: telemetria
plataforma: [linux, windows]
producto: nginx / Apache / IIS
identificador: "access.log"
por-defecto: true
coste: medio
visibilidad: publica
creado: 2026-08-05
aliases:
  - access.log
  - log de acceso HTTP
tags:
  - dominio/web
---

# Log de acceso del servidor web

## Qué lo genera

Cada petición HTTP atendida. Es de las poquísimas fuentes que **vienen activadas por defecto** en cualquier despliegue, lo que la vuelve el piso mínimo garantizado del lado web.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| Ruta y query string | La URL completa, con parámetros | El payload viaja entero acá si va por GET |
| Código de estado | 200, 500, 403 | Los 500 en ráfaga delatan pruebas de inyección |
| Bytes de respuesta | Tamaño | Un volcado exitoso se ve como una respuesta anormalmente grande |
| Tiempo de respuesta | Latencia | Solo si está configurado; es lo que delata el canal temporal |
| User-Agent y origen | Cliente | Correlación y agrupamiento |

## Coste de recolección

Medio: alto volumen en sitios con tráfico, pero cada línea es chica y comprime bien.

## Cómo se activa

Ya está. Lo que casi nunca está es **enviado al SIEM**, ni con el tiempo de respuesta incluido en el formato.

## Limitaciones

- **No ve el cuerpo de la petición.** Todo lo que viaje por POST es invisible acá: solo queda la ruta.
- No ve qué hizo la base de datos, solo qué pidió el cliente.
- Si hay un proxy o CDN adelante y no se propaga el origen real, la IP no sirve.

## Quién lo emite / quién lo consume

Rojo: [[SQLi - canal UNION]]
Azul: pendiente — ver [[Consultas del vault]] § Huecos defensivos propios
