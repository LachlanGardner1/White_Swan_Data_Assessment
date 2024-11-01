# White_Swan_Data_Assessment
Steps for installation and running of Scripts
1. install requirements.txt - pip install -r requirements.txt
2. Update the global variable driver_path in both python files to relevant chromedriver for your operating system eg. 'driver/chromedriver-win64.exe'
4. run data_scraping.py from root directory with the argument of either today or tomorrow eg. - python main/data_scraping.py tomorrow
5. After completion, run bot_automation.py from root directory with the argument of either today or tomorrow eg. - python main/bot_automation.py tomorrow