#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# EGYSÉGESÍTETT EXPORT MODUL - v1.0

import pandas as pd
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# A data_handler.py-ból importáljuk a FilterConfig-ot a típus annotációhoz
# Mivel ugyanabban a mappában lesznek, ez működni fog.
from data_handler import FilterConfig

class ExportManager:
    """
    Osztály az adatok és riportok exportálásához (Excel, PDF).
    """
    def __init__(self):
        project_root = next((p for p in Path(__file__).resolve().parents if (p / 'venv').exists()), Path.cwd())
        self.export_dir = project_root / "exports"
        self.export_dir.mkdir(exist_ok=True) # Hozzuk létre a mappát, ha nem létezik

    def export_excel(self, df: pd.DataFrame | None, config: FilterConfig) -> bool:
        """
        Exportálja a szűrt adatokat egy időbélyeggel ellátott Excel fájlba.
        """
        if df is None or df.empty:
            print("⚠️ Az exportálás sikertelen: Nincs adat az exportáláshoz.")
            return False

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"energia_export_{config.interval}_{timestamp}.xlsx"
            export_path = self.export_dir / filename

            # Az oszlopneveket felhasználóbarátabbá tesszük
            df_to_export = df.rename(columns={
                'Kezdo_datum': 'Időpont',
                'Hatasos_ertek_kWh': 'Fogyasztás (kWh)'
            })

            df_to_export.to_excel(export_path, index=False, sheet_name="Energia Adatok")
            print(f"✅ Excel fájl sikeresen exportálva ide: {export_path}")
            return True
        except Exception as e:
            print(f"❌ Hiba történt az Excel exportálás során: {e}")
            return False

    def export_pdf(self, df: pd.DataFrame | None, config: FilterConfig, chart_gen) -> bool:
        """
        Exportálja a riportot PDF formátumban.
        FIGYELEM: Ez a funkció jelenleg csak egy placeholder.
        A teljes PDF generálás egy bonyolultabb könyvtárat (pl. ReportLab, FPDF) igényelne.
        """
        if df is None or df.empty:
            print("⚠️ A PDF export sikertelen: Nincs adat a riport készítéséhez.")
            return False

        print("🚧 A PDF riport generálása folyamatban...")
        # Itt következne a komplex PDF generáló logika.
        # Most csak sikert szimulálunk, hogy az UI ne hibásodjon meg.
        
        # Példa: a chart_gen-t itt használnánk a grafikon képének elmentésére,
        # majd a kép beillesztésre kerülne a PDF-be a statisztikákkal együtt.

        print("✅ PDF Riport sikeresen 'legenerálva' (szimuláció).")
        return True
