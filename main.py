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
dias_meses = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
diccionario_data_frames = {}

#¿ Iterar para depurar columnas no necesarias y asignar DataFrames al diccionario de acuerdo al mes
for i in range(len(rutas)):
    data_frame_mes = pd.read_csv(rutas[i], sep=',')
    datos_mes = data_frame_mes.drop(columns=['codigoSerial',
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
    datos_mes['Fecha_Hora'] = pd.to_datetime(datos_mes['Fecha_Hora'], format='%Y-%m-%d %H:%M:%S')
    datos_mes.set_index('Fecha_Hora', inplace=True)
    diccionario_data_frames[meses[i]] = datos_mes


def validar_datos():
    """Esta funcion itera sobre los meses y dias del año 2017 para validar la cantidad de datos erroneos en PM2.5 y elimina las filas que contienen dichos datos."""
    for mes in meses:
        for i in range(dias_meses[meses.index(mes)]):
            if i!=dias_meses[0]:
                if i==0 or i==1: # Controlar que no haya duplicados en los dias iniciales
                    fecha_busqueda_inicio = f"2017-{str(meses.index(mes)+1).zfill(2)}-{str(i+1).zfill(2)} 01:00:00"
                    fecha_busqueda_fin= f"2017-{str(meses.index(mes)+1).zfill(2)}-{str(i+2).zfill(2)} 00:00:00"
                    serie_conteo_datos = (diccionario_data_frames[mes].loc[fecha_busqueda_inicio:fecha_busqueda_fin]['calidad_pm25'].value_counts())
                    try:
                        if serie_conteo_datos[151] and serie_conteo_datos[151]>18:
                            print(f"El dia {i+1} del mes de {mes} tiene mas de 18 datos erroneos en PM2.5")
                            diccionario_data_frames[mes].drop(diccionario_data_frames[mes].loc[fecha_busqueda_inicio:fecha_busqueda_fin].index, inplace=True)  #Eliminar la fila problemática
                    except KeyError:
                        pass
                else:
                    fecha_busqueda_inicio = f"2017-{str(meses.index(mes)+1).zfill(2)}-{str(i).zfill(2)} 01:00:00"
                    fecha_busqueda_fin = f"2017-{str(meses.index(mes)+1).zfill(2)}-{str(i+1).zfill(2)} 00:00:00"
                    serie_conteo_datos = (diccionario_data_frames[mes].loc[fecha_busqueda_inicio:fecha_busqueda_fin]['calidad_pm25'].value_counts())
                    try:
                        if serie_conteo_datos[151] and serie_conteo_datos[151]>18:
                            print(f"El dia {i+1} del mes de {mes} tiene mas de 18 datos erroneos en PM2.5")
                            diccionario_data_frames[mes].drop(diccionario_data_frames[mes].loc[fecha_busqueda_inicio:fecha_busqueda_fin].index, inplace=True) #Eliminar la fila problemática
                    except KeyError:
                        pass

print('ANTES DE DEPURAR DATOS')
validar_datos()
print('DESPUES DE DEPURAR DATOS')
validar_datos()