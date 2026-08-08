---
tipo: tecnica
taxonomia: cwe
identificador: CWE-502
wstg: WSTG-INPV-11
tacticas: []
aliases:
  - CWE-502
  - Deserialización insegura
  - insecure deserialization
tags:
  - dominio/web
---

# CWE-502 - Deserialization of Untrusted Data

> [!note] Nota paraguas
> Sin contenido operativo. La única variante escrita hoy es [[LFI - phar deserialization]], que llega acá por el vector de [[MOC - File inclusion]]. **El dominio propio todavía no está modelado** — ver [[Avances]] § Pendientes.

## Qué es

La aplicación reconstruye un objeto a partir de datos que controla el atacante. Reconstruir no es leer: el proceso de deserialización **ejecuta código** de la propia aplicación —constructores, destructores, ganchos del ciclo de vida— y lo hace con los valores que el atacante eligió.

## Por qué es distinta del resto de las inyecciones

En SQLi o en command injection el atacante aporta el código que se ejecuta. Acá no aporta nada: **el código ya está en la aplicación**. Lo que aporta es un estado que hace que ese código, ejecutado en el orden correcto, haga algo que nadie quiso.

De ahí la noción de cadena de gadgets: una secuencia de métodos que existen por razones legítimas y que encadenados alcanzan una primitiva peligrosa. Por eso la explotación depende tanto de qué bibliotecas están cargadas, y por eso una aplicación puede ser vulnerable hoy y no serlo mañana sin que su código cambie — alcanza con que una dependencia agregue o quite una clase.

## Por qué la mitigación no es validar

Filtrar el dato serializado no funciona: para saber si es peligroso hay que interpretarlo, y interpretarlo es el ataque. Firmar el dato ayuda contra la manipulación pero no contra un atacante que consiga la clave, y no cambia que el formato sea ejecutable por diseño.

La mitigación real es **no deserializar datos no confiables**. Cuando hace falta transportar estructuras, se usa un formato de datos puro —JSON, con esquema— que no reconstruye objetos ni invoca métodos.

## Cómo llega el dato

El vector rara vez es obvio, y esa es la dificultad del dominio. Cookies, campos ocultos, parámetros, cabeceras, mensajes en colas, cachés, y —el caso de [[LFI - phar deserialization]]— **operaciones de sistema de archivos**, donde ninguna función que se llame "deserializar" aparece en el código.

Ese último caso es el que hace a esta CWE relevante para el dominio de file inclusion: cualquier operación sobre una ruta controlada puede disparar deserialización sin que haya una sola llamada explícita.

## Referencias canónicas

- [CWE-502](https://cwe.mitre.org/data/definitions/502.html)
- WSTG-INPV-11
- OWASP Top 10 — A08 Software and Data Integrity Failures
