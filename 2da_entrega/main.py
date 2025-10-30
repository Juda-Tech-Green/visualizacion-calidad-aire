import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from windrose import WindroseAxes
from matplotlib import cm



#¿ Rutas de los archivos CSV a leer
rutas = ['../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170101_20170131.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170201_20170228.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170301_20170331.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170401_20170430.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170501_20170531.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170601_20170630.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170701_20170731.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170801_20170831.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20170901_20170930.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20171001_20171031.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20171101_20171130.csv',
         '../Datos_Calidad_Aire_Trabajo_1/estacion_data_calidadaire_38_20171201_20171231.csv']


#¿ Lista con meses y diccionario para almacenar los DataFrames
meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
               'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dias_meses = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
diccionario_data_frames = {}

#¿ Parámetros de referencia
Presion_referencia = 1013.25 #hPa a nivel del mar
Temperatura_referencia = 298.15 # 25°C en Kelvin
Presion_Local = 850 # hPa Presion local de Medellín

#¿ Variables con colores para gráficos
BLUE = '#0046FF'
RED = '#DD0303'
GREEN = '#08CB00'
PRECIPITACION = '#7ADAA5'
# Colores personalizados para cada mes
COLOR_PM25 = ['#FF5733', '#33FF57', '#5733FF', '#FF33A1', '#33FFF6', '#F6FF33',
                '#A133FF', '#FF8C33', '#33FF8C', '#8C33FF', '#FF3333', '#33A1FF']
COLORES_GRADIENTE = ['#33FF57', '#FF8C33']


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
                        'haire10_ssr','calidad_haire10_ssr',
                        'p_ssr','calidad_p_ssr',
                        'rglobal_ssr','calidad_rglobal_ssr',
                        ])
    datos_mes['Fecha_Hora'] = pd.to_datetime(datos_mes['Fecha_Hora'], format='%Y-%m-%d %H:%M:%S')
    datos_mes.set_index('Fecha_Hora', inplace=True)
    diccionario_data_frames[meses[i]] = datos_mes


#¿ Función para validar y limpiar los datos
def validar_datos(parametro, variable):
    """
    Itera sobre los meses, días y horas del año 2017 para:
      - asignar NaN en 'variable' cuando 'parametro' = 151 (inválidos)
      - eliminar días con menos de 18 datos válidos en 'variable'
    """
    for mes in meses:
        mes_num = meses.index(mes) + 1

        # Paso 1: invalidar datos con flag 151
        for dia in range(1, dias_meses[meses.index(mes)] + 1):
            for hora in range(24):
                fecha_inicio = f"2017-{mes_num:02d}-{dia:02d} {hora:02d}:00:00"
                if hora == 23:
                    fecha_fin = f"2017-{mes_num:02d}-{dia:02d} 00:00:00"
                else:
                    fecha_fin = f"2017-{mes_num:02d}-{dia:02d} {hora+1:02d}:00:00"
                try:
                    serie_conteo = diccionario_data_frames[mes].loc[fecha_inicio:fecha_fin][parametro].value_counts()
                    if 151 in serie_conteo.index:
                        # En vez de borrar fila, asignamos NaN solo en la variable correspondiente
                        diccionario_data_frames[mes].loc[fecha_inicio:fecha_fin, variable] = np.nan
                except Exception:
                    continue

        # Paso 2: eliminar días con menos de 18 datos válidos en esa variable
        try:
            conteo_diario = diccionario_data_frames[mes].resample("D")[variable].count()
        except Exception:
            continue

        dias_invalidos = conteo_diario[conteo_diario < 18].index
        if len(dias_invalidos) == 0:
            continue

        try:
            # Asignar NaN solo en la variable de esos días incompletos
            mask = diccionario_data_frames[mes].index.normalize().isin(dias_invalidos.normalize())
            diccionario_data_frames[mes].loc[mask, variable] = np.nan
        except Exception:
            continue
    print(f"Se corrigieron los datos para {parametro} y la variable: {variable}")

#¿ Llamada a la función para validar y limpiar los datos para el parámetro deseado
validar_datos(parametro='calidad_pm25', variable='pm25') #? Para calidad pm2.5
validar_datos(parametro="calidad_dviento_ssr",variable="dviento_ssr") #? Para calidad de dirección de viento
validar_datos(parametro="calidad_vviento_ssr", variable="vviento_ssr") #? Para calidad de velocidad viento

#¿ Ajustar los datos a condiciones de referencia
def ajustar_pm25_condiciones_referencia(df, temp_col='taire10_ssr', pres_col=None):
    """
    Ajusta la concentración de PM2.5 a condiciones de referencia (25 °C, 1 atm).
    Usa la ley de los gases ideales.
    Parámetros:
        df: DataFrame con columnas de pm25, temperatura y (opcionalmente) presión.
        temp_col: nombre de la columna de temperatura (°C)
        pres_col: nombre de la columna de presión (hPa). Si None, se usa 1013.25 o valor estimado.
    Retorna:
        DataFrame con una nueva columna 'pm25_ref' (µg/m³ normalizado).
    """
    # Condiciones de referencia
    P_ref = Presion_referencia
    T_ref = Temperatura_referencia

    # Temperatura medida en Kelvin
    T = df[temp_col] + 273.15

    # Presión atmosférica local
    P = Presion_Local

    # Calcular concentración normalizada
    df['pm25_ref'] = df['pm25'] * (P / P_ref) * (T_ref / T)
    print('Se ajustaron los datos de pm 2.5 a condiciones de referencia')
    return df


#¿ Concatenar todos los DataFrames mensuales en uno anual y ordenar índice por fecha
data_frame_anual = pd.concat([diccionario_data_frames[mes] for mes in meses], axis=0)
data_frame_anual.sort_index(inplace=True)

#¿ Ajustar PM2.5 a condiciones de referencia
data_frame_anual = ajustar_pm25_condiciones_referencia(data_frame_anual, temp_col='taire10_ssr')

def graficar_rosa_vientos_dia_noche():
    """
    Genera dos rosas de los vientos:
       Día: 06:00–18:00
       Noche: 18:00–06:00
    usando 'dviento_ssr' (dirección) y 'vviento_ssr' (velocidad) del DataFrame global data_frame_anual.
    """

    # --- Preparar datos base ---
    df_viento = data_frame_anual[['dviento_ssr', 'vviento_ssr']].dropna()
    df_viento_sin_calmas = df_viento[df_viento['vviento_ssr'] > 0.3]

    # Extraer hora del índice
    df_viento_sin_calmas['hora'] = df_viento_sin_calmas.index.hour

    # Dividir en día (6–18) y noche (18–6)
    df_dia = df_viento_sin_calmas[(df_viento_sin_calmas['hora'] >= 6) & (df_viento_sin_calmas['hora'] < 18)]
    df_noche = df_viento_sin_calmas[(df_viento_sin_calmas['hora'] >= 18) | (df_viento_sin_calmas['hora'] < 6)]

    # --- figura con dos rosas ---
    fig = plt.figure(figsize=(14, 7))

    # Crear la rosa del viento por rangos de velocidad de Beaufort.
    conversion_ms = round(5 / 18, 3)
    intervalos_beaufort = [1 * conversion_ms, 5 * conversion_ms,
                           6 * conversion_ms, 11 * conversion_ms,
                           12 * conversion_ms]

    print(df_dia['d_viento_ssr'].mean())
    print('---------------------------')
    print(df_noche['d_viento_ssr'].mean())

    #  Rosa diurna
    ax1 = fig.add_subplot(1, 2, 1, projection='windrose')
    ax1.bar(df_dia['dviento_ssr'], df_dia['vviento_ssr'],
            bins=intervalos_beaufort,
            cmap=plt.cm.viridis, normed=True, opening=0.8, edgecolor='white')

    # Configurar orientación y etiquetas
    ax1.set_theta_zero_location('E')
    ax1.set_theta_direction(1)
    valores, _ = plt.yticks()
    ax1.set_rgrids(valores, [f"{v:.0f}%" for v in valores], angle=60, fontsize=9)
    for text in ax1.yaxis.get_ticklabels():
        text.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2))
    ax1.set_title("Vientos diurnos (06:00–18:00)", fontsize=13, pad=20)
    ax1.legend(title='Velocidad (m/s)', loc='lower right', fontsize=9, frameon=True)

    #  Rosa nocturna
    ax2 = fig.add_subplot(1, 2, 2, projection='windrose')
    ax2.bar(df_noche['dviento_ssr'], df_noche['vviento_ssr'],
            bins=intervalos_beaufort,
            cmap=plt.cm.viridis, normed=True, opening=0.8, edgecolor='white')

    ax2.set_theta_zero_location('E')
    ax2.set_theta_direction(1)
    valores, _ = plt.yticks()
    ax2.set_rgrids(valores, [f"{v:.0f}%" for v in valores], angle=60, fontsize=9)
    for text in ax2.yaxis.get_ticklabels():
        text.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2))
    ax2.set_title("Vientos nocturnos (18:00–06:00)", fontsize=13, pad=20)
    ax2.legend(title='Velocidad (m/s)', loc='lower right', fontsize=9, frameon=True)

    plt.suptitle("Rosas de los vientos 2017", fontsize=15, y=0.95)
    plt.tight_layout()
    print('Se generó el gráfico de rosa de vientos para día y noche')
    #plt.savefig("rosa_vientos_dia_noche.png")
    plt.show()



def graficar_rosa_vientos_anual():
    """
    Grafica la rosa de los vientos anual (frecuencia y velocidad)
    a partir de las columnas 'dviento_ssr' (dirección) y 'vviento_ssr' (velocidad)
    del DataFrame global 'data_frame_anual'.
    """

    # Filtrar valores válidos y descartar calmas

    df_viento = data_frame_anual[['dviento_ssr', 'vviento_ssr']].dropna()
    df_viento_sin_calmas = df_viento[df_viento['vviento_ssr']>0.3]

    #  Crear figura y ejes tipo Windrose
    fig = plt.figure(figsize=(8, 8))
    ax = WindroseAxes.from_ax()
    try:
        # Crear la rosa del viento por rangos de velocidad de Beaufort.
        conversion_ms = round(5/18,3)
        intervalos_beaufort = [1*conversion_ms, 5*conversion_ms,
                               6*conversion_ms, 11*conversion_ms,
                               12*conversion_ms]
        ax.bar(df_viento_sin_calmas['dviento_ssr'],
               df_viento_sin_calmas['vviento_ssr'],
               bins= intervalos_beaufort,     # rangos de velocidad (m/s)
               cmap=plt.cm.viridis,              # escala de color
               normed=True,                      # porcentaje (%)
               opening=0.8,                      # separación entre barras
               edgecolor='white')

        #  orientación
        ax.set_theta_zero_location('N')   # 0° apunta al norte
        ax.set_theta_direction(-1)        # sentido horario

        # Título y leyenda
        ax.set_title('Rosa de los vientos anual (2017)', fontsize=14, pad=20)
        ax.legend(title='Velocidad (m/s)', loc='upper right', fontsize=10, frameon=True)
        print('Se generó el gráfico de rosa de vientos para día y noche')
        plt.show()
    except ValueError:
        print(f'{ValueError.args}')
        pass

#graficar_rosa_vientos_anual()
graficar_rosa_vientos_dia_noche()