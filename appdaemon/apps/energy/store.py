import hassapi as hass
from enum import Enum
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta
from energiledd import energiledd
import json
import sensors

# Declare Class 
class Store(hass.Hass):
    def initialize(self):

        """ ------------ Listners -------------- """
        # send notification when kwh prize goes up
        self.listen_state(self.notify_high_prize, sensors.electricity_price_eigeland_50_with_fees)


    """  SETTERS  """
    
    def set_daily_prize_accumulated_with_fees(self, price):
        self.set_value(sensors.daily_prize_accumulated_with_fees, round(price, 2))

    def set_monthly_prize_accumulated_with_fees(self, price):
        self.set_value(sensors.monthly_prize_accumulated_with_fees, round(price, 2))

    def set_yearly_prize_accumulated_with_fees(self, price):
        self.set_value(sensors.yearly_prize_accumulated_with_fees, round(price, 2))

    def set_kwh_price_with_fees(self, price):
        self.set_value(sensors.electricity_price_eigeland_50_with_fees, round(price, 2))

    def set_daily_accumulated_kwh_price_with_compensation(self, price):
        self.set_value(sensors.daily_prize_accumulated_with_compensation, round(price, 2))

    def set_kwh_price_with_compensation(self, price):
        self.set_value(sensors.electricity_price_eigeland_50_with_compensation, round(price, 2))

    def set_energiledd(self, price):
        self.set_value(sensors.energiledd, round(price, 2))


    """  GETTERS  """

    def get_daily_prize_accumulated_with_fees(self):
        return float(self.get_state(sensors.daily_prize_accumulated_with_fees, default=0))
    
    def get_monthly_prize_accumulated_with_fees(self):
        return float(self.get_state(sensors.monthly_prize_accumulated_with_fees, default=0))

    def get_yearly_prize_accumulated_with_fees(self):
        return float(self.get_state(sensors.yearly_prize_accumulated_with_fees, default=0))

    def get_daily_kwh_price_with_compensation(self):
        return float(self.get_state(sensors.daily_prize_accumulated_with_compensation, default=0))

    def get_kwh_price_with_compensation(self):
        return float(self.get_state(sensors.electricity_price_eigeland_50_with_compensation, default=0))

    def get_energiledd(self, price):
        return float(self.get_state(sensors.energiledd, default=0))


    """ -----------  Notification ------------- """
    def notify_high_prize(self, entity, attribute, old, new, kwargs):
        if not new:
            return
        if float(new) > 7.0 and new > old:
            self.notify("Prisen er for øyeblikket {0}kWh inkludert moms og energiledd på {1} øre".format(new, energiledd.energy_factor(self)), title = "Høy Strømpris")
            self.log("high prize " + str(new))

    def notify_price_is_negative(self, price):
        self.notify("BILLIG strøm. Nå tjener vi penger {0}kWh".format(price), title = "Negativ Strømpris")
        self.log("Negativ Strømpris " + str(price))