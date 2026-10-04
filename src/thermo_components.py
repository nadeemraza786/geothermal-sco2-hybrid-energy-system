from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def compressor(T1, P1, P2, eta_c=0.80):
    h1 = PropsSI("H", "T", T1, "P", P1, FLUID)
    s1 = PropsSI("S", "T", T1, "P", P1, FLUID)
    h2s = PropsSI("H", "P", P2, "S", s1, FLUID)
    h2 = h1 + (h2s - h1) / eta_c
    T2 = PropsSI("T", "P", P2, "H", h2, FLUID)
    return {"T": T2, "h": h2, "w": h2 - h1}

def turbine(T3, P3, P4, eta_t=0.85):
    h3 = PropsSI("H", "T", T3, "P", P3, FLUID)
    s3 = PropsSI("S", "T", T3, "P", P3, FLUID)
    h4s = PropsSI("H", "P", P4, "S", s3, FLUID)
    h4 = h3 - eta_t * (h3 - h4s)
    T4 = PropsSI("T", "P", P4, "H", h4, FLUID)
    return {"T": T4, "h": h4, "w": h3 - h4, "h_in": h3}

def recuperator(h2, T2, P_high, h4, T4, eps=0.80):
    """
    Effectiveness based recuperator.
    Heat recovery is enabled only when the turbine exhaust is hotter
    than the compressor outlet. This avoids nonphysical reverse recovery.
    """
    if T4 <= T2:
        return {
            "active": False,
            "h2r": h2,
            "h4r": h4,
            "q_recup": 0.0,
        }

    h2_max = PropsSI("H", "T", T4, "P", P_high, FLUID)
    q_recup = max(0.0, eps * (h2_max - h2))
    h2r = h2 + q_recup
    h4r = h4 - q_recup
    return {
        "active": True,
        "h2r": h2r,
        "h4r": h4r,
        "q_recup": q_recup,
    }
