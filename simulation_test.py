
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
    options.add_argument("--headless")

    runserver_cmd = 'python3 /home/yuan/gaussian_plume/myproject/manage.py runserver &'
    os.system(runserver_cmd)
    time.sleep(2)

    driver = webdriver.Chrome(options = options)
    url = "http://127.0.0.1:8000/"
    driver.get(url)
    time.sleep(2)


    # Fill in the form fields programmatically using the dictionary
    for field_name, value in form_inputs.items():
        try:
            WebDriverWait(driver, 120, 1).until(expect.visibility_of_element_located((By.NAME, field_name)))
            element = driver.find_element(By.NAME, field_name)

            if field_name in ['stacks', 'stability_used', 'stab1', 'output', 'wind', 'aerosol_type', 'humidify']:
                select = Select(element)
                select.select_by_value(value)
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
    kill_server = f'pkill -f  "python3 /home/yuan/gaussian_plume/myproject/manage.py runserver"'
    os.system(kill_server)
