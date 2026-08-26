---
tipo: moc
dominio: web
aliases:
  - MOC CSV
tags:
  - dominio/web
---

# MOC - CSV injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-1236 - Improper Neutralization of Formula Elements in a CSV File]]. Los payloads, en [[CSV - matriz de referencia]]. Acá vive **la decisión**.

Dominio compacto, y el más desplazado del vault: el atacante escribe la carga en un campo de la aplicación web, pero la carga se ejecuta **en otro programa, en la máquina de otra persona, después** —cuando un administrador exporta a CSV y lo abre en una hoja de cálculo—. No hay sink en el servidor; el sink es Excel, LibreOffice o Google Sheets, en la estación del analista.

| Eje | Valores |
|---|---|
| Capacidad | fuga de datos (exfil) · ejecución de comandos (DDE) |
| Aplicación | Excel · LibreOffice · Google Sheets → matriz |
| Disparador | `=` `+` `-` `@` tab CR → matriz |
| Impacto | robo del informe · phishing · RCE en la estación |

**La capacidad es el eje raíz**, como en SSTI y XSLT: qué puede hacer la fórmula —leer y exfiltrar, o ejecutar— decide el trabajo y el requisito. La aplicación y los disparadores van a matriz.

## Árbol de decisión — qué capacidad

```
¿Un campo de usuario se exporta a CSV/planilla?  → [[CSV - matriz de referencia]] § 2
├─ No, o el export prefija las fórmulas → no hay dominio
└─ Sí — plantá =1+1 y confirmá que evalúa
   │
   ├─ ¿Objetivo: robar el informe de otros usuarios?
   │     → [[CSV - fuga de datos por fórmula]]   ← PRIMERO, sin requisito del cliente
   │       WEBSERVICE / IMPORT* leen celdas y las exfiltran al abrir
   │
   └─ ¿Objetivo: ejecutar en la máquina del analista?
         → [[CSV - ejecución de comandos por fórmula]]
           DDE, pero necesita DDE habilitado (raro hoy) y aceptar advertencias
```

Tres cosas que este orden codifica:

**La exfiltración va primero porque no depende del cliente.** `WEBSERVICE` e `IMPORT*` disparan al abrir el archivo, sin macros ni DDE, y leen el resto de la planilla —los datos de otros usuarios del informe—. Es la capacidad fiable.

**La ejecución es el techo y el caso raro.** DDE está deshabilitado por defecto en Office moderno, así que la ejecución es oportunista: se planta junto con la exfiltración y se gana si el entorno resulta vulnerable, sin apostar el hallazgo a ella.

**La víctima es un administrador, no un usuario.** El que abre el export es quien descarga el informe —más privilegios, máquina interna—. Es lo que hace peligroso un dominio de nombre inocuo, y hay que decirlo en el informe: el impacto no es sobre el atacante ni sobre un usuario común, es sobre el personal del objetivo.

## Árbol de decisión — qué consigo

```
¿Qué permitió la planilla?
├─ WEBSERVICE/IMPORT* → exfil del informe completo (datos de todos los usuarios)
├─ HYPERLINK → phishing dentro de un informe de confianza
└─ DDE → RCE en la estación del analista → post-explotación interna
```

## Cheatsheets — entrada directa

- [[CSV - matriz de referencia]] — Disparadores y evasión, confirmar, exfiltración por app, DDE, phishing, dónde plantar, mitigación

## Orden de aprendizaje

1. [[CWE-1236 - Improper Neutralization of Formula Elements in a CSV File]] — la inyección diferida y desplazada, y por qué la víctima es el analista
2. [[CSV - matriz de referencia]] — disparadores y payloads
3. [[CSV - fuga de datos por fórmula]] — la capacidad fiable
4. [[CSV - ejecución de comandos por fórmula]] — el techo, cuando DDE está habilitado

## Relación con otros dominios

- [[XSS - almacenado]] — el primo por delivery: los dos plantan una carga en un campo que otro usuario "abre". La diferencia es el sink —navegador contra planilla— y la víctima —un usuario contra un analista—. CSV injection pasa los filtros de XSS porque no inyecta HTML, solo texto que empieza con `=`.
- [[MOC - Command injection]] — [[CSV - ejecución de comandos por fórmula]] es ejecución de comandos desplazada: el mismo impacto que [[Command injection - canal directo]] pero en la estación del analista, no en el servidor.
- [[MOC - Telemetría de Windows]] — la ejecución por DDE nace un proceso hijo de Excel, que vería la telemetría de endpoint, pero el vault no tiene una detección escrita para el par `excel.exe` → `cmd.exe`.
- **La firma de inyección transversal** — el `=` inicial es otro metacarácter de estructura en un campo de datos, del mismo grupo que las cuatro hermanas, el Host, el CRLF y el correo, aunque el sink sea una planilla y no web.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Fuga de datos | [[Registro del WAF]] · [[Log de auditoría de la aplicación]] | Campo almacenado que empieza con `=WEBSERVICE`/`=HYPERLINK`/`=IMPORT` |
| Ejecución (DDE) | [[Registro del WAF]] · [[Log de auditoría de la aplicación]] | Campo que empieza con `=cmd\|` |
| Ejecución en la estación | endpoint (no modelado para Office) | `cmd.exe`/`powershell.exe` con padre `excel.exe` |

La observación que define la cara azul, y agrega un caso al patrón del vault:

**La firma sobre la entrada es escribible; el impacto vive fuera del servidor.** Un campo almacenado que empieza con un carácter de fórmula seguido de `WEBSERVICE`, `IMPORT`, `HYPERLINK` o `cmd|` no tiene forma legítima —un nombre puede empezar con `+`, pero no con `=cmd|`—. Es una firma de buena fidelidad sobre la entrada, escribible, y del mismo grupo que las firmas de inyección. Pero el impacto —la exfiltración o la ejecución— ocurre en la **planilla del analista**, fuera del servidor: el vault no lo ve, igual que no ve el navegador de la víctima en los ataques del lado del cliente.

Es una variante nueva del patrón "el servidor es ciego a lo que pasa afuera": en clickjacking y tabnabbing lo de afuera es el navegador de la víctima; acá es la hoja de cálculo del analista. La diferencia con aquellos es que CSV injection **sí tiene un punto de entrada en el servidor** —el campo se almacena—, así que la firma de entrada es escribible, mientras que en los puramente del lado del cliente ni eso. La ejecución por DDE, además, sería detectable en el endpoint por el proceso hijo de Excel, un hueco de cobertura que [[MOC - Telemetría de Windows]] podría cerrar.

Vigésimo cuarto dominio cerrado sin detección nueva, con la firma de entrada como candidato escribible.

## Huecos conocidos

- [x] Las dos capacidades — exfiltración y ejecución
- [x] Disparadores, payloads por app y mitigación — una matriz (dominio compacto)
- [x] Cara azul — firma de entrada escribible, impacto fuera del servidor
- [ ] **La ejecución por DDE nace `excel.exe` → `cmd.exe`**, detectable en el endpoint pero sin detección escrita para Office en [[MOC - Telemetría de Windows]]. Hueco de cobertura, no de fuente
- [ ] Inyección de fórmulas en otros formatos de exportación —ODS, XLSX generado, TSV— con los mismos disparadores
- [ ] La firma de entrada `=fórmula` es otro sub-patrón del candidato transversal de firma de inyección
