---
tipo: meta
aliases:
  - ejemplo cracking OSINT
  - cracking con wordlist dirigida
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Cracking dirigido por OSINT - ejemplo

> [!info] Ejemplo completo, no un zettel
> Demuestra [[Cracking offline - matriz de referencia]] + [[Hashcat rules - matriz de referencia]] de punta a punta, con CeWL y el combinador: romper una contraseña que **cumple una política fuerte**, sin fuerza bruta. Datos ficticios (laboratorio). No se revela el plaintext: el valor es el método.

## Escenario

Hash comprometido del correo de Mark White (MD5): `97268a8ae45ac7d15c3cea4ce6ea550b`. OSINT:

- Nació el 05/08/1998 · vive en San Francisco · trabaja en **Nexura, Ltd.**
- Mascota: gato **Bella** · esposa **Maria** · hijo **Alex** · fan del béisbol
- Política: **≥ 12 caracteres, 1 mayúscula, 1 minúscula, 1 símbolo, 1 número**

## 1. Wordlist base con CeWL

En vez de tipear las palabras, se practica **CeWL**: se mete la OSINT en un `mark.html` y se crawlea. Clave: en el HTML van **solo los datos personales** (nombres, fechas, lugar, mascota, interés) — **no** la política, que metería basura genérica tipo `uppercase`/`symbol`.

```sh
python3 -m http.server 8000     # servir mark.html local
cewl -d 1 -m 2 --with-numbers -w mark_initial.txt http://<tun0>:8000/mark.html
```

`-d 1` profundidad 1 (página plana) · `-m 2` palabras ≥ 2 chars (capta `CA`/`US`) · `--with-numbers` incluye números (el `1998`). → **~27 palabras**. CeWL acá es overkill —se podrían tipear—, pero el ejercicio es practicar la herramienta.

## 2. Combinar palabras — combinador (`-a 1`)

La política pide ≥ 12, así que es probable que haya **unido dos datos**. El combinador une cada palabra con cada otra (incluida consigo misma):

```sh
hashcat --stdout -a 1 mark_initial.txt mark_initial.txt > mark_pairs.txt
```

→ **729 pares**.

## 3. Filtrar por largo (≥ 12)

Antes de gastar cómputo en reglas, tirar lo que la política ni permitiría:

```sh
awk 'length($0) >= 12' mark_pairs.txt > pairs_length12.txt
```

→ de 729 a **76**.

## 4. Reglas custom

`custom.rule` (capitalizar, leet, símbolo al final, y combinaciones) — funciones de [[Hashcat rules - matriz de referencia]]:

```
:
c
so0
c so0
sa@
c sa@
c sa@ so0
$!
$! c
$! so0
$! sa@
$! c so0
$! c sa@
$! so0 sa@
$! c so0 sa@
```

```sh
hashcat --stdout -r custom.rule pairs_length12.txt > mut_mark_final.txt
```

→ **1140 candidatos**, todos ≥ 12 y a medida.

## 5. Identificar y crackear

```sh
hashid -m 97268a8ae45ac7d15c3cea4ce6ea550b    # → MD5, Hashcat Mode 0
hashcat -a 0 -m 0 97268a8ae45ac7d15c3cea4ce6ea550b mut_mark_final.txt
```

`hashid -m` da el modo directo (`-m 0`); se valida que la forma/largo coincidan con un MD5 conocido (`echo -n test | md5sum`). Al romper, hashcat muestra la contraseña.

## La lección

El embudo cuenta la historia: **CeWL 27 → combinador 729 → filtro por política 76 → reglas 1140**. El combinador explota el espacio, el filtro lo recorta a lo que la política admite, las reglas lo vuelven a expandir pero ya compliant. Una política fuerte no protege contra una wordlist dirigida por OSINT: no es fuerza bruta, es inteligencia contextual + automatización. Lo reutilizable es el flujo, no este caso.
