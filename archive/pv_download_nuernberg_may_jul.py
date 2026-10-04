# pv_download_nuernberg_may_jul.py
# Download PVGIS hourly data for Nürnberg, compute simple PV power (MW) for May–July,
# save CSV for your hybrid geothermal+PV+battery simulation, and print quick checks.

import pandas as pd
import pvlib

# Nürnberg (approx city center)
LAT, LON = 49.4521, 11.0767

# PV plant size
PV_MW = 1.0          # 1 MWp
PR = 0.85            # performance ratio (losses) - simple thesis-friendly
OUT_PATH = "data/nuernberg_pv_may_jul_hourly.csv"


def main():
    # 1) Get PVGIS hourly (Typical Meteorological Year by default)
    data, meta = pvlib.iotools.get_pvgis_hourly(LAT, LON)

    # 2) Make a clean datetime index
    df = data.copy()
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
        df = df.set_index("time")
    else:
        df.index = pd.to_datetime(df.index)

    # 3) Filter May–July (months 5,6,7)
    df_may_jul = df[(df.index.month >= 5) & (df.index.month <= 7)].copy()

    # 4) IMPORTANT FIX:
    # PVGIS gives POA components (plane-of-array). Use their sum for PV power model.
    # (W/m²) = poa_direct + poa_sky_diffuse + poa_ground_diffuse
    needed = ["poa_direct", "poa_sky_diffuse", "poa_ground_diffuse"]
    missing = [c for c in needed if c not in df_may_jul.columns]
    if missing:
        raise ValueError(
            f"Missing POA columns {missing}. Available columns are: {list(df_may_jul.columns)}"
        )

    G_poa = (
        df_may_jul["poa_direct"]
        + df_may_jul["poa_sky_diffuse"]
        + df_may_jul["poa_ground_diffuse"]
    ).clip(lower=0)  # W/m²

    # 5) Simple PV power model:
    # 1 MWp produces approx (G/1000)*PR*PV_MW in MW
    df_may_jul["P_pv_MW"] = (G_poa / 1000.0) * PR * PV_MW

    # 6) Keep useful columns for hybrid model
    keep_cols = ["P_pv_MW", "temp_air", "wind_speed", "solar_elevation"]
    keep_cols = [c for c in keep_cols if c in df_may_jul.columns]
    out = df_may_jul[keep_cols].copy()

    # 7) Save CSV (make sure folder exists)
    # If you don't have "data" folder, create it:
    #   mkdir data
    out.to_csv(OUT_PATH)

    # 8) Quick checks (energy + peak)
    dt_h = 1.0  # hourly
    total_mwh = out["P_pv_MW"].sum() * dt_h
    max_mw = out["P_pv_MW"].max()

    print("Columns from PVGIS:", list(df.columns))
    print("\nFirst rows (raw PVGIS):")
    print(df.head(3))

    print("\n--- May–July preview (with computed PV power) ---")
    print(out.head(5))

    print(f"\nSaved: {OUT_PATH}")
    print(f"Rows (hours): {len(out)}")
    print(f"Total PV Energy (May–Jul) for {PV_MW:.1f} MWp ≈ {total_mwh:.2f} MWh")
    print(f"Max PV Power (May–Jul) ≈ {max_mw:.3f} MW")


if __name__ == "__main__":
    main()
