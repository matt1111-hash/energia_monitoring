#!/bin/bash

# --- BIZTONSÁGI FIGYELMEZTETÉS ---
# Ez a script VÉGLEGESEN törölni fog fájlokat és mappákat a projektből!
# Futtatás előtt győződj meg róla, hogy nincs benne olyan, amit meg akarsz tartani.
# Ha bizonytalan vagy, készíts egy teljes biztonsági mentést a projektmappáról!

echo "🧹 Projekt takarító script"
echo "-------------------------"
echo "Ez a script eltávolítja a felesleges fájlokat és mappákat."
echo "A törlés VÉGLEGES. Biztosan folytatni szeretnéd? (i/n)"

# Várunk a felhasználó megerősítésére
read -p "> " choice
if [[ "$choice" != "i" && "$choice" != "I" ]]; then
    echo "Takarítás megszakítva."
    exit 1
fi

echo "Takarítás megkezdve..."

# --- PyInstaller és build maradványok törlése ---
echo "🗑️  Build maradványok törlése (build/, dist/, *.spec)..."
rm -rf ./build/
rm -rf ./dist/
rm -f ./qt_energy_viewer.spec

# --- Kódelemző eszközök kimeneteinek törlése ---
echo "🗑️  Kódelemző kimenetek törlése (analysis_out/, *.png, *.dot)..."
rm -rf ./analysis_out/
rm -rf ./output/
rm -f ./architecture_map.png
rm -f ./fogyasztas_elemzes.png
rm -f ./hotspot_heatmap.png
rm -f ./project_edges.csv
rm -f ./project_graph.dot
rm -f ./project_graph.json
rm -f ./project_graph.png
rm -f ./project_import_graph_v2.png
rm -f ./structure_tree.png
rm -f ./radon_report.txt

# --- Régi, felesleges scriptek és segédfájlok törlése ---
echo "🗑️  Régi és felesleges scriptek törlése (*.sh, *.py)..."
rm -f ./cleanup.sh
rm -f ./debug_energia.sh
rm -f ./debug_utils.py
rm -f ./emergency_fix.py
rm -f ./energia_debug_script.sh
rm -f ./excel_structure_checker.py
rm -f ./generate_graph.py
rm -f ./generate_graph.sh
rm -f ./grok_project_mapper.py
rm -f ./indito.sh
rm -f ./mirror_py_to_txt.py
rm -f ./project_cleanup_analyzer.py
rm -f ./project_cleanup.py
rm -f ./project_mapper_standalone.py
rm -f ./quick_setup.sh
rm -f ./quick_test.py
rm -f ./run_energia_monitor.sh
rm -f ./start_energy_viewer.sh
rm -f ./start_viewer.sh
rm -f ./tools_archi_scan.py

# --- Régi .desktop fájlok törlése (a helyes 'EnergiaMonitor.desktop' megmarad) ---
rm -f ./energia-monitor.desktop
rm -f ./energia_monitor.desktop

# --- Ideiglenes, szöveges és egyéb maradvány fájlok törlése ---
echo "🗑️  Ideiglenes és egyéb maradványok törlése..."
rm -f ./2025-06-25-orai-adatok.csv # Adatfájl a gyökérben
rm -f ./'Névtelen dokumentum'
rm -f ./file_list.txt
rm -f ./file_references.txt
rm -f ./freeze_backup.txt
rm -f ./requirements_2025-08-11.txt
rm -f ./venv_dependencies.txt
rm -f ./CSV-normalis/energia_adatok.csv # Régi feldolgozott fájl

# --- Régi 'export' mappa kezelése ---
if [ -d "./export" ]; then
    echo "📦 Régi 'export' mappa átnevezése 'exports_regi'-re..."
    # Ha már létezik, akkor nem csinál semmit
    mv -n ./export ./exports_regi
    echo "    Nézd át az 'exports_regi' mappa tartalmát, és ha nem kell, töröld kézzel."
fi

# --- Python cache (__pycache__) mappák törlése ---
echo "🗑️  Python cache (__pycache__) törlése..."
find . -type d -name "__pycache__" -exec rm -r {} +

echo ""
echo "✅ Takarítás befejezve!"
echo "A projektmappa most már csak a szükséges fájlokat tartalmazza."
