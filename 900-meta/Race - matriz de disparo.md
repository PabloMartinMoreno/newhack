---
tipo: meta
aliases:
  - single-packet attack
  - disparo de race
  - Turbo Intruder race
tags:
  - meta/referencia
  - dominio/web
---

# Race - matriz de disparo

> [!info] Referencia pura, no un zettel
> Cómo hacer que N peticiones lleguen dentro de la ventana. Dónde buscar las ventanas está en [[Race - superficies y sub-estados]]; el criterio, en [[MOC - Race conditions]].

El dominio no tiene payload: tiene una técnica de sincronización. Todo esto es cómo vencer el jitter de la red para que las peticiones colisionen.

## 0. Elegir la técnica según el protocolo

| Conexión al servidor | Técnica | Peticiones que colisionan |
|---|---|---|
| HTTP/2 | **Ataque de un solo paquete** | 20-30 en un paquete TCP |
| HTTP/1.1 | **Sincronización por último byte** | Depende del jitter, decenas |

El ataque de un solo paquete es el que hizo el dominio fiable: al meter todas las peticiones en un paquete TCP, llegan sin dispersión. Es la primera opción siempre que haya HTTP/2.

## 1. Ataque de un solo paquete (HTTP/2)

La idea: mandar todas las peticiones menos su byte final, y después soltar todos los bytes finales en un solo paquete. El servidor recibe las 20-30 completas a la vez.

Con **Turbo Intruder** (extensión de Burp), la plantilla incorporada:

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    # 20 peticiones idénticas en el mismo paquete
    for i in range(20):
        engine.queue(target.req, gate='race1')
    engine.openGate('race1')

def handleResponse(req, interesting):
    table.add(req)
```

`gate` retiene las peticiones; `openGate` las suelta juntas. `Engine.BURP2` habilita el modo HTTP/2 de un solo paquete.

Desde el propio Burp Repeater: agrupar las pestañas y elegir **"Send group in parallel (single-packet attack)"** — es la forma sin escribir código, y suele alcanzar.

## 2. Sincronización por último byte (HTTP/1.1)

Cuando no hay HTTP/2. Se abren N conexiones, se manda casi toda cada petición dejando el último byte, se espera a que todas estén listas, y se sueltan los últimos bytes a la vez.

Turbo Intruder lo hace con `Engine.THREADED` y muchas conexiones; es menos preciso que el de un solo paquete porque el jitter sigue presente, así que hace falta más volumen y más intentos.

## 3. Calentar la conexión

El primer request de una conexión suele ser más lento —el servidor inicializa sesión, carga cachés, abre la conexión a la base—. Ese retardo dispersa la ráfaga. Se manda una o varias peticiones previas por la misma conexión para que los recursos estén calientes antes de la colisión:

```python
# petición de calentamiento, fuera del gate
engine.queue(warmup_req)
# después la ráfaga sincronizada
for i in range(20):
    engine.queue(target.req, gate='race1')
```

Es lo que más mejora la tasa de éxito en la práctica, y lo que más se olvida.

## 4. Calibrar el número de peticiones

- **Pocas** (2-5): puede no colisionar si la ventana es muy corta.
- **Muchas** (50+): el servidor empieza a serializarlas o a rechazar, y baja el éxito.
- **Punto dulce**: típicamente 10-30. Se prueba subiendo de a poco.

Repetir el ataque varias veces: la colisión es probabilística, y lo que no dio en un intento da en el tercero.

## 5. Detectar que hay ventana antes de explotar

Confirmar que la operación no es atómica sin dañar nada:

- Mandar la ráfaga contra algo reversible o inocuo y ver si **el efecto ocurre más veces de las permitidas**.
- Observar si dos respuestas concurrentes reflejan el **mismo estado previo** —las dos dicen "saldo: 100" antes de descontar—.
- Medir si el conteo final no coincide con el número de operaciones que deberían haber pasado.

## 6. Ajustes que suben la tasa de éxito

| Problema | Ajuste |
|---|---|
| El jitter dispersa aun con un solo paquete | Calentar la conexión, § 3 |
| El servidor serializa | Bajar el número de peticiones concurrentes |
| La ventana es cortísima | Más intentos, y buscar un endpoint más lento que la ensanche |
| Hay un proxy que reempaqueta | Apuntar más cerca del back, o usar último byte |
| La respuesta no dice si colisionó | Medir el estado después, no la respuesta |

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| Todas las respuestas iguales y un solo efecto | No colisionó: se serializaron. Calentar y reintentar |
| Funciona 1 de 10 veces | Normal: es probabilístico. Repetir |
| `Engine.BURP2` no disponible | Turbo Intruder viejo, o el objetivo no habla HTTP/2. Usar último byte |
| El servidor rechaza la ráfaga | Demasiadas peticiones; bajar el número |
| El efecto ocurre una vez de más y no más | La ventana deja pasar dos, no veinte. Puede alcanzar igual |
| Nada colisiona nunca | Probablemente hay atomicidad real. El dominio no aplica acá |

## Relacionadas

[[MOC - Race conditions]] · [[Race - superficies y sub-estados]] · [[Race - superación de límite]] · [[Request smuggling - matriz de sondeo]]
