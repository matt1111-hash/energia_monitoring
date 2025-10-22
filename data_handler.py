#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# EGYSÉGESÍTETT ADATKEZELŐ - v4.1 (JAVÍTOTT)

import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from datetime import date, datetime, time

@dataclass
class FilterConfig:
    """A GUI által átadott szűrési beállítások."""
    start_date: date
    end_date: date
    interval: str

class DataHandler:
    """Osztály a megtisztított adatok beolvasására és szűrésére a GUI számára."""
    def __init__(self):
        project_root = next((p for p in Path(__file__).resolve().parents if (p / 'venv').exists()), Path.cwd())
        self.processed_data_path = project_root / "CSV-normalis" / "energia_adatok_tisztitott.csv"
        self.electricity_price = 56.07  # Ft/kWh

    def load_data(self) -> pd.DataFrame | None:
        """Betölti az előfeldolgozott és megtisztított adatfájlt."""
        if not self.processed_data_path.exists():
            print(f"HIBA: A feldolgozott adatfájl nem található: {self.processed_data_path}")
            return None
        try:
            df = pd.read_csv(self.processed_data_path, sep=";", parse_dates=["Kezdo_datum"])
            print(f"✅ Adatok betöltve: {len(df)} sor a '{self.processed_data_path.name}' fájlból.")
            return df
        except Exception as e:
            print(f"HIBA az adatfájl beolvasása közben: {e}")
            return None

    def filter_data(self, df: pd.DataFrame | None, config: FilterConfig) -> pd.DataFrame | None:
        """Szűri és aggregálja az adatokat a megadott konfiguráció alapján."""
        if df is None or df.empty:
            return None

        # A szűréshez a teljes napot figyelembe vesszük
        start_dt = datetime.combine(config.start_date, time.min)
        end_dt = datetime.combine(config.end_date, time.max)

        mask = (df['Kezdo_datum'] >= start_dt) & (df['Kezdo_datum'] <= end_dt)
        filtered_df = df.loc[mask].copy()

        if filtered_df.empty:
            return None

        # Idősoros index beállítása a resample funkcióhoz
        filtered_df.set_index('Kezdo_datum', inplace=True)

        interval_map = {
            "15min": "15T",
            "hourly": "H",
            "daily": "D",
            "weekly": "W-MON",
            "monthly": "MS"
        }
        resample_rule = interval_map.get(config.interval)

        if resample_rule:
            # Csak akkor aggregálunk, ha van értelmes szabály
            aggregated_df = filtered_df['Hatasos_ertek_kWh'].resample(resample_rule).sum().reset_index()
            return aggregated_df
        else:
            # Ha nincs aggregálás (pl. "15 perces"), visszaadjuk a szűrt adatot
            return filtered_df.reset_index()

    def calculate_statistics(self, df: pd.DataFrame | None) -> dict:
        """Kiszámolja a statisztikákat a szűrt adatkészlet alapján."""
        if df is None or df.empty:
            # Üres szótár, ha nincs adat
            return {
                'avg': 0, 'min': 0, 'max': 0, 'total': 0,
                'daily_avg': 0, 'monthly_est': 0, 'monthly_cost': 0,
                'yearly_est': 0, 'yearly_cost': 0
            }

        consumption = df['Hatasos_ertek_kWh']
        total_consumption = consumption.sum()

        # Időszak hosszának kiszámítása napokban a valós adatok alapján
        num_days = (df['Kezdo_datum'].max() - df['Kezdo_datum'].min()).days + 1
        daily_avg = total_consumption / num_days if num_days > 0 else 0
        
        monthly_est = daily_avg * 30.44  # Átlagos hónap hossza
        yearly_est = daily_avg * 365.25 # Szökőévekkel is számolva

        stats = {
            'avg': consumption.mean(),
            'min': consumption.min(),
            'max': consumption.max(),
            'total': total_consumption,
            'daily_avg': daily_avg,
            'monthly_est': monthly_est,
            'monthly_cost': monthly_est * self.electricity_price,
            'yearly_est': yearly_est,
            'yearly_cost': yearly_est * self.electricity_price
        }
        return stats
