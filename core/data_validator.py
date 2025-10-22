#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 DATA VALIDATOR v1.0 - CENTRALIZED VALIDATION
===============================================
Fájl: /home/tibor/PythonProjects/energia_monitoring/src/core/data_validator.py

🎯 CÉL: Minden adatvalidálás EGY HELYEN
✅ Energia adatok minőség ellenőrzés
✅ Időintervallum validálás
✅ Fogyasztási anomáliák detektálása
✅ Szezonális mintázatok figyelembevétele
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class HealthStatus(Enum):
    """Adatok egészségügyi státusza"""

    HEALTHY = "✅ Egészséges"
    WARNING = "⚠️ Figyelmeztetés"
    CRITICAL = "🚨 Kritikus"
    UNKNOWN = "❓ Ismeretlen"


class SeasonType(Enum):
    """Évszakok elektromos fűtéshez"""

    WINTER = "❄️ Tél"  # Dec, Jan, Feb
    SPRING = "🌸 Tavasz"  # Mar, Apr, May
    SUMMER = "☀️ Nyár"  # Jun, Jul, Aug
    AUTUMN = "🍂 Ősz"  # Sep, Oct, Nov


@dataclass
class ConsumptionBounds:
    """Fogyasztási határértékek évszakonként"""

    min_daily_kwh: float
    max_daily_kwh: float
    expected_hourly_kwh: float
    season: SeasonType


@dataclass
class ValidationResult:
    """Egységes validálási eredmény"""

    is_valid: bool
    severity: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComprehensiveReport:
    """Teljes körű validálási riport"""

    total_records: int
    date_range_start: datetime
    date_range_end: datetime
    total_days: int

    # Fogyasztási statisztikák
    total_consumption_kwh: float
    avg_daily_consumption: float
    avg_hourly_consumption: float

    # Minőségi mutatók
    negative_values: int
    zero_values: int
    extreme_values: int
    missing_data_periods: int

    # Szezonális elemzés
    dominant_season: SeasonType
    seasonal_breakdown: Dict[SeasonType, float]

    # Validálási eredmények
    validation_results: List[ValidationResult]
    overall_health: HealthStatus

    # Becslések
    monthly_estimate_kwh: float
    yearly_estimate_kwh: float
    yearly_cost_estimate_huf: float


class DataValidator:
    """
    🔍 INTELLIGENS ADATVALIDÁTOR v1.0

    Központosított validálási logika minden energia adathoz.
    """

    def __init__(self, electricity_price_huf: float = 56.07):
        """
        Inicializálás

        Args:
            electricity_price_huf: Villamos energia ára (Ft/kWh)
        """
        self.electricity_price = electricity_price_huf
        self.logger = logging.getLogger(__name__)

        # Szezonális fogyasztási határértékek (elektromos fűtéssel)
        self.seasonal_bounds = {
            SeasonType.WINTER: ConsumptionBounds(15.0, 80.0, 1.5, SeasonType.WINTER),
            SeasonType.SPRING: ConsumptionBounds(8.0, 40.0, 0.8, SeasonType.SPRING),
            SeasonType.SUMMER: ConsumptionBounds(3.0, 25.0, 0.4, SeasonType.SUMMER),
            SeasonType.AUTUMN: ConsumptionBounds(10.0, 50.0, 1.0, SeasonType.AUTUMN),
        }

    def validate_comprehensive(self, df: pd.DataFrame) -> ComprehensiveReport:
        """
        🔍 TELJES KÖRŰ ADATVALIDÁLÁS

        Minden validálási ellenőrzés egy helyen.
        """
        print(f"\n🔍 TELJES KÖRŰ ADATVALIDÁLÁS ELKEZDŐDÖTT")
        print("=" * 60)

        # Alapadatok kinyerése
        basic_stats = self._extract_basic_statistics(df)

        # Validálási ellenőrzések futtatása
        validation_results = []
        validation_results.extend(self._validate_data_completeness(df))
        validation_results.extend(self._validate_consumption_values(df))
        validation_results.extend(self._validate_time_intervals(df))
        validation_results.extend(self._validate_seasonal_patterns(df, basic_stats))

        # Szezonális elemzés
        seasonal_breakdown = self._analyze_seasonal_consumption(df, basic_stats)
        dominant_season = self._determine_dominant_season(seasonal_breakdown)

        # Összesített egészségügyi státusz
        overall_health = self._calculate_overall_health(validation_results)

        # Becslések számítása
        estimates = self._calculate_consumption_estimates(basic_stats)

        # Riport összeállítása
        report = ComprehensiveReport(
            total_records=basic_stats["total_records"],
            date_range_start=basic_stats["date_start"],
            date_range_end=basic_stats["date_end"],
            total_days=basic_stats["total_days"],
            total_consumption_kwh=basic_stats["total_consumption"],
            avg_daily_consumption=basic_stats["avg_daily"],
            avg_hourly_consumption=basic_stats["avg_hourly"],
            negative_values=basic_stats["negative_count"],
            zero_values=basic_stats["zero_count"],
            extreme_values=basic_stats["extreme_count"],
            missing_data_periods=0,  # TODO: implementálni
            dominant_season=dominant_season,
            seasonal_breakdown=seasonal_breakdown,
            validation_results=validation_results,
            overall_health=overall_health,
            monthly_estimate_kwh=estimates["monthly"],
            yearly_estimate_kwh=estimates["yearly"],
            yearly_cost_estimate_huf=estimates["yearly_cost"],
        )

        self._print_comprehensive_report(report)

        return report

    def _extract_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Alapstatisztikák kinyerése"""

        # Időintervallum számítása
        df_work = df.copy()
        df_work["Intervallum_ora"] = (
            df_work["Zaro_datum"] - df_work["Kezdo_datum"]
        ).dt.total_seconds() / 3600
        df_work["Orankenti_fogyasztas"] = (
            df_work["Hatasos_ertek_kWh"] / df_work["Intervallum_ora"]
        )

        # Alapadatok
        total_records = len(df)
        date_start = df["Kezdo_datum"].min()
        date_end = df["Zaro_datum"].max()
        total_days = (date_end - date_start).days + 1

        # Fogyasztási adatok
        total_consumption = df["Hatasos_ertek_kWh"].sum()
        avg_hourly = df_work["Orankenti_fogyasztas"].mean()
        avg_daily = avg_hourly * 24

        # Minőségi mutatók
        negative_count = (df["Hatasos_ertek_kWh"] < 0).sum()
        zero_count = (df["Hatasos_ertek_kWh"] == 0).sum()
        extreme_count = (df_work["Orankenti_fogyasztas"] > 50).sum()

        return {
            "total_records": total_records,
            "date_start": date_start,
            "date_end": date_end,
            "total_days": total_days,
            "total_consumption": total_consumption,
            "avg_hourly": avg_hourly,
            "avg_daily": avg_daily,
            "negative_count": negative_count,
            "zero_count": zero_count,
            "extreme_count": extreme_count,
            "df_work": df_work,
        }

    def _validate_data_completeness(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Adatok teljességének ellenőrzése"""
        results = []

        # Hiányzó értékek ellenőrzése
        missing_start_dates = df["Kezdo_datum"].isna().sum()
        missing_end_dates = df["Zaro_datum"].isna().sum()
        missing_consumption = df["Hatasos_ertek_kWh"].isna().sum()

        total_missing = missing_start_dates + missing_end_dates + missing_consumption

        if total_missing == 0:
            results.append(
                ValidationResult(
                    is_valid=True,
                    severity=HealthStatus.HEALTHY,
                    message="Nincsenek hiányzó értékek",
                    details={"missing_count": 0},
                )
            )
        else:
            results.append(
                ValidationResult(
                    is_valid=False,
                    severity=HealthStatus.WARNING,
                    message=f"Hiányzó értékek találhatók: {total_missing}",
                    details={
                        "missing_start_dates": missing_start_dates,
                        "missing_end_dates": missing_end_dates,
                        "missing_consumption": missing_consumption,
                    },
                )
            )

        return results

    def _validate_consumption_values(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Fogyasztási értékek validálása"""
        results = []

        # Negatív értékek
        negative_count = (df["Hatasos_ertek_kWh"] < 0).sum()
        if negative_count > 0:
            results.append(
                ValidationResult(
                    is_valid=False,
                    severity=HealthStatus.WARNING,
                    message=f"Negatív fogyasztási értékek: {negative_count}",
                    details={"negative_values": negative_count},
                )
            )

        # Nulla értékek (hibás mérők)
        zero_count = (df["Hatasos_ertek_kWh"] == 0).sum()
        if zero_count > 0:
            zero_percentage = (zero_count / len(df)) * 100
            severity = (
                HealthStatus.CRITICAL if zero_percentage > 10 else HealthStatus.WARNING
            )

            results.append(
                ValidationResult(
                    is_valid=zero_percentage < 5,
                    severity=severity,
                    message=f"Nulla fogyasztási értékek: {zero_count} ({zero_percentage:.1f}%)",
                    details={
                        "zero_values": zero_count,
                        "zero_percentage": zero_percentage,
                    },
                )
            )

        return results

    def _validate_time_intervals(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Időintervallumok validálása"""
        results = []

        # Intervallum számítása
        df_work = df.copy()
        df_work["Intervallum_perc"] = (
            df_work["Zaro_datum"] - df_work["Kezdo_datum"]
        ).dt.total_seconds() / 60

        # Várt intervallumok ellenőrzése
        interval_15min = len(
            df_work[
                (df_work["Intervallum_perc"] >= 14)
                & (df_work["Intervallum_perc"] <= 16)
            ]
        )
        interval_60min = len(
            df_work[
                (df_work["Intervallum_perc"] >= 55)
                & (df_work["Intervallum_perc"] <= 65)
            ]
        )

        total_standard = interval_15min + interval_60min
        standard_percentage = (total_standard / len(df_work)) * 100

        if standard_percentage > 95:
            results.append(
                ValidationResult(
                    is_valid=True,
                    severity=HealthStatus.HEALTHY,
                    message=f"Időintervallumok rendben ({standard_percentage:.1f}% szabványos)",
                    details={
                        "interval_15min": interval_15min,
                        "interval_60min": interval_60min,
                        "standard_percentage": standard_percentage,
                    },
                )
            )
        else:
            results.append(
                ValidationResult(
                    is_valid=False,
                    severity=HealthStatus.WARNING,
                    message=f"Szokatlan időintervallumok ({standard_percentage:.1f}% szabványos)",
                    details={
                        "interval_15min": interval_15min,
                        "interval_60min": interval_60min,
                        "standard_percentage": standard_percentage,
                    },
                )
            )

        return results

    def _validate_seasonal_patterns(
        self, df: pd.DataFrame, basic_stats: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Szezonális mintázatok validálása"""
        results = []

        avg_daily = basic_stats["avg_daily"]
        date_start = basic_stats["date_start"]
        date_end = basic_stats["date_end"]

        # Meghatározzuk a domináns évszakot
        dominant_season = self._get_season_for_period(date_start, date_end)
        expected_bounds = self.seasonal_bounds[dominant_season]

        # Szezonális elvárásokhoz viszonyítás
        if expected_bounds.min_daily_kwh <= avg_daily <= expected_bounds.max_daily_kwh:
            results.append(
                ValidationResult(
                    is_valid=True,
                    severity=HealthStatus.HEALTHY,
                    message=f"Fogyasztás a szezonális elvárásoknak megfelelő ({dominant_season.value})",
                    details={
                        "avg_daily": avg_daily,
                        "season": dominant_season.value,
                        "expected_min": expected_bounds.min_daily_kwh,
                        "expected_max": expected_bounds.max_daily_kwh,
                    },
                )
            )
        else:
            if avg_daily < expected_bounds.min_daily_kwh:
                severity = HealthStatus.WARNING
                message = f"Átlag alatti fogyasztás {dominant_season.value} időszakra"
            else:
                severity = HealthStatus.WARNING
                message = f"Átlag feletti fogyasztás {dominant_season.value} időszakra"

            results.append(
                ValidationResult(
                    is_valid=False,
                    severity=severity,
                    message=message,
                    details={
                        "avg_daily": avg_daily,
                        "season": dominant_season.value,
                        "expected_min": expected_bounds.min_daily_kwh,
                        "expected_max": expected_bounds.max_daily_kwh,
                    },
                )
            )

        return results

    def _analyze_seasonal_consumption(
        self, df: pd.DataFrame, basic_stats: Dict[str, Any]
    ) -> Dict[SeasonType, float]:
        """Szezonális fogyasztás elemzése"""

        df_work = basic_stats["df_work"].copy()
        df_work["Month"] = df_work["Kezdo_datum"].dt.month

        # Havi fogyasztások számítása
        monthly_consumption = df_work.groupby("Month")["Hatasos_ertek_kWh"].sum()

        # Évszakokra bontás
        seasonal_totals = {season: 0.0 for season in SeasonType}

        for month, consumption in monthly_consumption.items():
            season = self._get_season_for_month(month)
            seasonal_totals[season] += consumption

        return seasonal_totals

    def _determine_dominant_season(
        self, seasonal_breakdown: Dict[SeasonType, float]
    ) -> SeasonType:
        """Meghatározza a domináns évszakot a fogyasztás alapján"""
        return max(seasonal_breakdown.keys(), key=lambda s: seasonal_breakdown[s])

    def _get_season_for_month(self, month: int) -> SeasonType:
        """Évszak meghatározása hónap alapján"""
        if month in [12, 1, 2]:
            return SeasonType.WINTER
        elif month in [3, 4, 5]:
            return SeasonType.SPRING
        elif month in [6, 7, 8]:
            return SeasonType.SUMMER
        else:  # 9, 10, 11
            return SeasonType.AUTUMN

    def _get_season_for_period(
        self, start_date: datetime, end_date: datetime
    ) -> SeasonType:
        """Domináns évszak meghatározása időszakra"""

        # Egyszerűsített: a középső dátum hónapja alapján
        middle_date = start_date + (end_date - start_date) / 2
        return self._get_season_for_month(middle_date.month)

    def _calculate_overall_health(
        self, validation_results: List[ValidationResult]
    ) -> HealthStatus:
        """Összesített egészségügyi státusz számítása"""

        if not validation_results:
            return HealthStatus.UNKNOWN

        # Legsúlyosabb probléma meghatározása
        severities = [result.severity for result in validation_results]

        if HealthStatus.CRITICAL in severities:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in severities:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY

    def _calculate_consumption_estimates(
        self, basic_stats: Dict[str, Any]
    ) -> Dict[str, float]:
        """Fogyasztási becslések számítása"""

        avg_daily = basic_stats["avg_daily"]

        monthly_estimate = avg_daily * 30
        yearly_estimate = avg_daily * 365
        yearly_cost = yearly_estimate * self.electricity_price

        return {
            "monthly": monthly_estimate,
            "yearly": yearly_estimate,
            "yearly_cost": yearly_cost,
        }

    def _print_comprehensive_report(self, report: ComprehensiveReport):
        """Részletes riport kiírása"""

        print(f"\n📊 TELJES KÖRŰ VALIDÁLÁSI RIPORT")
        print("=" * 60)

        # Alapadatok
        print(
            f"📅 Időszak: {report.date_range_start.date()} → {report.date_range_end.date()}"
        )
        print(f"📊 Napok száma: {report.total_days}")
        print(f"📈 Rekordok száma: {report.total_records:,}")

        # Fogyasztási statisztikák
        print(f"\n⚡ FOGYASZTÁSI ADATOK:")
        print(f"   📊 Összes: {report.total_consumption_kwh:.1f} kWh")
        print(f"   📊 Napi átlag: {report.avg_daily_consumption:.1f} kWh/nap")
        print(f"   📊 Órás átlag: {report.avg_hourly_consumption:.3f} kWh/óra")

        # Szezonális elemzés
        print(f"\n{report.dominant_season.value} SZEZONÁLIS ELEMZÉS:")
        for season, consumption in report.seasonal_breakdown.items():
            if consumption > 0:
                print(f"   {season.value}: {consumption:.1f} kWh")

        # Minőségi mutatók
        print(f"\n🔍 ADATMINŐSÉG:")
        print(f"   ❌ Negatív értékek: {report.negative_values}")
        print(f"   ⭕ Nulla értékek: {report.zero_values}")
        print(f"   🔥 Extrém értékek: {report.extreme_values}")

        # Validálási eredmények
        print(f"\n✅ VALIDÁLÁSI EREDMÉNYEK:")
        for result in report.validation_results:
            status_icon = "✅" if result.is_valid else "⚠️"
            print(f"   {status_icon} {result.message}")

        # Összesített státusz
        print(f"\n{report.overall_health.value} ÖSSZESÍTETT ÁLLAPOT")

        # Becslések
        print(f"\n💰 BECSLÉSEK:")
        print(f"   📊 Havi becslés: {report.monthly_estimate_kwh:.0f} kWh")
        print(f"   📊 Éves becslés: {report.yearly_estimate_kwh:.0f} kWh")
        print(f"   💰 Éves költség: {report.yearly_cost_estimate_huf:,.0f} Ft")

        self.logger.info(f"Validálási riport elkészült: {report.overall_health.value}")

    def quick_validate(self, df: pd.DataFrame) -> HealthStatus:
        """
        🚀 GYORS VALIDÁLÁS

        Egyszerű interface a gyors állapot ellenőrzéshez.
        """
        report = self.validate_comprehensive(df)
        return report.overall_health

    def validate_consumption_bounds(
        self, avg_daily: float, season: SeasonType
    ) -> ValidationResult:
        """Adott fogyasztás validálása szezonális határokhoz képest"""

        bounds = self.seasonal_bounds[season]

        if bounds.min_daily_kwh <= avg_daily <= bounds.max_daily_kwh:
            return ValidationResult(
                is_valid=True,
                severity=HealthStatus.HEALTHY,
                message=f"Fogyasztás normális {season.value} időszakra",
                details={"avg_daily": avg_daily, "season": season.value},
            )
        else:
            severity = HealthStatus.WARNING
            if avg_daily < bounds.min_daily_kwh:
                message = f"Alacsony fogyasztás {season.value} időszakra"
            else:
                message = f"Magas fogyasztás {season.value} időszakra"

            return ValidationResult(
                is_valid=False,
                severity=severity,
                message=message,
                details={"avg_daily": avg_daily, "season": season.value},
            )


# ===== UTILITY FUNCTIONS =====


def create_data_validator(electricity_price: float = 56.07) -> DataValidator:
    """Factory függvény DataValidator létrehozásához"""
    return DataValidator(electricity_price_huf=electricity_price)


def quick_data_validation(df: pd.DataFrame) -> HealthStatus:
    """
    🚀 GYORS ADATVALIDÁLÁS

    Egyszerű interface a gyors használathoz.
    """
    validator = DataValidator()
    return validator.quick_validate(df)


# ===== TESZTELÉSI FUNKCIÓK =====


def test_data_validator():
    """Alapvető tesztelés a DataValidator osztályhoz"""
    print("🧪 DATA VALIDATOR TESZT")
    print("=" * 40)

    # Mock DataFrame létrehozása
    date_range = pd.date_range("2025-01-01", periods=96, freq="15T")
    test_data = {
        "Gyariszam": ["123"] * 96,
        "Azonosito": ["A1"] * 96,
        "Kezdo_datum": date_range[:-1],
        "Zaro_datum": date_range[1:],
        "Hatasos_ertek_kWh": np.random.uniform(
            0.05, 0.25, 95
        ),  # Téli fogyasztás szimuláció
    }

    df_test = pd.DataFrame(test_data)

    print(f"Teszt DataFrame létrehozva: {len(df_test)} rekord")
    print("Téli fogyasztás szimulálva")

    # DataValidator tesztelése
    validator = DataValidator()
    report = validator.validate_comprehensive(df_test)

    print(f"✅ Teszt befejezve: {report.overall_health.value}")
    print(f"✅ Napi átlag: {report.avg_daily_consumption:.1f} kWh")

    return report


if __name__ == "__main__":
    # Alapvető teszt futtatása
    test_data_validator()

    print(f"\n🎉 DATA VALIDATOR v1.0 BETÖLTVE!")
    print(f"📝 Centralizált validálási logika")
    print(f"✅ Szezonális mintázatok figyelembevétele")
    print(f"✅ Elektromos fűtés támogatással!")
