#!/usr/bin/env python3
import constants
import gaussian_plume_model as gp
import numpy as np
from scipy.special import erfcinv as erfcinv
from gauss_func import gauss_func
import pandas as pd
import inspect
from pdb import set_trace

class Simulation:
    def __init__(self,
                 RH = str(0.9),
                 aerosol_type = "1",
                 dry_size = str(60e-9),
                 humidify = "1",
                 stab1 = "1",
                 stability_used = "1",
                 output = "1",
                 x_slice = None,
                 y_slice = None,
                 wind = "1",
                 stacks = "3",
                 # stack_x = [1.2818367, 1.2665375, 1.2678407],
                 # stack_y = [103.7141216, 103.6978671, 103.7140133],
                 # Q = [100, 100, 200],
                 # H = [50, 50, 50],
                 stack_x0 = "1.2818367",
                 stack_y0 = "103.7141216",
                 stack_x1 = "1.2665375",
                 stack_y1 = "103.6978671",
                 stack_x2 = "1.2678407",
                 stack_y2 = "103.7140133",
                 location_type = "EPSG:4326",
                 Q0 = "100",
                 H0 = "50",
                 Q1 = "100",
                 H1 = "50",
                 Q2 = "200",
                 H2 = "50",
                 days = "50",
                 num_contour = "100",
                 windspeed = "5",
                 wind_dir = "225",
                 dxy = 100,
                 dz = 10,
                 Dy = 10.0,
                 Dz = 10.0,
                 Mw = 18e-3,
                 seed=1234):
        self.RH = float(RH)
        self.aerosol_type = constants.AEROSOL_NAMES[aerosol_type]
        self.dry_size = float(dry_size)
        self.humidify = constants.HUMIDIFY_AEROSOL[humidify]
        self.stab1 = int(stab1)
        self.stability_used = constants.STABILITY_VARIANT[stability_used]
        self.output = constants.OUTPUT_VIEW_TYPES[output]
        self.x_slice = x_slice
        self.y_slice = y_slice
        self.wind_type = constants.WIND_FIELD[wind]
        self.stacks = stacks
        self.stack_x_orig = [float(stack_x0), float(stack_x1), float(stack_x2)]
        self.stack_y_orig = [float(stack_y0), float(stack_y1), float(stack_y2)]
        self.location_type = location_type
        self.Q = [float(Q0), float(Q1), float(Q2)]
        self.H = [float(H0), float(H1), float(H2)]
        self.days = int(days)
        self.num_contour = int(num_contour)
        self.windspeed = float(windspeed)
        self.wind_dir_deg = int(wind_dir)


        self.num_timesteps = 24 * self.days
        self.dxy = dxy
        self.dz = dz
        self.Dy = Dy
        self.Dz = Dz
        self.Mw = Mw

        np.random.seed(seed)

    def setup_grid(self):
        self.x = np.mgrid[-2500:2500+self.dxy:self.dxy]
        self.y = self.x
        if self.output in ["PLAN_VIEW", "SURFACE_TIME", "NO_PLOT"]:
            self.C1 = np.zeros((len(self.x),len(self.y), self.num_timesteps))
            [self.x,self.y]=np.meshgrid(self.x, self.y)
            self.z=np.zeros(np.shape(self.x))
        elif self.output == "HEIGHT_SLICE":
            self.z=np.mgrid[0:500+self.dz:self.dz]
            self.C1=np.zeros((len(self.y), len(self.z), self.num_timesteps))
            from pdb import set_trace; set_trace()
            [self.y,self.z]=np.meshgrid(self.y,self.z)
            self.x=self.x[x_slice]*np.ones(np.shape(y))
        else:
            raise ValueError("Unsupported output type")

        self.times=np.mgrid[1:(self.days)*24+1:1]/24.

    def set_stability_profile(self):
        if self.stability_used == "CONSTANT_STABILITY":
            self.stability = self.stab1 * np.ones((self.num_timesteps, 1))
            self.stability_str = constants.STABILITY_PROFILES[self.stab1 - 1]
        elif self.stability_used == "ANNUAL_CYCLE":
            self.stability = np.round(2.5 * np.cos(self.times * 2. * np.pi / 365.) + 3.5)
            self.stability_str = "Annual cycle"
        else:
            raise ValueError("Unsupported stability profile")

    def set_calculate_params(self):
        self.wind_speed = float(self.windspeed) * np.ones((self.num_timesteps,1))
        if self.wind_type == "CONSTANT_WIND":
            wind_dir = np.zeros((self.num_timesteps,1))
            self.wind_dir_str = "Constant wind"
        elif self.wind_type == "FLUCTUATING_WIND":
            wind_dir = 360.0 * np.random.rand(self.num_timesteps, 1)
            self.wind_dir_str = "Random wind"
        elif self.wind_type == "PREVAILING_WIND":
            wind_dir = -np.sqrt(2) * erfcinv(2.0 * np.random.rand(self.num_timesteps, 1)) * 40.0
            self.wind_dir_str = "Prevailing wind"
        else:
            raise ValueError("Invalid wind type")

        wind_dir = wind_dir + 270 - self.wind_dir_deg
        self.wind_dir = np.mod(wind_dir, 360)

    def run_main_loop(self):
        C1 = np.zeros((len(self.x), len(self.y), len(self.wind_dir)))  # Initialize 3D array for concentrations
        for t in range(len(self.wind_dir)):
            for j in range(int(self.stacks)):
                C = gauss_func(self.Q[j],
                               self.wind_speed[t],
                               self.wind_dir[t],
                               self.x,
                               self.y,
                               self.z,
                               self.stack_x[j],
                               self.stack_y[j],
                               self.H[j],
                               self.Dy,
                               self.Dz,
                               self.stability[t])
                C1[:, :, t] += C
        self.C1 = C1

    def apply_humidification(self):
        if self.humidify == "DRY_AEROSOL":
            pass
            # print("Dry aerosol selected. No humidification applied.")
        elif self.humidify == "HUMIDIFY":
            aerosol = constants.AEROSOL_PROPERTIES[self.aerosol_type]
            mass = (np.pi / 6) * aerosol['rho_s'] * self.dry_size**3
            moles = mass / aerosol['Ms']
            nw = self.RH * aerosol['nu'] * moles / (1 - self.RH)
            mass2 = nw * self.Mw + moles * aerosol['Ms']
            self.C1 = self.C1 * (mass2 / mass)
        else:
            raise ValueError("Invalid humidification option selected.")

    def coord_conversion(self):
        if self.location_type == "EPSG:4326":
            onemap_api_key = gp.get_onemap_token()
            self.stack_xm, self.stack_ym = gp.coors_convert(self.stack_x_orig, self.stack_y_orig, onemap_api_key, '4326to3414')
        elif self.location_type == "EPSG:3414":
            self.stack_xm, self.stack_ym = self.stack_x_orig, self.stack_y_orig
        self.cx, self.cy = gp.calc_center(self.stack_xm, self.stack_ym)
        self.stack_x, self.stack_y = gp.center_coors(self.stack_xm, self.stack_ym, self.cx, self.cy)

    def get_concentration_map(self):
        if self.output == "PLAN_VIEW":
            concentration = np.nanmean(self.C1,axis=2) * 1e6
            data = pd.DataFrame({
                'X': (self.x + self.cx).reshape(-1),
                'Y': (self.y + self.cy).reshape(-1),
                'Concentration_µg': concentration.reshape(-1)
            })
        elif self.output == "HEIGHT_SLICE":
            concentration = np.nanmean(self.C1, axis=2) * 1e6
            data = pd.DataFrame({
                'y': (self.y + self.cy).reshape(-1),
                'Z': self.z.reshape(-1),
                'Concentration_µg': concentration.reshape(-1)
            })
        elif self.output == "SURFACE_TIME":
            data = pd.DataFrame({'Time': self.times, 'MassLoading ($\mu$ g m$^{-3}$)': 1e6*np.squeeze(self.C1[self.y_slice,self.x_slice,:])})
        else:
            raise ValueError("Invalid output type.")
        return data

def run_simulation(**kwargs):
    valid_args = inspect.signature(Simulation).parameters
    valid_kwargs = {k: v for k, v in kwargs.items() if k in valid_args}

    if len(kwargs) > len(valid_kwargs):
        set_trace()
        raise ValueError("Invalid arguments supplied")
    sim = Simulation(**valid_kwargs)
    sim.coord_conversion()
    sim.setup_grid()
    sim.set_stability_profile()
    sim.set_calculate_params()
    sim.run_main_loop()
    sim.apply_humidification()
    return sim.get_concentration_map()

if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support import expected_conditions as expect
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support.ui import Select
    import time
    import os

    options = Options()
    # options.add_argument("--headless")

    runserver_cmd = 'python3 /home/yuan/gaussian_plume/myproject/manage.py runserver &'
    os.system(runserver_cmd)
    time.sleep(2)

    driver = webdriver.Chrome(options = options)
    url = "http://127.0.0.1:8000/"
    driver.get(url)
    # set_trace()
    time.sleep(2)


    fixed_inputs = {
        "RH": "0.9",
        "windspeed": "1.4",
        "days": "50",
        "wind_dir": "225",
        "stacks": "3",
        "aerosol_type": "1",  # SODIUM_CHLORIDE
        "humidify": "1",  # DRY_AEROSOL
        "stab1": "2", # Moderately Unstable
        "stability_used": "1",  # CONSTANT_STABILITY
        "output": "1",  # PLAN_VIEW
        "wind": "3",  # PREVAILING_WIND
        "num_contour": "100",
        "dry_size": str(60 / (10**9))
    }



    # Fill in the form fields programmatically using the dictionary
    for field_name, value in form_inputs.items():
        try:
            WebDriverWait(driver, 120, 1).until(expect.visibility_of_element_located((By.NAME, field_name)))
            element = driver.find_element(By.NAME, field_name)

            if field_name in ['stacks', 'stability_used', 'stab1', 'output', 'wind', 'aerosol_type', 'humidify']:
                select = Select(element)
                select.select_by_value(value)
                # set_trace()
            else:
                element.clear()  # Clear existing text if any
                element.send_keys(value)
        except Exception as e:
            print(f"Error filling field '{field_name}': {e}")

    # Click the "Run Simulation" button
    try:
        run_simulation_button = driver.find_element(By.XPATH, '//*[@id="submission_button"]')
        run_simulation_button.click()
        print("Simulation submitted successfully!")
    except Exception as e:
        print(f"Error clicking 'Run Simulation' button: {e}")
    WebDriverWait(driver, 120, 1).until(expect.visibility_of_element_located((By.XPATH, "//input[@type='button' and @value='Go Back']")))

    data = run_simulation(**form_inputs)
    data1 = pd.read_csv('~/tmp.csv')
    data2 = pd.merge(data1, data, on = ['X', 'Y'])
    max_err = (data2['Concentration_µg_x'] - data2['Concentration_µg_y']).abs().max()
    assert np.isclose(max_err, 0, atol = 1e-10)
    print(f"\n\n Test passed! max error: {max_err}\n\n")
    # time.sleep(3)
    driver.quit()
    set_trace()
    kill_server = f'pkill -f  "python3 /home/yuan/gaussian_plume/myproject/manage.py runserver"'
    os.system(kill_server)