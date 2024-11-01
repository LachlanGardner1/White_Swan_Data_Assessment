from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import pandas as pd
import logging
import logging.config
import yaml
import traceback
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

def define_race(current_race, race_number, url, race_time):
    #Common method to add race_number, url and race_time to current_race
    current_race["Race Number"] = race_number
    current_race["Race URL"] = url
    current_race["Race Start"] = race_time
    return current_race

def main(logger, args):
    try:
        logger.info("Begin Data Scraping")
        url = 'https://www.swiftbet.com.au/racing'
        if args.date == "tomorrow":
            tomorrows_date = datetime.today().date() + timedelta(days=1)
            url = f"{url}/all/{tomorrows_date}"
        #Open URL and wait for presence of track names
        try:
            driver.get(url)
            driver.maximize_window()
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "e17e4d890.exx10s30.css-lz7t06-Text-Text-Link-Link-MeetingItem-MeetingItem__MeetingName-MeetingItem.ea6hjv30")))
        except TimeoutException as e:
            logger.error(e)
            logger.error("Page took too long to load")
            raise e
        
        #find number of tracks
        number_of_tracks = len(driver.find_elements(By.CLASS_NAME, "e17e4d890.exx10s30.css-lz7t06-Text-Text-Link-Link-MeetingItem-MeetingItem__MeetingName-MeetingItem.ea6hjv30"))
        
        races_list = []
        index = 0
        for i in range(number_of_tracks):

            #Find all tracks and races to refresh the DOM
            all_tracks = driver.find_elements(By.CLASS_NAME, "e17e4d890.exx10s30.css-lz7t06-Text-Text-Link-Link-MeetingItem-MeetingItem__MeetingName-MeetingItem.ea6hjv30")
            all_races = driver.find_elements(By.CLASS_NAME, "e15267q10.css-dr0t2h-TableRow-TableRow-TableRow-RacesRow-RacesRow-RacesRow.e17s2h8j0")
            
            #Select current race track
            track = all_tracks[index]
            race_track = track.text
            
            #Select all races for current track
            races = all_races[index].find_elements(By.TAG_NAME, 'a')
            race_number = 1
            for race in races:
                logger.debug(f"Beginning scrape for race_track: {race_track}")
                current_race = {}

                #Add Track Name, Race Number, Race URL, and Race Time for current track
                current_race["Track Name"] = race_track
                race_url = race.get_attribute('href')
                if len(race.find_elements(By.XPATH, ".//div[@type='default']")) > 0:
                    races_list.append(define_race(current_race, race_number, race_url, race.text))
                else:
                    races_list.append(define_race(current_race, race_number, race_url,"Race Completed"))
                race_number += 1
            
            index += 1

        logger.debug(races_list)

        if races_list != []:
            #Transform races_list to dataframe and export to CSV as race_data.csv
            df_races_data = pd.DataFrame(races_list)
            df_races_data.to_csv(f'data/races_data_{args.date}.csv', index=False)

            logger.info("Races data retrieved and stored into races_data.csv")
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
