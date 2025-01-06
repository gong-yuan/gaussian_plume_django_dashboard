params = {
    "Q0": {
        "min": "0", 
        "max": "150",
        "step": "50"
    },
    "Q1": {
        "min": "0", 
        "max": "150",
        "step": "50"
    },
    "Q2": {
        "min": "0", 
        "max": "250",
        "step": "50"
    },
    "H0": {
        "min": "0",
        "max": "50",
        "step": "25"
    },
    "H1": {
        "min": "0",
        "max": "50",
        "step": "25"
    },
    "H2": {
        "min": "0",
        "max": "25",
        "step": "12.5"
    }
}

# When Q0 = 0, it means there is no stack, different H0 values will not matter, just test one H. Saving 16 * 2 = 32 cases.