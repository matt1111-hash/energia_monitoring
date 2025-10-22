#!/bin/bash

# A script saját mappájának megkeresése, hogy bárhonnan futtatható legyen
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# Változók a python környezethez és a scriptekhez
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
PROCESSING_SCRIPT="$SCRIPT_DIR/adatfeldolgozo.py"
GUI_SCRIPT="$SCRIPT_DIR/energia_monitor_ctk.py"

# Ellenőrizzük, hogy a venv létezik-e
if [ ! -f "$VENV_PYTHON" ]; then
    zenity --error --title="Indítási Hiba" --text="Hiba: A virtuális környezet (venv) nem található!\n\nKérlek, győződj meg róla, hogy a 'venv' mappa létezik a projektben."
    exit 1
fi

# 1. LÉPÉS: Adatfeldolgozás futtatása
# Lefuttatjuk a feldolgozó scriptet, és az esetleges hibaüzeneteket egy változóba mentjük.
echo "INFO: Adatfeldolgozás indul..."
PROCESSING_OUTPUT=$("$VENV_PYTHON" "$PROCESSING_SCRIPT" 2>&1)
EXIT_CODE=$? # Elmentjük a futás eredményét (0 = sikeres, nem 0 = hiba)

# 2. LÉPÉS: Eredmény ellenőrzése
if [ $EXIT_CODE -ne 0 ]; then
    # Ha hiba történt, megjelenítjük a hibaüzenetet egy ablakban és leállunk.
    zenity --error --title="Adatfeldolgozási Hiba" --width=500 --height=300 --text="Hiba történt az adatok feldolgozása közben, a program nem indul el.\n\nRészletek:\n$PROCESSING_OUTPUT"
    exit 1
fi

# 3. LÉPÉS: Grafikus felület indítása
# Ha minden rendben volt, elindítjuk a fő programot.
echo "INFO: Adatfeldolgozás sikeres. Grafikus felület indítása..."
"$VENV_PYTHON" "$GUI_SCRIPT"

exit 0
