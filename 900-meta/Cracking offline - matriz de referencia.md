---
tipo: meta
aliases:
  - cracking offline
  - hashcat cheatsheet
  - john cheatsheet
  - romper hashes
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Cracking offline - matriz de referencia

> [!info] Referencia pura, no un zettel
> Romper un hash o ticket **capturado**, sin tocar el objetivo. El criterio online vs offline y de dónde sale cada hash, en [[MOC - Ataques de contraseña]]. Herramientas: [[hashcat]] (GPU, lo rápido) y [[john]] (CPU, formatos raros y los `*2john`).

Tres pasos: **identificar** el hash → **elegir el ataque** (wordlist / regla / máscara) → correr. `hash.txt` = el/los hash; `rockyou.txt`/`lista.txt` = wordlist. Sin datos de objetivo real.

## 1. Identificar el hash

| Cómo | Comando |
|---|---|
| Por forma (heurística) | `hashid 'HASH'` · `name-that-hash -t 'HASH'` |
| Ejemplos de hashcat | `hashcat --example-hashes \| less` (buscar la forma) |
| Formatos que lee john | `john --list=formats` |

El prefijo delata: `$6$`=sha512crypt, `$1$`=md5crypt, `$2b$`=bcrypt, `$krb5tgs$`=Kerberoast, `aad3b…`=LM/NTLM del SAM.

## 2. Modos comunes de hashcat (`-m`)

| Hash | `-m` | De dónde (ver [[MOC - Ataques de contraseña]]) |
|---|---|---|
| NTLM (SAM/NTDS/LSASS) | `1000` | volcado de credenciales |
| NetNTLMv2 | `5600` | Responder/relay |
| NetNTLMv1 | `5500` | ídem, downgrade |
| LM | `3000` | SAM viejo |
| DCC2 / mscash2 (cache de dominio) | `2100` | host sin DC |
| Kerberoast (TGS-REP) | `13100` | roasting |
| AS-REP roast | `18200` | roasting sin preauth |
| sha512crypt `$6$` | `1800` | `/etc/shadow` |
| md5crypt `$1$` | `500` | shadow/IOS viejo |
| bcrypt `$2*$` | `3200` | apps web |
| JWT (HS256) | `16500` | secreto de firma |
| KeePass | `13400` | loot |
| ZIP / Office / PDF | `13600` / `9x00` / `10x00` | archivos protegidos |

## 3. Ataques de hashcat (`-a`)

| Ataque | Flag | Ejemplo |
|---|---|---|
| Diccionario | `-a 0` | `hashcat -m 1000 hash.txt rockyou.txt` |
| Diccionario + reglas | `-a 0 -r` | `hashcat -m 1000 hash.txt rockyou.txt -r rules/best64.rule` |
| Máscara (fuerza bruta dirigida) | `-a 3` | `hashcat -m 1000 hash.txt '?u?l?l?l?l?d?d?d'` |
| Combinador (dos listas) | `-a 1` | `hashcat -m 1000 hash.txt lista1 lista2` |
| Híbrido (wordlist + máscara) | `-a 6` / `-a 7` | `hashcat -m 1000 hash.txt rockyou.txt '?d?d?d'` |

**Máscaras:** `?l` minúscula · `?u` mayúscula · `?d` dígito · `?s` símbolo · `?a` todo · `?b` byte. Charset propio: `-1 ?l?d` y después `?1?1?1?1`.

**Reglas** que más rinden: `best64.rule` (rápida), `rockyou-30000.rule`, `OneRuleToRuleThemAll.rule` (lenta, exhaustiva). Mutan la wordlist (mayúsculas, leet, sufijos).

## 4. John the Ripper

Cuando el formato es raro o hay que **extraer** el hash de un archivo con los `*2john`.

| Tarea | Comando |
|---|---|
| Diccionario | `john --wordlist=rockyou.txt hash.txt` |
| Con reglas | `john --wordlist=rockyou.txt --rules=Jumbo hash.txt` |
| Forzar formato | `john --format=krb5tgs hash.txt` |
| Ver crackeados | `john --show hash.txt` |
| Modo incremental (brute) | `john --incremental hash.txt` |

Extraer el hash de un archivo (`*2john`): `zip2john f.zip > h` · `ssh2john id_rsa > h` · `keepass2john f.kdbx > h` · `office2john f.docx > h` · `rar2john` · `pdf2john`.

## 5. Gestión del crackeo

| Tarea | hashcat | john |
|---|---|---|
| Ver resultados | `hashcat -m 1000 hash.txt --show` | `john --show hash.txt` |
| Asociar user:hash | `--username` | lee `user:hash` solo |
| Quitar ya crackeados | `--left` | — |
| Potfile (cache de crackeados) | `~/.local/share/hashcat/hashcat.potfile` | `~/.john/john.pot` |
| Rendimiento | `-O` (optimizado) · `-w 3` (workload) · `-b` (benchmark) | hilos con `--fork=N` |
| Estado en vivo | tecla `s` | tecla cualquiera |

## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| `No hashes loaded` | modo/formato equivocado o hash mal copiado | re-identificar; revisar que no sobre un salto de línea |
| `Exhausted` sin romper | la wordlist no tenía la contraseña | sumar reglas, máscara, o wordlist más grande (SecLists) |
| Lentísimo | bcrypt/sha512crypt son lentos por diseño | GPU, wordlist curada + reglas; no brute puro |
| `Separator unmatched` (john) | formato mal | `--format=` explícito |
| Salteó un hash salado | cada salt multiplica el trabajo | igual corre; priorizar wordlist chica + reglas |
