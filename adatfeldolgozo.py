#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# VÉGLEGES, EGYSÉGESÍTETT ADATFELDOLGOZÓ PIPELINE (DEFENZÍV LOGIKÁVAL)

import logging
from pathlib import Path
import sys
import pandas as pd

# Core modulok importálása a helyes útvonalról
try:
    current_dir = Path(__file__).resolve().parent
    core_path = current_dir / "core"
    if str(core_path) not in sys.path:
        sys.path.insert(0, str(core_path))
    from file_processor import FileProcessor
    from duplicate_handler import DuplicateHandler
except ImportError as e:
    print(f"❌ Kritikus hiba: Nem sikerült betölteni a core modulokat: {e}")
    sys.exit(1)

def main():
    """A teljes adatfeldolgozási láncot futtató fő függvény."""
    fp = FileProcessor()
    dh = DuplicateHandler(strategy="emergency_fix_v1")
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)])

    logging.info("-" * 50)
    logging.info("STEP 1: Fájlok beolvasása")
    logging.info("-" * 50)

    all_files = sorted(list(fp.input_dir.glob("*.csv")))
    if not all_files:
        logging.warning(f"Nincsenek feldolgozandó CSV fájlok a(z) '{fp.input_dir}' mappában.")
        sys.exit(0)

    all_dataframes = [(fp.load_csv_file(file_path), file_path.name) for file_path in all_files]
    
    logging.info("\n" + "-" * 50)
    logging.info("STEP 2: Adatkeretek validálása és normalizálása (fájlonként)")
    logging.info("-" * 50)

    standard_columns = ['Gyariszam', 'Azonosito', 'Kezdo_datum', 'Zaro_datum', 'Hatasos_ertek_kWh']
    
    column_map = {
        'gyáriszám': 'Gyariszam',
        'azonosító': 'Azonosito',
        'kezdő dátum': 'Kezdo_datum',
        'záró dátum': 'Zaro_datum',
        'hatásos érték [kwh]': 'Hatasos_ertek_kWh'
    }

    normalized_dfs = []
    for df, filename in all_dataframes:
        if df is None:
            continue

        original_columns = df.columns
        rename_map = {}
        found_cols = set()

        for col in original_columns:
            clean_col = str(col).strip().lower().replace('_', ' ')
            if clean_col in column_map:
                standard_name = column_map[clean_col]
                rename_map[col] = standard_name
                found_cols.add(standard_name)
        
        if set(standard_columns).issubset(found_cols):
            normalized_df = df.rename(columns=rename_map)
            normalized_dfs.append(normalized_df[standard_columns])
            logging.info(f"✅ '{filename}' sikeresen normalizálva.")
        else:
            logging.warning(f"⚠️ '{filename}' kihagyva: hiányzó oszlopok. Szükséges: {standard_columns}, Talált: {list(found_cols)}")

    if not normalized_dfs:
        logging.critical("❌ Egyetlen CSV fájlt sem sikerült sikeresen normalizálni. A folyamat leáll.")
        sys.exit(1)

    combined_df = pd.concat(normalized_dfs, ignore_index=True)
    logging.info(f"Normalizált adatok összefűzve: {len(combined_df)} sor.")

    logging.info("\n" + "-" * 50)
    logging.info("STEP 3: Adattisztítás és duplikáció-szűrés")
    logging.info("-" * 50)
    
    df_filtered = combined_df.copy()
    df_filtered['Hatasos_ertek_kWh'] = pd.to_numeric(df_filtered['Hatasos_ertek_kWh'].astype(str).str.replace(',', '.'), errors='coerce')
    df_filtered['Kezdo_datum'] = pd.to_datetime(df_filtered['Kezdo_datum'], errors='coerce')
    df_filtered['Zaro_datum'] = pd.to_datetime(df_filtered['Zaro_datum'], errors='coerce')
    df_filtered.dropna(subset=['Kezdo_datum', 'Zaro_datum', 'Hatasos_ertek_kWh'], inplace=True)
    
    final_df = dh.remove_duplicates(df_filtered, keep_strategy='last')
    stats = dh.get_duplication_statistics()
    logging.info(f"Duplikáció-szűrés után: {stats.final_count} sor maradt (eltávolítva: {stats.removed_total}).")

    logging.info("\n" + "-" * 50)
    logging.info("STEP 4: Végeredmény mentése")
    logging.info("-" * 50)
    
    output_df = final_df[['Kezdo_datum', 'Hatasos_ertek_kWh']].sort_values(by="Kezdo_datum").reset_index(drop=True)
    output_path = fp.output_dir / "energia_adatok_tisztitott.csv"
    
    if fp.save_csv_file(output_df, output_path):
        logging.info(f"✅ Végleges, tiszta adatfájl sikeresen elmentve ide: {output_path}")
    else:
        logging.error("❌ A végleges adatfájl mentése SIKERTELEN.")
        sys.exit(1)

if __name__ == "__main__":
    main()


