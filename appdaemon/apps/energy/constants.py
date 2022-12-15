
##### constants #####

# Energy factor from vendor
ENERGY_FACTOR_DAY = 0.5251
ENERGY_FACTOR_NIGHT = 0.4251

VAT=1.25

# Norwegian compensation numbers from the goverment. 
COMPENSATION_THRESHOLD=0.70 # øre
COMPENSATION_LEVEL=90 # %

# file to store every days average kwh price
JSON_AVG_PRICE_FILE="/config/appdaemon/apps/energy/avg_day_price.json"
TOP_THREE_KWH_HOURS_FILE="/config/appdaemon/apps/energy/topthreehours.txt"
TOP_THREE_KWH_HOURS_RESET_FILE="/config/appdaemon/apps/energy/topthreehours_reset.txt"

# https://tibber.com/no/magazine/power-hacks/ny-nettleie-del-1?utm_source=googleadwords_int&utm_medium=cpc&utm_content=10309245966_102363939813_531418368653&utm_id=g_&keyword=&gclid=Cj0KCQjwjbyYBhCdARIsAArC6LLlu8b5-jYqS2Shveyf7S-GseiMPZ2IZER9OsEKiMzXxKiHJ2G3NqsaAq-HEALw_wcB
FASTLEDD = [
    {"name":"trinn1", "prize": 245, "max_kwh": 2},
    {"name":"trinn2", "prize": 315, "max_kwh": 5},
    {"name":"trinn3", "prize": 440, "max_kwh": 10},
    {"name":"trinn4", "prize": 815, "max_kwh": 15},
    {"name":"trinn5", "prize": 1500, "max_kwh": 20},
    {"name":"trinn6", "prize": 2188, "max_kwh": 25},
    {"name":"trinn7", "prize": 4375, "max_kwh": 50},
    {"name":"trinn8", "prize": 6563, "max_kwh": 75},
    {"name":"trinn9", "prize": 8750, "max_kwh": 100}
]
