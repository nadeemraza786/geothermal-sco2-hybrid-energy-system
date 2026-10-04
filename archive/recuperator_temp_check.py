from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def comp_out(T1, P_low, P_high, eta_c=0.80):
    """Return T2 (K), h2 (J/kg) after compressor"""
    h1 = PropsSI("H", "T", T1, "P", P_low, FLUID)
    s1 = PropsSI("S", "T", T1, "P", P_low, FLUID)

    h2s = PropsSI("H", "P", P_high, "S", s1, FLUID)      # isentropic
    h2  = h1 + (h2s - h1) / eta_c                         # real
    T2  = PropsSI("T", "P", P_high, "H", h2, FLUID)
    return T2, h2

def turb_out(T3, P_high, P_low, eta_t=0.85):
    """Return T4 (K), h4 (J/kg) after turbine"""
    h3 = PropsSI("H", "T", T3, "P", P_high, FLUID)
    s3 = PropsSI("S", "T", T3, "P", P_high, FLUID)

    h4s = PropsSI("H", "P", P_low, "S", s3, FLUID)        # isentropic
    h4  = h3 - eta_t * (h3 - h4s)                         # real
    T4  = PropsSI("T", "P", P_low, "H", h4, FLUID)
    return T4, h4

def recuperator(T2, h2, P_high, T4, h4, P_low, eps=0.80):
    """
    Simple recuperator model (effectiveness eps).
    Returns: T2r, h2r (cold outlet), T4r, h4r (hot outlet)
    """
    # Cold side maximum possible: cold outlet cannot exceed hot inlet temperature (T4)
    h2_max = PropsSI("H", "T", T4, "P", P_high, FLUID)

    # Actual cold outlet enthalpy using effectiveness
    h2r = h2 + eps * (h2_max - h2)

    # Energy balance (same m_dot on both sides)
    h4r = h4 - (h2r - h2)

    # Convert to temperatures
    T2r = PropsSI("T", "P", P_high, "H", h2r, FLUID)
    T4r = PropsSI("T", "P", P_low,  "H", h4r, FLUID)

    return T2r, h2r, T4r, h4r

def main():
    # --- Use your current best values (edit if you want) ---
    T1_C = 35
    T3_C = 150
    P_low_bar  = 85      # you found ~85 bar from 2D map (use 80 if you want)
    P_high_bar = 160     # optimal high pressure

    eta_c = 0.80
    eta_t = 0.85
    eps_recup = 0.80     # recuperator effectiveness

    # Convert units
    T1 = T1_C + 273.15
    T3 = T3_C + 273.15
    P_low  = P_low_bar  * 1e5
    P_high = P_high_bar * 1e5

    # --- Compute states ---
    T2, h2 = comp_out(T1, P_low, P_high, eta_c)
    T4, h4 = turb_out(T3, P_high, P_low, eta_t)

    # Temps in °C
    T2_C = T2 - 273.15
    T4_C = T4 - 273.15

    # Recuperator temperature driving difference
    dT_recup = T4_C - T2_C

    print("\n--- Temperatures without Recuperator ---")
    print(f"T2 (after compressor): {T2_C:.2f} °C")
    print(f"T4 (after turbine):    {T4_C:.2f} °C")
    print(f"DeltaT available for recuperator (T4 - T2): {dT_recup:.2f} °C")

    # --- Optional: compute recuperator outlet temps ---
    T2r, h2r, T4r, h4r = recuperator(T2, h2, P_high, T4, h4, P_low, eps_recup)
    T2r_C = T2r - 273.15
    T4r_C = T4r - 273.15

    print("\n--- With Recuperator (effectiveness eps = {:.2f}) ---".format(eps_recup))
    print(f"T2r (after recuperator, cold side out): {T2r_C:.2f} °C")
    print(f"T4r (after recuperator, hot side out):  {T4r_C:.2f} °C")
    print(f"Cold-side temperature rise (T2r - T2):  {(T2r_C - T2_C):.2f} °C")
    print(f"Hot-side temperature drop (T4 - T4r):   {(T4_C - T4r_C):.2f} °C")

if __name__ == "__main__":
    main()
