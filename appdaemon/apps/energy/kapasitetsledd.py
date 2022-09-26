import hassapi as hass
from enum import Enum
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta
import sensors
import constants

# Declare Class
class kapasitetsledd(hass.Hass):
    def initialize(self):
        self.watt_peak = 0
        self.watt_peak_cost = 0
        
        # run on initial load
        self.peak_calculation()
        
        # update whenever new peak is updated from Tibber 
        self.listen_state(self.peak_handler, sensors.monthly_peak_hour_consumption_eigeland_50, immediate=True)

    def peak_handler(self, entity, attribute, old, new, kwargs):
        """Event handler: watt peak changed"""
        if new == "unavailable" or new == None:
            return

        # send notification if peak is higher than old value
        if old != None and new > old:
            self.notify("Ny strøm peak registrert {}kWh".format(new))

        self.watt_peak = float(new)
        self.peak_calculation()

    def peak_calculation(self):
        for level in constants.FASTLEDD:
            if level["max_kwh"] >= self.watt_peak:
                self.watt_peak_cost = level["prize"]
                self.set_state(sensors.monthly_power_peak_prize, state = round(self.watt_peak_cost, 2), attributes={"unit_of_measurement": "NOK"})
                break