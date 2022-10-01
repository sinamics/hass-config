import hassapi as hass
from enum import Enum
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta
import json
import sensors
import constants

###
# 
#  (gj.snitt områdepris – terskelpris på 70 øre/kwh) * komp.grad på 0,80 * event. Mva. 1,25
#
###


# Declare Class
class Compensation(hass.Hass):
    def initialize(self):
        self.avg_price_today = 0
        self.tibber_attributes = 0

        # Power Consumption
        self.daily_consumption = 0
        self.monthly_consumption = 0

        # NOK compensation
        self.daily_compensation = 0
        self.monthly_compensation = 0

        # Listners
        self.listen_state(self.avg_price_handler, sensors.sensor_electricity_price, attribute="all", immediate=True)
        self.listen_state(self.montly_power_consumption_handler, sensors.kwh_consumption_thismonth, immediate=True)
        self.listen_state(self.daily_power_consumption_handler, sensors.kwh_consumption_today, immediate=True)

        # Run every month at first day 00:00
        today = date.today()
        first_day = today.replace(day=1) + relativedelta(months=1)
        run_date = first_day.strftime("%Y-%m-%d %H:%M:%S")
        self.run_at(self.run_every_month, run_date)

    """ ------------ Listners -------------- """
    def avg_price_handler(self, entity, attribute, old, new, kwargs):
        self.avg_price_today = new["attributes"]["average"]

    def daily_power_consumption_handler(self, entity, attribute, old, new, kwargs):
        if new == "unavailable":
            return
        self.daily_consumption = new
        self.daily()

    def montly_power_consumption_handler(self, entity, attribute, old, new, kwargs):
        if new == "unavailable":
            return
            
        self.monthly_consumption = new
        self.monthly()
        
    """ ------------ Methods -------------- """
    def kwh_compensation(self):
        return self.calculate_compensation_amount(self.avg_price_today, 1)
    
    def daily(self):
        if self.avg_price_today > constants.COMPENSATION_THRESHOLD:
            self.daily_compensation = self.calculate_compensation_amount(self.avg_price_today, self.daily_consumption)
            # self.daily_consumption = 18.2
            # self.daily_compensation = 36.2
        self.set_state(sensors.energy_compensation_daily, state = round(self.daily_compensation, 2), attributes = {"compensation": round(self.daily_compensation,2), "unit_of_measurement": "NOK"})

    def monthly(self):
        # Opening JSON file
        with open(constants.JSON_AVG_PRICE_FILE, 'r') as openfile:   
            # Reading from json file
            avg_monthly_history = json.load(openfile)

        # number of days stored
        days = len(avg_monthly_history)

        if date.today().day == 1 and days > 1:
            avg_monthly_history = {"day1":0}

        avg_monthly_history["day{}".format(date.today().day)] = self.avg_price_today

        # calculate this month avg prize
        month_avg = 0
        for item in avg_monthly_history:
            month_avg += avg_monthly_history[item]

        if days > 1:
            month_avg = month_avg / days # len has 1 index
 
        # # calculate compensation level so far this month.
        if month_avg > constants.COMPENSATION_THRESHOLD:
            self.monthly_compensation = self.calculate_compensation_amount(month_avg, self.monthly_consumption)

        with open(constants.JSON_AVG_PRICE_FILE, "w") as outfile:
            outfile.write(json.dumps(avg_monthly_history))

        # update state
        self.set_state(sensors.energy_compensation_this_month, state = round(self.monthly_compensation, 2), attributes = {"compensation": round(self.monthly_compensation,2), "unit_of_measurement": "NOK"})
        # set avg price so far this month
        self.set_value(sensors.monthly_avg_kwh_price, round(month_avg,3))
        
    def calculate_compensation_amount(self, avg_price, kwh_consumption):
        rest = avg_price - constants.COMPENSATION_THRESHOLD
        compensation_amount = constants.COMPENSATION_LEVEL * rest / 100
        return compensation_amount * float(kwh_consumption)

    def run_every_day(self, kwargs):
        # run cleanup functions and shift numbers for new hour / min / day
        self.log("compensation cleanup function run_every_day " + str(datetime.now()))
        self.daily_compensation = 0

    def run_every_month(self, kwargs):
        # run cleanup functions and shift numbers for new hour / min / day
        self.log("compensation cleanup function run_every_month " + str(datetime.now()))
