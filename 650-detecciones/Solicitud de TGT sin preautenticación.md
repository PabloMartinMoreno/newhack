---
tipo: deteccion
tecnicas: ["[[T1558.004 - AS-REP Roasting]]"]
telemetria: ["[[Windows 4768 - Kerberos TGT requested]]"]
forma: evento
ventana: 
estado: idea
fidelidad: alta
logica: sigma
validada: 
aliases:
  - detección de AS-REP roasting
tags:
  - dominio/ad
---

# Solicitud de TGT sin preautenticación

## Qué detecta

Una petición de ticket inicial de Kerberos con la **preautenticación ausente**. Es la firma exacta de [[AS-REP roasting]], y es de forma `evento` porque la condición casi no ocurre de forma legítima: una sola petición así ya merece mirarse.

## Lógica

```yaml
detection:
  selection:
    EventID: 4768
    PreAuthType: '0'
  condition: selection
```

Refuerzo de fidelidad, no imprescindible pero muy barato: el **tipo de cifrado**. Si además `TicketEncryptionType` es el valor de RC4 en un dominio que soporta AES, es degradación deliberada — la respuesta se pide débil para romperla más rápido.

```yaml
  selection_rc4:
    EventID: 4768
    PreAuthType: '0'
    TicketEncryptionType: '0x17'
```

## Falsos positivos conocidos

- **Cuentas legítimas sin preautenticación**, que existen por compatibilidad con clientes viejos. Son el falso positivo dominante, y la respuesta correcta no es excluirlas de la regla: es **arreglarlas**. La superficie es finita y conocida —una consulta al directorio la lista entera—, así que conviene tratar cada una como un hallazgo a corregir, no como ruido a filtrar.
- **Algunos dispositivos y appliances** viejos que autentican así por diseño. Se documentan y se acotan por cuenta.

A diferencia de casi todas las detecciones del vault, acá la lista de excepciones **es también la lista de trabajo pendiente del defensor**.

## Evasiones conocidas

- **Que no haya cuentas sin preautenticación** — entonces no hay ataque que detectar, porque no hay superficie. Es la mitigación, no una evasión.
- **Pedir despacio** no ayuda al atacante: como es forma `evento` y de alta fidelidad, una sola petición ya dispara. Bajar el ritmo no cambia nada.
- **RC4 forzado evitado** — pedir AES no evade la regla principal, que ancla en la preautenticación, no en el cifrado. Solo evade el refuerzo.

Es una de las pocas detecciones del vault que no se evade bajando el volumen, porque no depende del volumen.

## Cómo se prueba

Disparador: [[AS-REP roasting]] en un laboratorio con al menos una cuenta configurada sin preautenticación.

Forma `evento`: un disparo la valida. La única verificación previa es que la **auditoría de Kerberos esté encendida en todos los controladores** — el atacante habla con uno, no necesariamente con el que se está mirando. Ver [[Windows 4768 - Kerberos TGT requested]].
