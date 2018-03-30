# TagManager

## Descripción

**TagManager** es un sencillo script que permite buscar todos los eventos (o atributos) de todas las organizaciones (o de una en concreto) que tengan una etiqueta específica (*tag_old*) y 

 -   o bien les añade (*add*) una nueva etiqueta (*tag_new*)
 -   o bien les cambia (*change*) la etiqueta (*tag_old*) por una nueva (*tag_new*)

Si se indica, se puede acotar por fechas (desde-hasta) y publicar los eventos.

Con esta herramienta se consigue etiquetar fácilmente eventos antiguos y de otras organizaciones en base al método de clasificación propuesto (Galaxies, Taxonomías, etiquetas propias y otras etiquetas) pudiendo:

 -   Crear una tarea en el “*cron*” que ejecute el **TagManager** para clasificación automática.  
 -   Etiquetas previas a la versión 2.4.
 -   Reclasificar con las nuevas Galaxies y Taxonomías.
 -   Reclasificar con nuestras propias “Taxonomías” la información que tengamos.
 -   Información proveniente de otras fuentes

Así, se puede compartir la misma información pero cada cual tener su propio criterio para clasificarla.


## Instalación

Para ejecutar el **TagManager** hay que tener instalado *Python 3* en el sistema dado que la librería para conectar con el MISP (*PyMISP*) está programado en ese lenguaje. Además, hay que tener instalado '*pip*' para instalar *PyMISP*:

```
user@machine:~$ sudo apt-get install -y python3 python3-pip
```

Una vez instalado, se puede instalar la librería de conexión con MISP [PyMISP](https://github.com/CIRCL/PyMISP):

```
user@machine:~$ sudo pip install pymisp
```


## Certificado

Para obtener el certificado .pem, que es el formato que PyMISP requiere, a partir del certificado .p12 (certificado.pem), se debe tener instalado **openssl**:

```
user@machine:~$ sudo apt-get install -y openssl
```

Posteriormente, se deben ejecutar el siguiente comando para obtener el certificado:

```
openssl pkcs12 -in certificado.p12 -out certificado.pem -clcerts -nokeys
```

La clave privada se obtiene con la siguiente instrucción:

```
openssl pkcs12 -in certificado.p12 -out certificado_key.pem -nocerts -nodes
```

Se añade la clave privada al certificado

```
cat certificado_key.pem >> certificado.pem
```

Por limpieza, se puede editar el fichero y quitar las cabeceras que no sean el certificado propiamente dicho pero no es obligatorio.


## Configuración

Antes de empezar, hay que editar el fichero **TagManager.py** y cambiar los datos de conexión al MISP contra el que se va a trabajar, el token y la ruta del certificado (si se requiere).

```
misp_url = 'https://www.csirt.es/misp/'
misp_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
misp_cert = '/path/to/certificate.pem'
misp_verifycert = True
```


## Uso

A partir de ahí, se puede ejecutar el **TagManager.py**. Con el parámetro -h, se puede ver la ayuda y los parámetros admitidos:
```
python3 TagManager.py -h
```

Las opciones son:

-   `-a / --action` es la acción a realizar cuyos valores pueden ser "add", "change" y "test"; "add" añade una etiqueta; "change" cambia una etiqueta por otra; "test" indica sobre qué eventos o atributos se realizará la acción si se cambia por "add" o "change"
-   `-t / --tag_old` es la etiqueta que se busca
-   `-n / --tag_new` es la etiqueta que se añade ("add") o cambia ("change")
-   `-o / --organisation` es la organización sobre la que se buscarán eventos/atributos; si no se pone este parámetro, se hace contra todas las organizaciones
-   `-i / --attributes` es el parámetro que indica que la acción se realizará sobre atributos (por defecto, es decir, si este parámetro, se realiza sobre los eventos)
-   `-p / --publish` es el parámetro que indica si al finalizar los cambios se publicará el evento
-   `-F / --date_from` es la fecha "desde" la cual se tienen en cuenta los evento (formato yyyy-MM-dd)
-   `-T / --date_to` es la fecha "hasta" la cual se tienen en cuenta los evento (formato yyyy-MM-dd)


## Ejemplos

Su uso es algo así como:

Añadir a los eventos que tengan la etiqueta "Trj=LokiBot", la etiqueta "APT":

```
python3 TagManager.py -a add -t "Trj=LokiBot" -n "APT"
```

Añadir a los eventos que tengan la etiqueta "Trj=LokiBot", la etiqueta "APT", y además se publica el evento:

```
python3 TagManager.py -a add -t "Trj=LokiBot" -n "APT" -p
```

Cambiar los eventos de la organización "CIRCL_1373" que tengan la etiqueta "Trj=LokiBot" por la etiqueta "APT":

```
python3 TagManager.py -a change -o CIRCL_1373 -t "Trj=LokiBot" -n "APT"
```

Visualizar los atributos de la organización "CIRCL_1373" que tengan la etiqueta 'osint:source-type="technical-report"' (hay que *escapar* las comillas en el comando):

```
python3 TagManager.py -a test -o CIRCL_1373 -t "osint:source-type=\"technical-report\"" -n "osint:source-type=\"other\"" -i
```

Un ejemplo con las fechas "desde" y "hasta":

```
python3 TagManager.py -a test -t "Trj=Silence" -n "APT" -F 2017-10-01 -T 2017-10-31
```
