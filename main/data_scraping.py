from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import regex as re
from time import sleep

url = 'https://www.swiftbet.com.au/racing/all/2024-10-30'
path = '../driver/chromedriver.exe'
service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)

def main():
    try:
        number_of_titles = len(driver.find_elements(By.CLASS_NAME, "e17e4d890.exx10s30.css-lz7t06-Text-Text-Link-Link-MeetingItem-MeetingItem__MeetingName-MeetingItem.ea6hjv30"))
        all_races = driver.find_elements(By.CLASS_NAME, "e15267q10.css-dr0t2h-TableRow-TableRow-TableRow-RacesRow-RacesRow-RacesRow.e17s2h8j0")
        races_dictionary = {}
        index = 0
        for i in  range(number_of_titles):
            all_titles = driver.find_elements(By.CLASS_NAME, "e17e4d890.exx10s30.css-lz7t06-Text-Text-Link-Link-MeetingItem-MeetingItem__MeetingName-MeetingItem.ea6hjv30")
            title = all_titles[index]
            race_title = title.text
            
            current_race = {}
            current_race[race_title] = {}
            
            races = all_races[index].find_elements(By.TAG_NAME, 'a')
            race_number = 1
            for race in races:
                if len(race.find_elements(By.XPATH, ".//div[@type='default']")) > 0:
                    current_race[race_title][f"Race {race_number}"] = {"race_url": race.get_attribute('href'), "race_time": race.text}
                else:
                    current_race[race_title][f"Race {race_number}"] = {"race_url": race.get_attribute('href'), "race_time": "Race Completed"}
                race_number += 1
            races_dictionary.update(current_race)
            index += 1
        races_df = pd.DataFrame.from_dict(races_dictionary)
        print(races_df.describe())
        print(races_df.columns)
        races_df.to_csv('../data/out.csv', index=False) 
    except Exception as e:
        print(e)
        print("error during processing")
if __name__ == '__main__':
    try:
        driver.get(url)
        sleep(15)
        main()
        driver.quit()
    except Exception as e:
        print(e)
        print("an error has occured")
