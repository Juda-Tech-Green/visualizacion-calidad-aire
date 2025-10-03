import pandas as pd
import matplotlib.pyplot as plt

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
    datos_mes = data_frame_mes.drop(columns=[
                        'codigoSerial',
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


def validar_datos(parametro):
    """Esta función itera sobre los meses, días y horas del año 2017 para validar datos erróneos del parámetro proporcionado y elimina las filas correspondientes a esas horas."""
    for mes in meses:
        mes_num = meses.index(mes) + 1
        for dia in range(1, dias_meses[meses.index(mes)] + 1):
            for hora in range(24): 
                fecha_busqueda_inicio = f"2017-{str(mes_num).zfill(2)}-{str(dia).zfill(2)} {str(hora).zfill(2)}:00:00"
                if hora == 23:
                    fecha_busqueda_fin = f"2017-{str(mes_num).zfill(2)}-{str(dia).zfill(2)} {str(0).zfill(2)}:00:00"
                else:
                    fecha_busqueda_fin = f"2017-{str(mes_num).zfill(2)}-{str(dia).zfill(2)} {str(hora+1).zfill(2)}:00:00"
                try:
                    serie_conteo_datos = diccionario_data_frames[mes].loc[fecha_busqueda_inicio:fecha_busqueda_fin][parametro].value_counts()
                    if serie_conteo_datos[151]:
                        diccionario_data_frames[mes].drop(diccionario_data_frames[mes].loc[fecha_busqueda_inicio:fecha_busqueda_fin].index, inplace=True)
                except KeyError:
                    pass
        #print(mes)
        #print(diccionario_data_frames[mes][parametro].value_counts())
        #print('...')


#¿ Llamada a la función para validar y limpiar los datos
validar_datos('calidad_pm25') #? Para calidad pm2.5
validar_datos('calidad_pliquida_ssr') #? Para calidad de precipitación líquida
validar_datos('calidad_taire10_ssr') #? Para calidad de temperatura del aire a 10m

#¿ Concatenar todos los DataFrames mensuales en uno anual y ordenar por índice
data_frame_anual = pd.concat([diccionario_data_frames[mes] for mes in meses], axis=0)
data_frame_anual.sort_index(inplace=True)



def graficar_pm_25():
    """Esta función grafica la concentración horaria de PM2.5 a lo largo del año 2017."""
    plt.figure(figsize=(12, 6))
    plt.plot(data_frame_anual.index, data_frame_anual['pm25'], marker='o', linestyle='-', color='b', markersize=2)
    plt.title('Concentración horaria de PM2.5 en 2017', fontsize=16)
    plt.xlabel('Fecha', fontsize=14)
    plt.ylabel('Concentración de PM2.5 (µg/m³)', fontsize=14)
    plt.axhline(y=37, color='r', linestyle='--', label='Normativa (37 µg/m³)')
    plt.grid(True)
    plt.legend(['PM2.5'], fontsize=12)
    plt.tight_layout()

    plt.show()


def graficar_precipitacion():
    """Esta función grafica la precipitación líquida diaria a lo largo del año 2017."""

    plt.figure(figsize=(12, 6))
    plt.bar(data_frame_anual.index, data_frame_anual['pliquida_ssr'], color='c')
    plt.title('Precipitación líquida horaria en 2017', fontsize=16)
    plt.xlabel('Fecha', fontsize=14)
    plt.ylabel('Precipitación líquida (mm)', fontsize=14)
    plt.grid(True)
    plt.tight_layout()

    plt.show()

graficar_pm_25()
graficar_precipitacion()


