# services.py
import pandas as pd
from config import TAX_RATE_BM, obtener_nombre_es, FAMILIAS_EQUIPO
from api_client import AlbionApiClient

class MarketAnalysisService:
    
    @staticmethod
    def analizar_arbitraje_bm(source_city, items_list):
        """Calcula oportunidades de ganancia mediante transporte hacia el Mercado Negro."""
        raw_data = AlbionApiClient.fetch_market_data(items_list, [source_city, "Black Market"])
        if not raw_data:
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)
        df = df[(df['sell_price_min'] > 0) | (df['buy_price_max'] > 0)]

        df_source = df[df['city'] == source_city][['item_id', 'quality', 'sell_price_min']]
        df_source.rename(columns={'sell_price_min': 'precio_compra'}, inplace=True)

        df_bm = df[df['city'] == "Black Market"][['item_id', 'quality', 'buy_price_max']]
        df_bm.rename(columns={'buy_price_max': 'precio_venta_bm'}, inplace=True)

        df_merged = pd.merge(df_source, df_bm, on=['item_id', 'quality'], how='inner')

        nombres_calidad = {1: 'Normal', 2: 'Bueno', 3: 'Sobresaliente', 4: 'Excelente', 5: 'Obra Maestra'}
        df_merged['calidad'] = df_merged['quality'].map(nombres_calidad)

        df_merged = df_merged[(df_merged['precio_compra'] > 0) & (df_merged['precio_venta_bm'] > 0)]

        df_merged['ingreso_neto'] = df_merged['precio_venta_bm'] * (1 - TAX_RATE_BM)
        df_merged['ganancia_neta'] = df_merged['ingreso_neto'] - df_merged['precio_compra']
        df_merged['roi_%'] = (df_merged['ganancia_neta'] / df_merged['precio_compra']) * 100

        df_merged = df_merged.round({'ingreso_neto': 0, 'ganancia_neta': 0, 'roi_%': 2})
        df_merged.sort_values(by='roi_%', ascending=False, inplace=True)

        oportunidades = df_merged[df_merged['ganancia_neta'] > 0].copy()
        if not oportunidades.empty:
            oportunidades['nombre'] = oportunidades['item_id'].apply(obtener_nombre_es)

        return oportunidades

    @staticmethod
    def obtener_tabla_materiales_caerleon(tiers_seleccionados):
        """Genera la tabla de referencia de materiales filtrada por los Tiers elegidos."""
        mats_a_buscar = []
        for tier in tiers_seleccionados:
            mats_a_buscar.extend([f"T{tier}_RUNE", f"T{tier}_SOUL", f"T{tier}_RELIC"])
            
        raw_data = AlbionApiClient.fetch_market_data(mats_a_buscar, ["Caerleon"], qualities="1")
        if not raw_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(raw_data)
        df = df[df['city'] == "Caerleon"][['item_id', 'sell_price_min']]
        
        mat_dict = {}
        for _, row in df.iterrows():
            mat_dict[row['item_id']] = row['sell_price_min']
            
        filas = []
        for tier in tiers_seleccionados:
            t_str = f"T{tier}"
            filas.append({
                "Tier": f"Tier {tier}",
                "Runas (.1)": mat_dict.get(f"{t_str}_RUNE", 0),
                "Almas (.2)": mat_dict.get(f"{t_str}_SOUL", 0),
                "Reliquias (.3)": mat_dict.get(f"{t_str}_RELIC", 0)
            })
        return pd.DataFrame(filas)

    @staticmethod
    def obtener_cantidad_materiales(base_item_id):
        """Define la cantidad exacta de material según la parte del equipo (sin importar el Tier)."""
        if "2H_" in base_item_id:
            return 384  # Armas principales de dos manos
        elif "MAIN_" in base_item_id:
            return 288  # Armas principales de una mano
        elif "ARMOR_" in base_item_id:
            return 192  # Túnicas (Armaduras de cuerpo)
        elif "BAG" in base_item_id:
            return 192  # Bolsas
        elif "CAPE" in base_item_id:
            return 96   # Capas
        elif "HEAD_" in base_item_id:
            return 96   # Cascos
        elif "SHOES_" in base_item_id:
            return 96   # Botas
        # Para armas secundarias u otros ítems base por defecto
        return 96

    @staticmethod
    def analizar_flipping_caerleon(tiers_seleccionados, ordenar_por="Mayor % de ROI (Rentabilidad)"):
        """Calcula el flipping interno en Caerleon usando las cantidades exactas por parte de equipo."""
        items_a_consultar = []
        mats_a_consultar = []
        
        for tier in tiers_seleccionados:
            mats_a_consultar.extend([f"T{tier}_RUNE", f"T{tier}_SOUL", f"T{tier}_RELIC"])
            for clave in FAMILIAS_EQUIPO.keys():
                items_a_consultar.append(f"T{tier}_{clave}")
                for enc in range(1, 4):
                    items_a_consultar.append(f"T{tier}_{clave}@{enc}")
                    
        all_ids = items_a_consultar + mats_a_consultar
        raw_data = AlbionApiClient.fetch_market_data(all_ids, ["Caerleon", "Black Market"], qualities="1")
        if not raw_data:
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)
        
        df_caerleon = df[df['city'] == "Caerleon"].set_index('item_id')['sell_price_min'].to_dict()
        df_bm = df[(df['city'] == "Black Market") & (df['quality'] == 1)].set_index('item_id')['buy_price_max'].to_dict()

        resultados = []

        for tier in tiers_seleccionados:
            t_str = f"T{tier}"
            for clave in FAMILIAS_EQUIPO.keys():
                base_id = f"{t_str}_{clave}"
                precio_base = df_caerleon.get(base_id, 0)
                if precio_base <= 0:
                    continue
                    
                cant_mat = MarketAnalysisService.obtener_cantidad_materiales(base_id)

                for enc in range(1, 4):
                    enc_id = f"{base_id}@{enc}"
                    precio_bm = df_bm.get(enc_id, 0)
                    if precio_bm <= 0:
                        continue

                    if enc == 1:
                        mat_id = f"{t_str}_RUNE"
                    elif enc == 2:
                        mat_id = f"{t_str}_SOUL"
                    else:
                        mat_id = f"{t_str}_RELIC"

                    precio_mat = df_caerleon.get(mat_id, 0)
                    costo_materiales = cant_mat * precio_mat
                    costo_total = precio_base + costo_materiales

                    ingreso_neto = precio_bm * (1 - TAX_RATE_BM)
                    ganancia = ingreso_neto - costo_total
                    roi = (ganancia / costo_total) * 100 if costo_total > 0 else 0

                    if ganancia > 0:
                        nombre_item = obtener_nombre_es(enc_id)
                        resultados.append({
                            "Ítem a Vender": nombre_item,
                            "Precio Base Caerleon": precio_base,
                            "Costo Materiales": costo_materiales,
                            "Costo Total Inversión": costo_total,
                            "Precio BM (Orden Compra)": precio_bm,
                            "Profit (Ganancia Neta)": int(ganancia),
                            "ROI %": round(roi, 2)
                        })

        df_res = pd.DataFrame(resultados)
        if not df_res.empty:
            if ordenar_por == "Mayor Profit Neto (Plata)":
                df_res.sort_values(by="Profit (Ganancia Neta)", ascending=False, inplace=True)
            else:
                df_res.sort_values(by="ROI %", ascending=False, inplace=True)
        return df_res