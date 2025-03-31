# Queries_a_CSVs - qacsv.py
- Escribe queries a Bases de Datos en archivos .CSV.

En la Compañía en la que trabajo, surgió la necesidad de generar varios archivos .CSV 
(Comma Separated Values), a partir de datos de salida de diferentes queries a distintas
 BDs.
Estos CSVs deben ser guardados en directorios específicos del disco local C: (en un
sistema Windows), y sirven como entrada para un proceso de análisis de datos.    
Dado que en la Compañía los usuarios manejan habitualmente archivos .xlsx se propone que en un planilla de cálculo se generara la lista de todos los .CSV requeridos
junto con toda la información adicional necesaria para construir y almacenar dichos 
.CSV de salida.
Esta planilla de cálculo, cuyo nombre de archivo debe ser CSVs_list.xlsx, oficiará de
archivo de entrada del script qacsv.py, y debe tener el siquiente formato:

![image](CSVs_list_xlsx.png)

qacsv.py lo que hace es leer el archivo listas/CSVs_list.xlsx y completar los queries y 
tareas indicadas en cada una de sus filas.

Escribí dos versiones de qacsv.py. La procedural (o funcional) qacsv_proc.py y la OOP, qacsv_oop.py.
La versión OOP es más completa en términos de resumen de resultados.
Ambas versiones tienen la premisa de procesar todas y cada una de las líneas de CSVs_list.xlsx
y no detenerse por errores, solo registrarlos para cada caso y continuar.
Los resultados del proceso son registrados de la misma manera en la pantalla y en el archivo de log.

Definiciones:
- Archivo de Entrada: listas/CSVs_list.xlsx (camino relativo respecto de qacsv.py)
- Archivo de Logs: logs/qacsv_AAAAMMDDHHmm.log
- Format de CSVs_list.xlsx con estas consideraciones:
	- Se pueden adicionar todas las columnas que se deseen.
	- Las columnas que lee por nombre el script son: ['Periodo', 'Carpeta', 'Nombre de archivo CSV', 'Server Base', 'Modo de armado', 'Disk', 'path']
	- No es necessario completar todos los campos de las columnas ['Server Base','Disk', 'path']
		mientras su valor se igual a uno anterior existiete (ffil de dichas columnas)
- El valor de 'Period' es leído unicamente de la celda A2 <- df.loc[0, 'Periodo'], de lista/CSVs_list.xlsx.
- Si existe un CSV de salida con el mismo nombre (y en la misma carpeta destino), este será sobreescrito.
- CSVs_list_xlsx es modificado luego de la ejecución del script de la siguiente manera:    
  - a. Si no ocurren errores en la ejecución, CSVs_list.xlsx es movido a listas_hechas/CSV_list_AAAAMMDDHHmm.xlsx
  - b. Si oucrrió algún error se renombra CSVs_list_xlsx a CSVs_list_AAAAMMDDHHmm_err.xlsx en el mismo subdirectorio.
	(en todos los casos AAAAMMDDHHmm es exactamente el mismo que el del archivo de logs).
- Se loegea paso a paso cada acción del script. Pero también se registra al final del log:
	- Lista de conexiones fallidas a Servers-DB con su error, y lista de conexiones exitosas.
	- De las conexiones exitosas se registra la lista de CSV generados exitosamente, las lista de los no generados
	con sus respectivos errores.
- Se registra el resumen de resultados al final del proceso.
- Lo mismo que aparece en pantalla es lo que figurará en el log.


TO-DO:
- List generated files and subdirectories in kind of tree view (minor)
- List csv files that couldn't be processed cause server-db connection fail
- Make a super class of DBconextion for several DB engines (MySQL, SQLite, Postgress...)
	- and the a subclass for every diff. engine
- Make a unic class of whole app, kind of CSV_list class that containd all methods
- Make static typed codfication (permit mypy check)
	- https://mypy.readthedocs.io/en/stable/getting_started.html#installing-and-running-mypy
- (Nice Pandas excersice), at the end of the process, ADD a column to the CSV_list.xlsx named 'DONE'
	- DONE col.: values 'ok' for succesfuly build files and 'NO' for those files that couldn't be generated
	- Rename this file like CSV_list_AAAAMMDDHHmm_done_err.xlsx if errors occurs or CSV...HHmm_done.xlsx if not
	- PLUS other col named 'ERROR' for those NO generated files rows
	- PLUS..



