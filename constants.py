#!/usr/bin/env python3

AEROSOL_PROPERTIES = {
    "SODIUM_CHLORIDE": {"nu": 2.0, "rho_s": 2160.0, "Ms": 58.44e-3},
    "SULPHURIC_ACID": {"nu": 2.5, "rho_s": 1840.0, "Ms": 98e-3},
    "ORGANIC_ACID": {"nu": 1.0, "rho_s": 1500.0, "Ms": 200e-3},
    "AMMONIUM_NITRATE": {"nu": 2.0, "rho_s": 1725.0, "Ms": 80e-3}
}

AEROSOL_NAMES = {
    "1": "SODIUM_CHLORIDE",
    "2": "SULPHURIC_ACID",
    "3": "ORGANIC_ACID",
    "4": "AMMONIUM_NITRATE"
}

STABILITY_PROFILES = [
    "Very unstable",
    "Moderately unstable",
    "Slightly unstable",
    "Neutral",
    "Moderately stable",
    "Very stable"
]

HUMIDIFY_AEROSOL = {
    "1": "DRY_AEROSOL",
    "2": "HUMIDIFY"

}

OUTPUT_VIEW_TYPES = {
    "1": "PLAN_VIEW",
    "2": "HEIGHT_SLICE",
    "3": "SURFACE_TIME",
    "4": "NO_PLOT"
}

WIND_FIELD = {
    "1": "CONSTANT_WIND",
    "2": "FLUCTUATING_WIND",
    "3": "PREVAILING_WIND"
}

NUMBER_OF_STACKS = {
    "1": "ONE_STACK",
    "2": "TWO_STACKS",
    "3": "THREE_STACKS"
 }

STABILITY_VARIANT = {
    "1": "CONSTANT_STABILITY",
    "2": "ANNUAL_CYCLE"
}
