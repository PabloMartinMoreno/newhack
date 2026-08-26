---
tipo: moc
dominio: web
aliases:
  - MOC HPP
  - parameter pollution
tags:
  - dominio/web
---

# MOC - HTTP parameter pollution

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-235 - Improper Handling of Extra Parameters]]. La tabla de resolución y los payloads, en [[HPP - matriz de referencia]]. Acá vive **la decisión**.

Es el tercer dominio de **discrepancia de parseo** del vault, con [[MOC - Request smuggling]] y la parte de discrepancia de [[MOC - Web cache]]. Los tres abusan que dos componentes de la cadena interpreten lo mismo distinto: en smuggling, dónde termina la petición; en caché, cómo se normaliza la clave; en HPP, qué valor tiene un parámetro que aparece dos veces. La tabla de cómo resuelve cada marco de trabajo un duplicado **es** el dominio.

| Eje | Valores |
|---|---|
| Uso de la discrepancia | bypass (dos capas discrepan) · inyección de parámetro (agregar a una URL construida) |
| Resolución | primero · último · concatenado · lista → matriz |
| Separador | `&` · `%26` · `;` → matriz |
| Impacto | evasión de WAF · bypass de lógica/autz · segundo orden · client-side |

**El uso de la discrepancia es el eje raíz**: aprovechar que dos capas resuelven distinto para colar un valor (bypass), o inyectar un `&` para agregar parámetros a una petición que la aplicación construye (inyección). La tabla de resolución y las codificaciones van a matriz.

## Árbol de decisión — cómo uso la discrepancia

```
¿La aplicación resuelve un parámetro duplicado?  → [[HPP - matriz de referencia]] § 2
├─ Probá ?x=1&x=2 → ¿usa 1, 2, o 1,2?
└─ Sí — ¿para qué?
   │
   ├─ Colar un valor que un filtro/WAF bloquea
   │     → [[HPP - bypass por discrepancia de parseo]]
   │       inocente donde valida el WAF, malicioso donde usa la app
   │       — es el sobre para meter SQLi/XSS por el WAF
   │
   └─ Agregar parámetros a una petición/URL que la app construye
         → [[HPP - inyección de parámetros]]
           servidor (segundo orden al backend) o cliente (enlace generado)
```

Tres cosas que este orden codifica:

**HPP es sobre todo un vehículo de evasión.** Su uso más frecuente no es un fin sino colar otra inyección por un WAF que discrepa con la aplicación. Por eso [[HPP - bypass por discrepancia de parseo]] se combina con las evasiones de cada dominio, y el payload sale de allí.

**La inyección de parámetros es el uso "propio".** Cuando la aplicación reenvía la entrada a una URL —al backend o a un enlace—, un `&` inyectado agrega parámetros que sobrescriben privilegios o cambian destinos. Es HPP como fin, no como vehículo.

**El punto de partida es la tabla de resolución.** Sin saber cómo resuelve cada capa, no se puede predecir dónde esconder el valor. Confirmar la resolución del WAF y de la aplicación por separado es el paso cero, y decide todo.

## Árbol de decisión — qué consigo

```
¿Qué logré con la discrepancia?
├─ Colé un payload por el WAF → la inyección de fondo (SQLi, XSS, command)
├─ Sobrescribí un parámetro de control → bypass de autz/lógica → [[MOC - Broken access control]]
├─ Inyecté un param al backend → segundo orden, a veces SSRF → [[MOC - SSRF]]
└─ Envenené un enlace generado → acción con la sesión de la víctima → [[MOC - CSRF]]
```

## Cheatsheets — entrada directa

- [[HPP - matriz de referencia]] — La tabla de resolución por marco de trabajo, confirmar cada capa, codificación del separador, bypass, inyección, sobrescritura

## Orden de aprendizaje

1. [[CWE-235 - Improper Handling of Extra Parameters]] — por qué un parámetro duplicado no tiene una resolución única
2. [[HPP - matriz de referencia]] — la tabla de resolución es lo primero
3. [[HPP - bypass por discrepancia de parseo]] — el uso más frecuente, como vehículo de evasión
4. [[HPP - inyección de parámetros]] — el uso propio, segundo orden y cliente

## Relación con otros dominios

- [[MOC - Request smuggling]] — el primo directo por discrepancia de parseo, y comparten la conclusión defensiva: la defensa falla cuando dos componentes ven cosas distintas. En smuggling la discrepancia es sobre el largo de la petición, en HPP sobre el valor de un parámetro.
- [[MOC - Web cache]] — la discrepancia de normalización de la clave de caché es la misma familia; un parámetro duplicado puede además envenenar la clave.
- **Todas las inyecciones** — HPP es un vehículo de evasión de WAF para SQLi, XSS, command, LDAP, etc. Se combina con la matriz de evasión de cada dominio; el payload es de allí, el sobre es de acá.
- [[MOC - Broken access control]] — sobrescribir un parámetro de rol o de precio es control de acceso/lógica por la vía del duplicado.
- [[MOC - SSRF]] y [[MOC - CSRF]] — la inyección de parámetros del lado del servidor cruza a SSRF; la del cliente, a CSRF vía enlace envenenado.
- [[CWE-88 - Argument Injection]] — pariente conceptual: HPP inyecta parámetros HTTP, argument injection inyecta flags de línea de comandos; los dos abusan la separación de argumentos.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Bypass por discrepancia | [[Log de acceso del servidor web]] · [[Registro del WAF]] | El mismo parámetro dos veces, con valores discrepantes |
| Inyección de parámetros | [[Registro del WAF]] · [[Log de acceso del servidor web]] | Un `&`/`%26` dentro de un valor que se refleja en una URL |
| Segundo orden | [[Conexión saliente del servidor de aplicación]] | La petición al backend con el parámetro inyectado |

La observación que define la cara azul, y es la ironía del dominio:

**El WAF —la fuente natural— es justo el que la técnica ciega.** En el bypass por discrepancia, si el WAF valida un valor y la aplicación usa otro, el WAF **registra el valor inocente que validó**, no el malicioso que la aplicación ejecutó. La herramienta que debería ver la inyección la deja pasar porque mira el valor equivocado. La firma —un parámetro duplicado con valores discrepantes— es escribible, pero tiene que estar en un componente que vea **todos** los valores y valide cada uno, no en uno que resuelva primero y valide después. Es la lección defensiva del dominio: **validar después de resolver el duplicado, no antes**, y que el WAF y la aplicación resuelvan igual.

Es el mismo patrón de discrepancia de parseo de [[MOC - Request smuggling]] —la defensa falla cuando dos componentes ven cosas distintas— aplicado al valor de un parámetro. La firma del parámetro duplicado es escribible sobre el log de acceso, que sí ve la query completa aunque el WAF mire un solo valor.

Vigésimo quinto dominio cerrado sin detección nueva, con la firma del duplicado como candidato escribible.

## Huecos conocidos

- [x] Los dos usos — bypass e inyección
- [x] Tabla de resolución, codificación y payloads — una matriz
- [x] Cara azul — firma del duplicado, con la ironía del WAF ciego
- [ ] **La firma del parámetro duplicado es escribible sobre el log de acceso**, no sobre el WAF —que la técnica ciega—. Candidato de detección, con la advertencia de dónde ponerlo
- [ ] HPP en el cuerpo (formularios, JSON con claves duplicadas) además de en la query, con resoluciones propias
- [ ] La resolución exacta por versión de marco de trabajo cambia; la tabla es orientativa y hay que confirmar contra el objetivo
