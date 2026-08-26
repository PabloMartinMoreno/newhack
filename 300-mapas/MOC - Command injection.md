---
tipo: moc
dominio: web
aliases:
  - MOC command injection
  - Command injection
tags:
  - dominio/web
---

# MOC - Command injection

> [!abstract] Nota de referencia paraguas
> Las definiciones viven en [[CWE-78 - OS Command Injection]] y [[CWE-88 - Argument Injection]]. La sintaxis por shell, en [[Command injection shells - matriz de referencia]]. Acá vive **la decisión**.

Dos CWE en un MOC. No por parecido temático sino porque **la misma pregunta las separa**: si hay shell de por medio es CWE-78, si no la hay es CWE-88. Esa pregunta es el nodo raíz del árbol, no un detalle de implementación, y por eso las dos ramas comparten mapa.

| Eje | Valores |
|---|---|
| Canal de extracción | directo · ciego · temporal · fuera de banda |
| Ruptura del contexto | separador · sustitución · newline · escape de comillas · **sin ruptura** |
| Shell | `sh`/`bash` · `cmd` · PowerShell · **sin shell** |
| Obstáculo | espacios · barras · palabras clave · lista blanca · WAF |
| Impacto | lectura · shell interactiva · webshell · pivote |

## Árbol de decisión — el nodo raíz

```
¿Los metacaracteres hacen algo?
├─ Sí → hay shell: CWE-78, seguir al árbol de canales
└─ No
   ├─ ¿El argumento llega intacto al binario?
   │  └─ Sí → CWE-88: [[Argument injection - abuso de flags]]
   └─ No → no hay superficie por acá
```

Este es el orden correcto y se invierte todo el tiempo. Probar los separadores es barato y da la respuesta de una: si los metacaracteres aparecen literales en un error, no hace falta insistir con evasiones — hay que cambiar de CWE.

## Árbol de decisión — elegir canal

```
¿La salida del comando vuelve en la respuesta?
├─ Sí                          → [[Command injection - canal directo]]
└─ No — ¿probaste 2>&1?
   ├─ Ahora sí                 → [[Command injection - canal directo]]
   └─ Sigue sin volver
      ├─ ¿Hay egress de red?   → [[Command injection - canal fuera de banda]]
      └─ No
         ├─ ¿Hay dónde escribir en la raíz web? → [[Command injection - canal ciego]]
         └─ No                                  → [[Command injection - canal temporal]]
```

Igual que en [[MOC - SQL injection]], el orden es de **coste creciente**. Dos diferencias respecto de SQLi que cambian la práctica:

**`2>&1` es un nodo del árbol, no un truco.** Muchísimas apps imprimen `stdout` y descartan `stderr`; el comando corre y parece no haber corrido. Redirigir mueve el caso de "ciego" a "directo" sin cambiar nada más, y es lo más barato del árbol entero.

**El temporal queda último, y a veces miente.** Si la ejecución es asíncrona, no hay retardo que medir aunque haya ejecución. Ante un `sleep` que no funciona, hay que probar fuera de banda antes de descartar la vulnerabilidad — ver [[Command injection ciego - matriz de referencia]] § 1.

## Árbol de decisión — obstáculos

Las primitivas se combinan; todas viven en [[Command injection evasión - matriz de referencia]], una sección por obstáculo.

```
¿Qué te está bloqueando?
├─ Espacios filtrados     → ${IFS} / %09 / {a,b}    → § Sin espacios
├─ Barras filtradas       → ${HOME:0:1} / cd        → § Sin barras
├─ Palabra clave          → w'h'oami / base64 / $@  → § Palabra clave bloqueada
├─ Lista blanca de comandos → abusar sus flags      → [[Argument injection - abuso de flags]]
└─ WAF con firma          → codificar + POST        → § WAF con firma
```

La cuarta rama es la que se olvida: cuando el comando está fijo y no se puede cambiar, la salida no es evadir el filtro sino **abusar del binario permitido**.

## Cheatsheets — entrada directa a los payloads

- [[Command injection contextos - matriz de referencia]] — Cómo romper según dónde cae el input: suelto, entre comillas, en una ruta, newline
- [[Command injection shells - matriz de referencia]] — Diferencias entre `sh`, `cmd` y PowerShell: separadores, retardo, red, lectura
- [[Command injection ciego - matriz de referencia]] — Confirmar ejecución, oráculo booleano, escritura a la raíz web, exfiltración por DNS
- [[Command injection evasión - matriz de referencia]] — Sin espacios / sin barras / palabras clave / WAF / Windows
- [[Command injection impacto - matriz de referencia]] — Reconocimiento, reverse shells por lenguaje, promoción a TTY, pivote
- [[Argument injection - matriz de referencia]] — Qué flag pedirle a cada binario: ejecución, escritura, lectura, cambio de destino

## Orden de aprendizaje

Secuencia por dependencia conceptual. Este es el temario del módulo.

1. [[CWE-78 - OS Command Injection]] — qué es y por qué existe
2. [[Command injection contextos - matriz de referencia]] — dónde cae la inyección y cómo romper
3. [[Command injection - canal directo]] — el caso feliz, fija el modelo mental
4. [[Command injection shells - matriz de referencia]] — qué cambia entre plataformas
5. [[Command injection - canal fuera de banda]] — el canal que resuelve el caso asíncrono
6. [[Command injection - canal ciego]]
7. [[La latencia como canal de datos]] → [[Command injection - canal temporal]] — el concepto antes de la técnica
8. Evasiones
9. [[CWE-88 - Argument Injection]] → [[Argument injection - abuso de flags]] — rompe la intuición de "sin shell no hay riesgo"
10. Impacto: [[Command injection - a shell interactiva]], [[Webshell]]

El punto 9 va al final a propósito: recién tiene sentido cuando ya se interiorizó que la mitigación de CWE-78 es pasar argumentos como array. La sorpresa pedagógica es que esa mitigación correcta no cierra CWE-88.

## Relación con otros dominios

- [[MOC - File upload]] y [[MOC - File inclusion]] — llegan al mismo destino por otra puerta. Los tres terminan en [[Webshell]], que es el nodo compartido.
- [[MOC - SQL injection]] — mismo eje de canales y misma lógica de extracción ciega. Quien entiende uno tiene medio camino hecho en el otro.
- El impacto de escritura de [[Argument injection - matriz de referencia]] § 2 desemboca directo en el dominio de upload.

## Cara azul

Qué emite cada canal y qué lo ve:

| Canal | Telemetría | Firma |
|---|---|---|
| Directo / ciego | [[Proceso hijo del servidor web]] | El servidor web como padre de `/bin/sh` |
| Temporal | [[Log de acceso del servidor web]] | Latencias bimodales; proceso hijo de vida larga |
| Fuera de banda | [[Consulta DNS saliente]] | Subdominios de alta entropía hacia un dominio sin historial |
| Shell interactiva | [[Proceso hijo del servidor web]] | Intérprete con redirección a descriptor de red |
| Argument injection | [[Proceso hijo del servidor web]] | **Ninguna anómala** — el árbol de procesos es el legítimo |

La última fila es el hueco real del dominio: la telemetría lo captura y ninguna detección genérica lo ve, porque hay que conocer la invocación normal de la aplicación para notar la flag de más.

## Huecos conocidos

- [x] Los cuatro canales de extracción — completos
- [x] Ruptura del contexto — en [[Command injection contextos - matriz de referencia]]
- [x] Argument injection — [[Argument injection - abuso de flags]] y su matriz
- [x] Evasiones — en [[Command injection evasión - matriz de referencia]]
- [x] Impacto — [[Command injection - a shell interactiva]] y [[Webshell]]
- [x] Cara azul — [[Intérprete de comandos como hijo del servidor web]], la detección de mayor fidelidad del lado web: ancla en la relación padre-hijo, que ninguna evasión de la matriz toca
- [ ] Ejecución sin proceso — `eval` de PHP, SSTI y deserialización no emiten `execve`. Son dominios propios y hoy no existen
