import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from windrose import WindroseAxes
from matplotlib import cm



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
    print(f"Se corrigieron los datos para {parametro} y la varaible: {variable}")

#¿ Llamada a la función para validar y limpiar los datos para el parámetro deseado
validar_datos(parametro='calidad_pm25', variable='pm25') #? Para calidad pm2.5
validar_datos(parametro='calidad_pliquida_ssr', variable='pliquida_ssr') #? Para calidad de precipitación líquida
validar_datos(parametro='calidad_taire10_ssr',variable='taire10_ssr') #? Para calidad de temperatura del aire a 10m
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


def graficar_calidad_25_diario():
    """Esta función grafica el promedio diario de PM2.5 a lo largo del año 2017."""
    df_diario = data_frame_anual.resample('D')['pm25_ref'].mean().interpolate(method='linear')
    plt.figure(figsize=(12, 6))
    plt.plot(df_diario.index, df_diario, marker='o', linestyle='-', color=BLUE, markersize=4, label='PM2.5 (promedio diario)')
    plt.title('Promedio diario de PM2.5 en 2017', fontsize=16)
    plt.xlabel('Fecha', fontsize=14)
    plt.ylabel('Concentración de PM2.5 (µg/m³)', fontsize=14)
    plt.axhline(y=37, color='r', linestyle='--', label='Normativa (37 µg/m³)')
    plt.grid(True)
    plt.legend(fontsize=12, loc="upper right") 
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('promedio_diario_pm25.png')
    print('Se generó el gráfico de promedio diario')
    #plt.show()


def graficar_calidad_25_mensual():
    """Esta función grafica el promedio mensual de PM2.5 a lo largo del año 2017."""
    # Calcular el promedio mensual
    df_mensual = data_frame_anual.resample('ME').mean()
    
    # Datos para apilar: pm25
    pm25 = df_mensual['pm25_ref']
    
    # Crear gráfico de barras apiladas
    plt.figure(figsize=(12, 8))
    plt.bar(meses, pm25, label='PM2.5', color=COLOR_PM25, alpha=0.7)

    # Línea de normativa para PM2.5 (25 µg/m³) como referencia
    plt.axhline(y=25, color='r', linestyle='--', label='Normativa PM2.5 (25 µg/m³)')

    plt.title('Promedio mensual de PM2.5 en 2017', fontsize=16)
    plt.xlabel('Meses', fontsize=14)
    plt.ylabel('Concentración de PM2.5 (µg/m³)', fontsize=14)
    plt.legend(fontsize=12, loc="upper right") 
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('promedio_mensual_pm25.png')
    print('Se generó el gráfico de promedio mensual')
    #plt.show()


def graficar_promedio_anual_apilado():
    """Esta función grafica el promedio anual de PM2.5 en 2017 como una sola barra."""
    # Calcular el promedio anual
    promedio_anual_pm25 = data_frame_anual['pm25_ref'].mean()

    # Crear un gradiente de colores para la barra
    
    cmap = cm.colors.LinearSegmentedColormap.from_list('custom_gradient', COLORES_GRADIENTE, N=100)
    norm = plt.Normalize(0, promedio_anual_pm25)
    colores = cmap(norm(np.linspace(0, promedio_anual_pm25, 100)))

    # Crear gráfico de barra con degradado (dividir en 100 segmentos)
    plt.figure(figsize=(6, 6))
    y_inferior = 0
    for i in range(99):  # 99 segmentos para cubrir 100 pasos
        altura = (promedio_anual_pm25 / 100)
        plt.bar(['2017'], [altura], bottom=[y_inferior], color=[colores[i]], alpha=0.7, edgecolor='none')
        y_inferior += altura
    
    # Ajustar el último segmento para completar la altura exacta
    plt.bar(['2017'], [promedio_anual_pm25 - y_inferior], bottom=[y_inferior], color=[colores[99]], alpha=0.7, edgecolor='none')
    
    # Línea de normativa como referencia
    plt.axhline(y=25, color='r', linestyle='--', label='Normativa PM2.5 (25 µg/m³)')
    
    plt.title('Promedio anual de PM2.5 en 2017', fontsize=16)
    plt.xlabel('Año', fontsize=14)
    plt.ylabel('Concentración de PM2.5 (µg/m³)', fontsize=14)
    plt.legend(fontsize=12, loc="upper right") 
    plt.ylim(0, max(40, promedio_anual_pm25 * 1.2))  # Ajustar límite Y para visibilidad
    plt.tight_layout()
    plt.savefig('promedio_anual_pm25.png')
    print('Se generó el gráfico anual apilado')
    #plt.show()


def graficar_ciclo_diurno_pm25():
    """
    Grafica el ciclo diurno (0-23 horas) de PM2.5 en 2017:
    - Promedio diurno general
    - Día con mayor promedio diario
    - Día con menor promedio diario
    """

    # Asegurar columna "hora"
    data_frame_anual['hora'] = data_frame_anual.index.hour

    # Promedio general por hora (ciclo diurno)
    promedio_diurno = data_frame_anual.groupby('hora')['pm25_ref'].mean()

    # Promedio diario para identificar día máximo y mínimo
    promedio_diario = data_frame_anual.resample('D')['pm25_ref'].mean()
    dia_max = promedio_diario.idxmax().date()
    dia_min = promedio_diario.idxmin().date()

    # Extraer datos de esos días
    pm25_dia_max = data_frame_anual[data_frame_anual.index.date == dia_max].groupby('hora')['pm25_ref'].mean()
    pm25_dia_min = data_frame_anual[data_frame_anual.index.date == dia_min].groupby('hora')['pm25_ref'].mean()

    # Reindexar para asegurar 24 horas (0–23)
    horas = range(24)
    pm25_dia_max = pm25_dia_max.reindex(horas).interpolate().bfill().ffill()
    pm25_dia_min = pm25_dia_min.reindex(horas).interpolate().bfill().ffill()


    # Crear gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(promedio_diurno.index, promedio_diurno, label="Promedio diurno", color=BLUE, linewidth=2)
    plt.plot(pm25_dia_max.index, pm25_dia_max, label=f"Día máximo ({dia_max})", color=RED, linewidth=2)
    plt.plot(pm25_dia_min.index, pm25_dia_min, label=f"Día mínimo ({dia_min})", color=GREEN, linewidth=2)

    # Decoración
    plt.title("Ciclo diurno de PM2.5 en 2017", fontsize=16)
    plt.xlabel("Hora del día", fontsize=14)
    plt.ylabel("Concentración de PM2.5 (µg/m³)", fontsize=14)
    plt.xticks(range(0, 24))
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=12, loc="upper right") 
    plt.tight_layout()
    plt.savefig('ciclo_diurno_pm25.png')
    print('Se generó el gráfico de ciclo diurno')
    #plt.show()


def graficar_ciclo_semanal_pm25_precipitacion():
    """
    Grafica el ciclo semanal promedio de PM2.5 y la distribución porcentual
    de la precipitación (pliquida_ssr) por día de la semana.
    - Eje Y izquierdo: concentración promedio de PM2.5 (µg/m³)
    - Eje Y derecho: porcentaje de precipitación (%)
    """

    # Asegurar columna "dia_semana" (0=Lunes, 6=Domingo)
    data_frame_anual['dia_semana'] = data_frame_anual.index.dayofweek

    # Promedio de PM2.5 por día de la semana
    pm25_semanal = data_frame_anual.groupby('dia_semana')['pm25_ref'].mean()

    # Precipitación total por día de la semana
    precipitacion_semanal = data_frame_anual.groupby('dia_semana')['pliquida_ssr'].sum()

    # Calcular porcentajes (frecuencia relativa)
    precipitacion_porcentaje = (precipitacion_semanal / precipitacion_semanal.sum()) * 100

    # Etiquetas para el eje X
    dias_semana_labels = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    # Crear gráfico con dos ejes Y
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Crear segundo eje Y para precipitación
    ax2 = ax1.twinx()
    ax2.bar(dias_semana_labels, precipitacion_porcentaje, color=PRECIPITACION, alpha=0.6, label='Precipitación (%)', zorder=1)
    ax2.set_ylabel('Precipitación relativa (%)', color='black', fontsize=14)
    ax2.tick_params(axis='y', labelcolor='black')
    
    
    # asegurar que ax1 (línea) esté por encima de ax2
    ax1.set_zorder(3)   # eje de las líneas por encima
    ax2.set_zorder(2)   # eje de las barras por debajo
    ax1.patch.set_visible(False)   # o ax1.set_facecolor('none')

    # Gráfico de PM2.5 (línea, eje Y izquierdo)
    ax1.plot(dias_semana_labels, pm25_semanal, color=BLUE, marker='o', linewidth=2, label='PM2.5 promedio', zorder=4)
    ax1.set_xlabel('Día de la semana', fontsize=14)
    ax1.set_ylabel('Concentración de PM2.5 (µg/m³)', color='black', fontsize=14)
    ax1.tick_params(axis='y', labelcolor='black')

    

    # Título y leyenda
    fig.suptitle('Ciclo semanal de PM2.5 y distribución de precipitación en 2017', fontsize=16)

    # Leyenda combinada
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    leg = ax2.legend(h1 + h2, l1 + l2, loc='upper right', fontsize=12, frameon=True)
    ax2.add_artist(leg)
    plt.tight_layout()
    plt.savefig('ciclo_semanal_pm25_precipitacion.png')
    #plt.show()
    print('Se generó el gráfico de ciclo semanal con frecuencia de precipitación')

def graficar_rosa_vientos_anual():
    """
    Grafica la rosa de los vientos anual (frecuencia y velocidad)
    a partir de las columnas 'dviento_ssr' (dirección) y 'vviento_ssr' (velocidad)
    """

    #  Crear figura y ejes tipo Windrose
    fig = plt.figure(figsize=(8, 8))
    ax = WindroseAxes.from_ax()

    #  Crear la rosa del viento por rangos de velocidad
    ax.bar(data_frame_anual['dviento_ssr'],
           data_frame_anual['vviento_ssr'],
           bins=[0, 1, 5, 8,10],     # rangos de velocidad (m/s)
           cmap=plt.cm.viridis,              # escala de color
           normed=True,                      # porcentaje (%)
           opening=0.8,                      # separación entre barras
           edgecolor='white')
    
    # Mostrar frecuencias en porcentaje en los círculos ---
    valores, etiquetas = plt.yticks()
    ax.set_rgrids(valores, [f"{v:.0f}%" for v in valores], angle=60, fontsize=10) # Obtener porcentajes a partir de tamaño datos
    for text in ax.yaxis.get_ticklabels(): # Agregar buffer blanco para mejor visibilidad
        text.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.8, pad=2))

    # Ajustes finales
    ax.set_theta_zero_location('N')   # 0° apunta al norte
    ax.set_theta_direction(-1)        # sentido horario
    ax.set_title('Rosa de los vientos 2017', fontsize=14, pad=20)
    ax.legend(title='Velocidad (m/s)', loc='lower right', fontsize=10, frameon=True)
    plt.savefig('rosa_vientos.png')
    #plt.show()
    print('Se generó el gráfico de rosa de los vientos')

#¿ Llamadas a las funciones para generar los gráficos

graficar_calidad_25_diario()
graficar_calidad_25_mensual()
graficar_promedio_anual_apilado()
graficar_ciclo_diurno_pm25()
graficar_ciclo_semanal_pm25_precipitacion()
graficar_rosa_vientos_anual()
