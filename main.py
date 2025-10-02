import pandas as pd

#¿ Rutas de los archivos CSV a leer 
rutas = ['./Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170101_20170131.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170201_20170228.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170301_20170331.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170401_20170430.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170501_20170531.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170601_20170630.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170701_20170731.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170801_20170831.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170901_20170930.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20171001_20171031.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20171101_20171130.csv',
         './Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20171201_20171231.csv']

#¿ Lista con meses y diccionario para almacenar los DataFrames
meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
               'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
diccionario_data_frames = {}

#¿ Depurar columnas no necesarias y asignar DataFrames al diccionario de acuerdo al mes
for i in range(len(rutas)):
    data_frame_mes = pd.read_csv(rutas[i], sep=',')
    diccionario_data_frames[meses[i]] = data_frame_mes.drop(columns=['codigoSerial',
                        'pm10','calidad_pm10',
                        'pm1','calidad_pm1',
                        'no','calidad_no',
                        'no2','calidad_no2',
                        'nox','calidad_nox',
                        'co','calidad_co',
                        'so2','calidad_so2',
                        'pst','calidad_pst',
                        'dviento_ssr','calidad_dviento_ssr',
                        'haire10_ssr','calidad_haire10_ssr',
                        'p_ssr','calidad_p_ssr',
                        'rglobal_ssr','calidad_rglobal_ssr',
                        'vviento_ssr','calidad_vviento_ssr',
                        ])

#¿ Corregir fechas del día anterior
"""
for fecha in diccionario_data_frames['febrero']['Fecha_Hora']:
    if fecha[-8:-6] == '00':
        print(fecha)
"""

#¿ Funcion para detectar el porcentaje de datos erroneos en PM2.5
def detectar_porcentaje_erroneos(mes):
    erroneos = float(diccionario_data_frames[mes]['calidad_pm25'].value_counts()[1.0])/float(diccionario_data_frames[mes]['calidad_pm25'].count())
    erroneos = round(1- erroneos,2) #Hallar porcentaje de erróneos
    return erroneos 


for mes in meses:
    print(f"{mes}: {detectar_porcentaje_erroneos(mes)*100} %")
    if detectar_porcentaje_erroneos(mes) > 0.3:
        print(diccionario_data_frames[mes]['calidad_pm25'].value_counts())
    print('---  ---')