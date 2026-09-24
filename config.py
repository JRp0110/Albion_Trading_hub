# config.py

BASE_URL = "https://west.albion-online-data.com/api/v2/stats/prices"

CIUDADES = ["Thetford", "Martlock", "Lymhurst", "Bridgewatch", "Fort Sterling", "Caerleon", "Brecilien"]

TAX_RATE_BM = 0.08  # Impuesto del Mercado Negro (8%)

# 1. Familias de equipamiento completas (Combate, Capas de Facción, Recolección)
FAMILIAS_EQUIPO = {
    "BAG": "Bolsa",
    "CAPE": "Capa Base",
    
    # Capas de Facción y Ciudades
    "CAPE_THETFORD": "Capa de Thetford",
    "CAPE_LYMHURST": "Capa de Lymhurst",
    "CAPE_FORSTERLING": "Capa de Fort Sterling",
    "CAPE_BRIDGEWATCH": "Capa de Bridgewatch",
    "CAPE_MARTLOCK": "Capa de Martlock",
    "CAPE_CAERLEON": "Capa de Caerleon",
    "CAPE_UNDEAD": "Capa de No-Muerto",
    "CAPE_KEEPER": "Capa de Guardián",
    "CAPE_DEMON": "Capa de Demonio",
    "CAPE_AVALON": "Capa de Avalón",

    # Equipos de Recolección y Mochilas
    "ARMOR_CLOTH_HARVESTER": "Túnica de Recolector de Fibras",
    "HEAD_CLOTH_HARVESTER": "Capucha de Recolector de Fibras",
    "SHOES_CLOTH_HARVESTER": "Zapatos de Recolector de Fibras",
    "BACKPACK_HARVESTER": "Mochila de Recolector de Fibras",

    "ARMOR_LEATHER_SKINNER": "Chaqueta de Peletero",
    "HEAD_LEATHER_SKINNER": "Capucha de Peletero",
    "SHOES_LEATHER_SKINNER": "Zapatos de Peletero",
    "BACKPACK_SKINNER": "Mochila de Peletero",

    "ARMOR_PLATE_MINER": "Armadura de Minero",
    "HEAD_PLATE_MINER": "Casco de Minero",
    "SHOES_PLATE_MINER": "Botas de Minero",
    "BACKPACK_MINER": "Mochila de Minero",

    # Armaduras y Armas Populares
    "ARMOR_CLOTH_CLERIC": "Túnica de Clérigo",
    "ARMOR_LEATHER_MERCENARY": "Chaqueta de Mercenario",
    "ARMOR_LEATHER_ASSASSIN": "Chaqueta de Asesino",
    "ARMOR_PLATE_SOLDIER": "Armadura de Soldado",
    "HEAD_CLOTH_CLERIC": "Hábito de Clérigo",
    "SHOES_LEATHER_MERCENARY": "Zapatos de Mercenario",
    "SHOES_PLATE_SOLDIER": "Botas de Soldado",
    "MAIN_AXE": "Hacha de Batalla",
    "MAIN_SWORD": "Espada Ancha",
    "2H_BOW": "Arco (Base)",
    "2H_WARBOW": "Arco de Guerra",
    "2H_SKULLORB_HELL": "Calavera Maldita"
}

# 2. Monturas específicas
MONTURAS_ESPECIFICAS = {
    "T3_MOUNT_HORSE": "Caballo de Monta T3",
    "T4_MOUNT_HORSE": "Caballo de Monta T4",
    "T5_MOUNT_HORSE": "Caballo de Monta T5",
    "T6_MOUNT_HORSE": "Caballo de Monta T6",
    "T7_MOUNT_HORSE": "Caballo de Monta T7",
    "T8_MOUNT_HORSE": "Caballo de Monta T8",
    
    "T4_MOUNT_ARMOREDHORSE": "Caballo Acorazado T4",
    "T5_MOUNT_ARMOREDHORSE": "Caballo Acorazado T5",
    "T6_MOUNT_ARMOREDHORSE": "Caballo Acorazado T6",
    "T7_MOUNT_ARMOREDHORSE": "Caballo Acorazado T7",
    "T8_MOUNT_ARMOREDHORSE": "Caballo Acorazado T8",
    
    "T3_MOUNT_OX": "Buey de Carga T3",
    "T4_MOUNT_OX": "Buey de Carga T4",
    "T5_MOUNT_OX": "Buey de Carga T5",
    "T6_MOUNT_OX": "Buey de Carga T6",
    "T7_MOUNT_OX": "Buey de Carga T7",
    "T8_MOUNT_OX": "Buey de Carga T8",
    
    "T4_MOUNT_STAG": "Ciervo",
    "T5_MOUNT_GIANTSTAG": "Ciervo Gigante",
    "T5_MOUNT_BOAR": "Jabalí Ensillado",
    "T6_MOUNT_SWAMPDRAGON": "Lagarto de Pantano",
    "T6_MOUNT_DIREBEAR": "Oso Pardo (Grizzly)",
    "T8_MOUNT_WINTERBEAR": "Oso de Invierno Ensillado"
}

# 3. Materiales de encantamiento (Runas, Almas, Reliquias)
def generar_lista_materiales():
    mats = []
    for tier in range(4, 9):
        mats.extend([f"T{tier}_RUNE", f"T{tier}_SOUL", f"T{tier}_RELIC"])
    return mats

MATERIALES_IDS = generar_lista_materiales()

def generar_catalogo_items():
    items = []
    # Generar combinaciones de Tiers y Encantamientos (.1 a .3 para flipping)
    for tier in range(4, 9):
        for clave in FAMILIAS_EQUIPO.keys():
            items.append(f"T{tier}_{clave}")
            for enc in range(1, 4):
                items.append(f"T{tier}_{clave}@{enc}")
                
    # Agregar monturas
    for item_montura in MONTURAS_ESPECIFICAS.keys():
        items.append(item_montura)
            
    return items

ITEMS_TO_CHECK = generar_catalogo_items() + MATERIALES_IDS

def obtener_nombre_es(item_id):
    if item_id in MONTURAS_ESPECIFICAS:
        return MONTURAS_ESPECIFICAS[item_id]
    if "RUNE" in item_id:
        t = item_id.split('_')[0]
        return f"Runa {t}"
    if "SOUL" in item_id:
        t = item_id.split('_')[0]
        return f"Alma {t}"
    if "RELIC" in item_id:
        t = item_id.split('_')[0]
        return f"Reliquia {t}"
        
    partes = item_id.split('@')
    base = partes[0]
    encantamiento = f".{partes[1]}" if len(partes) > 1 else ".0"
    tier = base.split('_')[0]
    clave_familia = "_".join(base.split('_')[1:])
    nombre_base = FAMILIAS_EQUIPO.get(clave_familia, clave_familia)
    return f"{nombre_base} {tier}{encantamiento}"