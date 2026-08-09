---
tipo: deteccion
tecnicas: ["[[T1558.003 - Kerberoasting]]"]
telemetria: ["[[Windows 4769 - Kerberos service ticket requested]]"]
forma: agregado
ventana: "10m"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - detección de kerberoasting
tags:
  - dominio/ad
---

# Tickets de servicio con cifrado débil en volumen

## Qué detecta

Una cuenta pidiendo tickets de servicio para **muchos servicios distintos en poco tiempo**, con cifrado débil. Es la firma de [[Kerberoasting]], y es de forma `agregado` porque un ticket suelto es rutina absoluta: lo que delata es el patrón de pedir muchos.

## Lógica

```
kerberos_tgs
| where EventID == 4769
| where timestamp > ago(10m)
| where TicketEncryptionType == '0x17'          // RC4
| where ServiceName !endswith '$'               // no cuentas de máquina
| summarize servicios = dcount(ServiceName), total = count() by TargetUserName, IpAddress
| where servicios > 10
```

Tres condiciones hacen el trabajo, y cada una descarta una fuente de ruido:

- **RC4** — degradación deliberada. Un dominio moderno usa AES para lo legítimo; pedir RC4 es querer romperlo más rápido.
- **El servicio no termina en `$`** — descarta las cuentas de máquina, que tienen contraseña larga y aleatoria y no valen la pena romper. El ataque va por las cuentas de usuario.
- **Muchos servicios distintos** — un usuario normal pide tickets para los pocos servicios que usa. Diez o más en diez minutos no es un patrón humano.

## Falsos positivos conocidos

- **Cuentas de escaneo de vulnerabilidades** que hacen exactamente esto de forma autorizada — piden tickets de todo para auditar contraseñas débiles. Es el falso positivo dominante, y se excluye por cuenta.
- **Aplicaciones que acceden a muchos servicios** legítimamente — un servidor de integración, un orquestador. Se conocen y se excluyen.
- **RC4 normal en un dominio viejo.** Si el dominio no forzó AES, RC4 es el valor por defecto y la condición de cifrado no discrimina nada. Ahí hay que apoyarse solo en el volumen, y **primero endurecer el dominio**. Ver [[Sin línea base no hay anomalía]].

## Evasiones conocidas

- **Pedir despacio**, por debajo del umbral de servicios por ventana. Es la evasión directa y funciona: la ventana define cuán lento hay que ir. Un atacante paciente pide de a pocos durante horas.
- **Pedir AES en vez de RC4** — evade la condición de cifrado. Se rompe más lento, pero evade. Deja solo el volumen como señal.
- **Apuntar a pocas cuentas de servicio** conocidas de antemano, en vez de a todas. Si la enumeración ya identificó las tres que valen, no hay volumen que detectar.

Contra un atacante que sabe esto, la detección degrada a "pidió un ticket RC4 para una cuenta de servicio", que es de baja fidelidad. La ventana buena es contra el barrido ruidoso, que es lo que hacen las herramientas por defecto.

## Cómo se prueba

Disparador: [[Kerberoasting]] en laboratorio, con varias cuentas de servicio bajo usuario.

Forma `agregado`: el disparo tiene que ser un barrido real, no un ticket. Y el umbral de servicios hay que derivarlo de la línea base — cuántos servicios distintos pide un usuario normal, que varía muchísimo entre dominios.
