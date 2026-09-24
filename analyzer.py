import pandas as pd
from config import SOURCE_CITY, TARGET_CITY, TAX_RATE, obtener_nombre_es

def analyze_margins(raw_data):
    if not raw_data:
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)
    df = df[(df['sell_price_min'] > 0) | (df['buy_price_max'] > 0)]

    df_source = df[df['city'] == SOURCE_CITY][['item_id', 'quality', 'sell_price_min']]
    df_source.rename(columns={'sell_price_min': 'precio_compra'}, inplace=True)

    df_bm = df[df['city'] == TARGET_CITY][['item_id', 'quality', 'buy_price_max']]
    df_bm.rename(columns={'buy_price_max': 'precio_venta_bm'}, inplace=True)

    df_merged = pd.merge(df_source, df_bm, on=['item_id', 'quality'], how='inner')

    nombres_calidad = {1: 'Normal', 2: 'Bueno', 3: 'Sobresaliente', 4: 'Excelente', 5: 'Obra Maestra'}
    df_merged['calidad'] = df_merged['quality'].map(nombres_calidad)

    df_merged = df_merged[(df_merged['precio_compra'] > 0) & (df_merged['precio_venta_bm'] > 0)]

    df_merged['ingreso_neto'] = df_merged['precio_venta_bm'] * (1 - TAX_RATE)
    df_merged['ganancia_neta'] = df_merged['ingreso_neto'] - df_merged['precio_compra']
    df_merged['roi_%'] = (df_merged['ganancia_neta'] / df_merged['precio_compra']) * 100

    df_merged = df_merged.round({'ingreso_neto': 0, 'ganancia_neta': 0, 'roi_%': 2})
    df_merged.sort_values(by='roi_%', ascending=False, inplace=True)

    oportunidades = df_merged[df_merged['ganancia_neta'] > 0].copy()
    
    # Aplicar la traducción dinámica de nombres
    oportunidades['nombre'] = oportunidades['item_id'].apply(obtener_nombre_es)
    
    return oportunidades