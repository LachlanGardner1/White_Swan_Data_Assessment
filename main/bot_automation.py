from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import pandas as pd
from random import randint
import logging
import logging.config
import yaml
import traceback
from time import sleep
import argparse
from datetime import datetime, timedelta

#Update chromdriver path to relevant operating system if necessary
driver_path = 'driver/chromedriver-win64.exe'
service = Service(executable_path=driver_path)
options = webdriver.ChromeOptions()
options.add_argument("log-level=3")
driver = webdriver.Chrome(options=options, service=service)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("date", help="Enter either today or tomorrow", choices=['today', 'tomorrow'])
    args = parser.parse_args()
    return args

def get_logger(config):
    logging.config.dictConfig(config)
    logger = logging.getLogger("development")
    return logger

def check_price(price):
    if price == '':
        return 'SCRATCHED'
    elif price == 'SP':
        return 'N/A'
    return price

def main(logger, args):
    try:
        logger.info("Begin Bot Automation")
        
        #select url and read races data csv based on date selection
        url = 'https://www.swiftbet.com.au/racing'
        if args.date == "tomorrow":
            tomorrows_date = datetime.today().date() + timedelta(days=1)
            url = f"{url}/all/{tomorrows_date}"
        
        races_df = pd.read_csv(f'data/races_data_{args.date}.csv')
        
        #select random row
        random_row = randint(0, len(races_df.index))
        selected_row = races_df.iloc[random_row]

        #get track name and number and race type to determine where to click
        track_name = selected_row['Track Name'].split(" ")
        track_name = track_name[:-1]
        track_name = "-".join(track_name).lower()
        race_number = selected_row['Race Number']
        race_type = selected_row['Race URL'].split("racing/")[1].split("/")[0]
        logging.info(f"Clicking on randomly selected race track: {track_name}, race number: {race_number}, race type: {race_type}")

        all_racers = []
        try:
            #launch url and wait for loading
            driver.get(url)
            driver.maximize_window()
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH,  f"//*[contains(@href, '{track_name}') and contains(@href, 'race-{race_number}') and contains(@href, '{race_type}')]")))
            
            #click randomly selected race and wait for page to load
            driver.find_element(By.XPATH,  f"//*[contains(@href, '{track_name}') and contains(@href, 'race-{race_number}') and contains(@href, '{race_type}')]").click()
            sleep(10)
        except TimeoutException as e:
            logger.error(e)
            logger.error("Page took too long to load")
            raise e

        #find amount of racers
        all_racers = driver.find_elements(By.XPATH, "//div[contains(@data-fs-title, 'racer_name')]")
        racers_count = len(all_racers)
        performed_bets = []
        index = 0
        for i in range(racers_count):
            current_racer = {}
            
            #find all racers elements to refresh the DOM
            all_racers = driver.find_elements(By.XPATH, "//div[contains(@data-fs-title, 'racer_name')]")

            #Get fixed win and fixed place prices for all racers
            fixed_win_prices = driver.find_elements(By.XPATH, "//div[contains(@data-fs-title, '0-price_button')]")
            fixed_place_prices = driver.find_elements(By.XPATH, "//div[contains(@data-fs-title, '1-price_button')]")

            #select fixed win price for current racer
            fixed_win_price = fixed_win_prices[index].find_element(By.TAG_NAME, "span").text
            fixed_win_price = check_price(fixed_win_price)
                
            #select fixed place price for current racer
            fixed_place_price = fixed_place_prices[index].find_element(By.TAG_NAME, "span").text
            fixed_place_price = check_price(fixed_place_price)

            #store current racer information in performed_bets
            current_racer['Racer'] = all_racers[index].text
            current_racer['Fixed Win Price'] = fixed_win_price
            current_racer['Fixed Place Price'] = fixed_place_price
            
            logger.debug(f"appending betting information {all_racers[index].text}")
            performed_bets.append(current_racer)
            index += 1

        logger.debug(performed_bets)

        if performed_bets != []:
            #convert performed_bets into dataframe and export to CSV with track_name and race_number
            df_performed_bets = pd.DataFrame(performed_bets)
            df_performed_bets.to_csv(f'data/{track_name}-race-{race_number}.csv', index=False) 
        
            logger.info(f"Performed bets retrieved and stored into {track_name}-race-{race_number}.csv")

        driver.quit()
    except Exception as e:
        driver.quit()
        logger.error(e)
        logger.error("error during processing")
        raise e

if __name__ == '__main__':
    #get logger config and load logger
    with open('config/logger_config.yaml','rt') as f:
            config=yaml.safe_load(f.read())
    logger = get_logger(config)
    try:
        args = parse_args()
        main(logger, args)
    except Exception as e:
        logging.error(traceback.format_exc())
        logger.error(e)
        logger.error("an error has occured")
