---
tipo: tradecraft
clase: "[[CWE-1321 - Prototype Pollution]]"
eje: gadget
implementacion: "Contaminar una propiedad que una API de Node lee como opción, hasta llegar a ejecución"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Log de errores del servidor web]]", "[[Conexión saliente del servidor de aplicación]]", "[[Registro del WAF]]"]
requisitos: [contaminacion-confirmada-en-el-servidor, gadget-en-las-bibliotecas-cargadas]
coste: alto
alternativas: ["[[Prototype pollution - propiedad que gobierna una decisión]]", "[[Deserialización - cadena de gadgets]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - prototype pollution RCE
  - Node gadget
tags:
  - dominio/web
---

# Prototype pollution - gadget del lado del servidor

## Cuándo lo elijo

Cuando la contaminación está confirmada del lado del servidor y [[Prototype pollution - propiedad que gobierna una decisión]] no dio nada, o dio poco y hace falta demostrar impacto máximo.

Es la rama cara del dominio y la que más se parece a [[Deserialización - cadena de gadgets]]: el acceso ya está, lo que falta es encontrar el lugar del código que convierta una propiedad de más en ejecución. Conviene entrar sabiendo que puede no haberlo.

## Por qué funciona

Node pasa objetos de opciones por todos lados, y esos objetos casi nunca traen todas sus propiedades definidas. Una propiedad que falta se busca en el prototipo, así que contaminarla equivale a **inyectar un argumento en una llamada que el atacante no hace**.

Las familias de gadget, en orden de fiabilidad:

- **Opciones de creación de procesos.** `child_process` acepta un objeto con `shell`, `env` y `NODE_OPTIONS`. Contaminar `NODE_OPTIONS` con `--require` hace que cualquier proceso hijo cargue un archivo elegido; contaminar `shell` cambia el intérprete. La aplicación no tiene que llamar a nada raro: alcanza con que en algún momento nazca un proceso hijo por cualquier motivo.
- **Motores de plantilla.** Varios compilan la plantilla concatenando opciones; contaminar la que controla el prólogo del código generado da ejecución en el siguiente renderizado. Se cruza con [[MOC - SSTI]] por el mismo efecto y por otro camino.
- **Resolución de módulos.** Contaminar propiedades que gobiernan dónde se buscan los módulos hace que un `require` cargue otra cosa.
- **Configuración de bibliotecas.** Cualquier opción que termine en una llamada al sistema o en una construcción de cadena que después se evalúe.

El catálogo por biblioteca está en [[Prototype pollution gadgets - matriz de referencia]].

La propiedad que hay que entender es la del disparo diferido: **contaminar no ejecuta nada**. La ejecución ocurre después, cuando la aplicación pasa por el camino que lee esa opción. A veces hace falta provocarlo con una segunda petición a un endpoint distinto, y esa separación entre contaminar y disparar es lo que hace el trabajo lento.

## Cómo falla

Falla cuando el proceso nunca pasa por ninguna de las rutas con gadget. Es el resultado más común y es legítimo: la contaminación existe, el impacto máximo no se alcanza, y se reporta lo que se pudo demostrar.

Falla contra `Object.freeze(Object.prototype)` y contra `--disable-proto=delete`, que cierran el dominio entero.

Falla contra versiones nuevas de las bibliotecas: los gadget publicados se parchean, y aunque la contaminación siga siendo posible, la cadena que se conocía deja de estarlo. Es la misma caducidad que documenta [[Deserialización - cadena de gadgets]], y por eso este dominio necesita revalidación tanto como aquel.

## Coste

Alto. Enumerar qué bibliotecas y qué versiones están cargadas es un trabajo propio, y sin eso los gadget se prueban a ciegas. Cada intento son dos peticiones —contaminar y disparar— y el fallo suele ser silencioso.

Presupuesto razonable: probar los gadget de la matriz que correspondan a lo que se sepa de la pila, y si no salió, bajar a la rama de propiedad. La escalada a ejecución es tentadora y es donde se va la tarde, igual que en [[SSTI - escape del entorno restringido]].

> [!danger] Esto rompe la aplicación
> Contaminar opciones de procesos o de resolución de módulos afecta a **todas** las peticiones que atienda ese proceso, no solo a las del atacante. Un gadget a medio funcionar deja la aplicación en un estado incoherente hasta que se reinicie. Confirmar y explotar tienen que ser dos pasos, y en un entorno productivo hay que acordar la ventana antes.

## Huella esperada

Es la variante más visible del dominio, y por el mismo motivo que casi todas las de ejecución del vault: **nace un proceso hijo del servidor web**, que es la relación en la que ancla [[Intérprete de comandos como hijo del servidor web]]. Esa detección lo ve sin saber que hubo contaminación, igual que ve command injection, deserialización y SSTI.

Cuando el gadget usa `NODE_OPTIONS` con `--require` apuntando a un archivo remoto, además hay una conexión saliente desde el proceso de la aplicación, que cubre [[Barrido de puertos internos desde el servidor de aplicación]] por destino anómalo.

Antes de eso queda el reconocimiento, y es lo que más se ve: los intentos con gadget equivocados producen excepciones dispersas en [[Log de errores del servidor web]], a menudo sin relación aparente con la petición que las causó — porque el error lo lanza otra petición, la que pasó por el camino contaminado. Esa desconexión entre causa y síntoma es la firma real del dominio del lado defensivo, y es difícil de leer sin saber qué se busca.

Y la carga en sí es texto reconocible —`__proto__`, `constructor[prototype]`— en la URL o en el cuerpo. Ver la nota sobre por qué acá la firma sí funciona en [[MOC - Prototype pollution]].
