#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Energia Monitor v3.0 - CustomTkinter UI (naptár popup)
"""

import os
from datetime import datetime, timedelta
from tkinter import messagebox
import tkinter as tk

import customtkinter as ctk
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from data_handler import DataHandler, FilterConfig
from export_module import ExportManager

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class EnergyMonitorApp(ctk.CTk):
    """Energia Monitor - splitter layout + naptár."""

    def __init__(self):
        super().__init__()

        self.title("⚡ Energia Monitor v3.0")
        self.geometry("1600x900")

        self.data_handler = DataHandler()
        self.export_mgr = ExportManager()
        self.current_df = None

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """UI komponensek - 3 panel splitterekkel."""
        main_paned = tk.PanedWindow(self, orient="horizontal", bg="#2b2b2b", 
                                    sashwidth=5, sashrelief="raised")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)

        left_frame = self.create_left_panel()
        main_paned.add(left_frame, minsize=250, width=320)

        center_frame = self.create_center_panel()
        main_paned.add(center_frame, minsize=400)

        right_frame = self.create_right_panel()
        main_paned.add(right_frame, minsize=200, width=240)

        self.status_label = ctk.CTkLabel(self, text="⏳ Indítás...", font=("Ubuntu", 12))
        self.status_label.pack(side="bottom", pady=5)

    def create_left_panel(self):
        """Bal oldali kontroll panel."""
        frame = ctk.CTkFrame(self)

        header_frame = ctk.CTkFrame(frame)
        header_frame.pack(pady=10, fill="x", padx=10)
        
        ctk.CTkLabel(header_frame, text="📋 Beállítások", font=("Ubuntu", 16, "bold")).pack(side="left")
        
        self.theme_switch = ctk.CTkSwitch(
            header_frame, 
            text="🌙", 
            command=self.toggle_theme,
            width=50
        )
        self.theme_switch.pack(side="right")
        self.theme_switch.select()

        self.quick_pick = ctk.CTkComboBox(
            frame,
            values=["Teljes adatkészlet", "Mai nap", "Előző 7 nap", "Előző hónap", "Egyedi"],
            command=self.handle_quick_pick,
            font=("Ubuntu", 12)
        )
        self.quick_pick.pack(pady=5, padx=10, fill="x")
        self.quick_pick.set("Teljes adatkészlet")

        ctk.CTkLabel(frame, text="Kezdő dátum:", font=("Ubuntu", 12)).pack(pady=(10, 0))
        self.start_date = DateEntry(
            frame,
            width=25,
            background='#1f538d',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Ubuntu", 11)
        )
        self.start_date.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(frame, text="Végső dátum:", font=("Ubuntu", 12)).pack(pady=(10, 0))
        self.end_date = DateEntry(
            frame,
            width=25,
            background='#1f538d',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Ubuntu", 11)
        )
        self.end_date.pack(pady=5, padx=10, fill="x")

        self.interval = ctk.CTkComboBox(
            frame,
            values=["15 perces", "Óránkénti", "Napi", "Heti", "Havi"],
            font=("Ubuntu", 12)
        )
        self.interval.pack(pady=10, padx=10, fill="x")
        self.interval.set("Napi")

        ctk.CTkButton(frame, text="🔄 Frissítés", command=self.refresh_chart, font=("Ubuntu", 13, "bold")).pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(frame, text="📊 Excel Export", command=self.export_excel, font=("Ubuntu", 12)).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(frame, text="📄 PDF Riport", command=self.export_pdf, font=("Ubuntu", 12)).pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(frame, text="💰 Egységár: 56.07 Ft/kWh", font=("Ubuntu", 11)).pack(pady=20)

        return frame

    def create_center_panel(self):
        """Középső panel - grafikon."""
        frame = ctk.CTkFrame(self)
        self.chart_frame = ctk.CTkFrame(frame)
        self.chart_frame.pack(fill="both", expand=True, padx=5, pady=5)
        return frame

    def create_right_panel(self):
        """Jobb panel - statisztikák."""
        frame = ctk.CTkFrame(self)
        
        ctk.CTkLabel(frame, text="📊 STATISZTIKÁK", font=("Ubuntu", 18, "bold")).pack(pady=15)
        
        self.stats_text = ctk.CTkTextbox(frame, font=("Ubuntu", 16), wrap="word")
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.stats_text.insert("1.0", "📊 Statisztikák betöltése...")
        self.stats_text.configure(state="disabled")
        
        return frame

    def load_data(self):
        """Adatok betöltése."""
        self.status_label.configure(text="⏳ Adatok betöltése...")
        self.update()

        self.current_df = self.data_handler.load_data()
        if self.current_df is not None:
            # FONTOS: állítsuk be a dátumokat az aktuális adatkészlethez
            # a quick_pick.set NEM hívja meg a logikát, ezért kézzel triggerelem
            self.quick_pick.set("Teljes adatkészlet")
            self.handle_quick_pick("Teljes adatkészlet")
            self.refresh_chart()
            self.status_label.configure(text="✅ Adatok betöltve")
        else:
            self.status_label.configure(text="❌ Adatok betöltési hiba")

    def handle_quick_pick(self, choice):
        """Gyors választás kezelése."""
        today = datetime.now().date()

        if choice == "Mai nap":
            self.start_date.set_date(today)
            self.end_date.set_date(today)
        elif choice == "Előző 7 nap":
            self.start_date.set_date(today - timedelta(days=7))
            self.end_date.set_date(today)
        elif choice == "Előző hónap":
            first_day = today.replace(day=1)
            prev_month_end = first_day - timedelta(days=1)
            prev_month_start = prev_month_end.replace(day=1)
            self.start_date.set_date(prev_month_start)
            self.end_date.set_date(prev_month_end)
        elif choice == "Teljes adatkészlet" and self.current_df is not None:
            min_date = self.current_df["Kezdo_datum"].min().date()
            max_date = self.current_df["Kezdo_datum"].max().date()
            self.start_date.set_date(min_date)
            self.end_date.set_date(max_date)

    def refresh_chart(self):
        """Grafikon frissítése."""
        self.status_label.configure(text="⏳ Grafikon generálása...")
        self.update()

        interval_map = {
            "15 perces": "15min",
            "Óránkénti": "hourly",
            "Napi": "daily",
            "Heti": "weekly",
            "Havi": "monthly",
        }

        config = FilterConfig(
            start_date=self.start_date.get_date(),
            end_date=self.end_date.get_date(),
            interval=interval_map[self.interval.get()],
        )

        filtered_df = self.data_handler.filter_data(self.current_df, config)

        if filtered_df is None or filtered_df.empty:
            messagebox.showwarning("Hiba", "Nincs adat a kiválasztott időszakban")
            return

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        is_dark = ctk.get_appearance_mode() == "Dark"
        
        fig = Figure(figsize=(14, 7), dpi=100, 
                    facecolor="#2b2b2b" if is_dark else "#f0f0f0")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#3b3b3b" if is_dark else "white")

        x_data = filtered_df["Kezdo_datum"]
        y_data = filtered_df["Hatasos_ertek_kWh"]

        ax.plot(x_data, y_data, linewidth=2, color="#2E86C1", alpha=0.8)

        avg_val = y_data.mean()
        ax.axhline(y=avg_val, color="#E74C3C", linestyle="--", linewidth=2, 
                   label=f"Átlag: {avg_val:.2f} kWh", alpha=0.7)

        text_color = "white" if is_dark else "black"
        ax.set_title(f"⚡ Energiafogyasztás - {self.interval.get()}", 
                     color=text_color, fontsize=14, fontweight="bold", fontfamily="Ubuntu")
        ax.set_xlabel("Idő", color=text_color, fontsize=11, fontfamily="Ubuntu")
        ax.set_ylabel("Fogyasztás (kWh)", color=text_color, fontsize=11, fontfamily="Ubuntu")
        ax.tick_params(colors=text_color, labelsize=10)
        ax.grid(True, alpha=0.3, linestyle="--", color="gray")
        
        legend_bg = "#2b2b2b" if is_dark else "white"
        legend = ax.legend(facecolor=legend_bg, edgecolor=text_color, labelcolor=text_color)
        legend.get_frame().set_alpha(0.9)

        fig.autofmt_xdate(rotation=45, ha="right")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_statistics(filtered_df)
        self.status_label.configure(text=f"✅ Grafikon kész ({len(filtered_df)} adatpont)")

    def update_statistics(self, df):
        """Statisztikák frissítése."""
        stats = self.data_handler.calculate_statistics(df)

        stats_text = f"""📊 ALAPADATOK


Átlag:  {stats['avg']:.2f} kWh

Minimum:  {stats['min']:.2f} kWh

Maximum:  {stats['max']:.2f} kWh

Összesen:  {stats['total']:.2f} kWh



💰 BECSLÉSEK
(Egységár: 56.07 Ft/kWh)


Napi átlag:
    {stats['daily_avg']:.2f} kWh


Havi becslés:
    {stats['monthly_est']:.0f} kWh
    {stats['monthly_cost']:,.0f} Ft


Éves becslés:
    {stats['yearly_est']:.0f} kWh
    {stats['yearly_cost']:,.0f} Ft"""

        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats_text)
        self.stats_text.configure(state="disabled")

    def toggle_theme(self):
        """Téma váltás dark/light között."""
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="🌙")
        else:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="☀️")
        
        if self.current_df is not None:
            self.refresh_chart()

    def export_excel(self):
        """Excel export."""
        self.status_label.configure(text="⏳ Excel export...")
        self.update()

        interval_map = {
            "15 perces": "15min",
            "Óránkénti": "hourly",
            "Napi": "daily",
            "Heti": "weekly",
            "Havi": "monthly",
        }

        config = FilterConfig(
            start_date=self.start_date.get_date(),
            end_date=self.end_date.get_date(),
            interval=interval_map[self.interval.get()],
        )

        filtered_df = self.data_handler.filter_data(self.current_df, config)
        success = self.export_mgr.export_excel(filtered_df, config)

        if success:
            self.status_label.configure(text="✅ Excel exportálva")
            messagebox.showinfo("Siker", "Excel fájl sikeresen exportálva!")
        else:
            self.status_label.configure(text="❌ Excel export hiba")

    def export_pdf(self):
        """PDF export."""
        self.status_label.configure(text="⏳ PDF export...")
        self.update()

        interval_map = {
            "15 perces": "15min",
            "Óránkénti": "hourly",
            "Napi": "daily",
            "Heti": "weekly",
            "Havi": "monthly",
        }

        config = FilterConfig(
            start_date=self.start_date.get_date(),
            end_date=self.end_date.get_date(),
            interval=interval_map[self.interval.get()],
        )

        filtered_df = self.data_handler.filter_data(self.current_df, config)
        
        from charts_module import ChartGenerator
        chart_gen = ChartGenerator(theme="dark")
        
        success = self.export_mgr.export_pdf(filtered_df, config, chart_gen)

        if success:
            self.status_label.configure(text="✅ PDF exportálva")
            messagebox.showinfo("Siker", "PDF riport sikeresen exportálva!")
        else:
            self.status_label.configure(text="❌ PDF export hiba")


def main():
    """Alkalmazás indítása."""
    app = EnergyMonitorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
