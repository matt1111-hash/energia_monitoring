#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# VÉGLEGES, GOLYÓÁLLÓ VERZIÓ

import logging
from pathlib import Path
import shutil
import pandas as pd

class FileProcessor:
    """Fájlkezelő modul, amely soha nem hibázik csendben."""

    def __init__(self) -> None:
        self.base_dir = next((p for p in Path(__file__).resolve().parents if (p / 'venv').exists() or (p / '.git').exists()), Path.cwd())
        self.input_dir = self.base_dir / "CSV-eredeti"
        self.output_dir = self.base_dir / "CSV-normalis"
        self.log_dir = self.base_dir / "logs"
        self.backup_dir = self.base_dir / "backups"
        for d in [self.input_dir, self.output_dir, self.log_dir, self.backup_dir]:
            d.mkdir(exist_ok=True)

    def load_csv_file(self, path: Path) -> pd.DataFrame | None:
        """Beolvas egy CSV fájlt, több kódolást is megpróbálva."""
        encodings = ["utf-8-sig", "ISO-8859-2", "cp1250", "latin1"]
        for enc in encodings:
            try:
                df = pd.read_csv(path, sep=";", encoding=enc, low_memory=False, on_bad_lines="warn")
                if not df.empty and len(df.columns) > 5:
                    logging.info(f"✅ Sikeres beolvasás: '{path.name}' ('{enc}').")
                    return df
            except Exception:
                continue
        
        logging.error(f"❌ VÉGLEGES HIBA: '{path.name}' fájlt nem sikerült beolvasni. KIHAGYVA.")
        return None

    def save_csv_file(self, df: pd.DataFrame, path: Path, create_backup: bool = True) -> bool:
        """Elment egy DataFrame-et CSV formátumba."""
        try:
            if create_backup and path.exists() and path.stat().st_size > 0:
                backup_name = f"{path.stem}_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                shutil.copy2(path, self.backup_dir / backup_name)
            df.to_csv(path, sep=";", encoding="utf-8-sig", index=False)
            return True
        except Exception as e:
            logging.error(f"❌ Mentési hiba a(z) '{path}' fájlnál: {e}")
            return False
