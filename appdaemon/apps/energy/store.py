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
        self.listen_state(self.notify_high_prize, sensors.kwh_price_with_fees)

    """  SETTERS  """
    def set_cost_lastday(self, price):
        self.set_value(sensors.cost_lastday, round(price, 4))

    def set_kwh_consumption_lastday(self, price):
        self.set_value(sensors.kwh_consumption_lastday, round(price, 4))

    def set_kwh_active_usage(self, price):
        self.set_value(sensors.kwh_active_usage, round(price, 4))

    def set_kwh_min(self, price):
        self.set_value(sensors.kwh_min, round(price, 4))

    def set_kwh_max(self, price):
        self.set_value(sensors.kwh_max, round(price, 4))

    def set_kwh_consumption_lastmonth(self, price):
        self.set_value(sensors.kwh_consumption_lastmonth, round(price, 4))

    def set_total_accumulated_kwh_month(self, price):
        self.set_value(sensors.kwh_consumption_thismonth, round(price, 4))

    def set_total_accumulated_kwh_today(self, price):
        self.set_value(sensors.kwh_consumption_today, round(price, 4))

    def set_total_accumulated_kwh(self, price):
        self.set_value(sensors.kwh_consumption_total, round(price, 4))

    def set_daily_prize_accumulated_with_fees(self, price):
        self.set_value(sensors.daily_prize_accumulated_with_fees, round(price, 2))

    def set_monthly_prize_accumulated_with_fees(self, price):
        self.set_value(sensors.monthly_prize_accumulated_with_fees, round(price, 2))

    def set_yearly_prize_accumulated_with_fees(self, price):
        self.set_value(sensors.yearly_prize_accumulated_with_fees, round(price, 2))

    def set_kwh_price_with_fees(self, price):
        self.set_value(sensors.kwh_price_with_fees, round(price, 2))

    def set_daily_accumulated_kwh_price_with_compensation(self, price):
        self.set_value(sensors.daily_prize_accumulated_with_compensation, round(price, 2))

    def set_kwh_price_with_compensation(self, price):
        self.set_value(sensors.kwh_price_with_compensation, round(price, 2))

    def set_energiledd(self, price):
        self.set_value(sensors.energiledd, round(price, 2))


    """  GETTERS  """
    def get_cost_lastday(self):
        return float(self.get_state(sensors.cost_lastday, default=0))

    def get_kwh_consumption_lastday(self):
        return float(self.get_state(sensors.kwh_consumption_lastday, default=0))

    def get_kwh_min(self):
        return float(self.get_state(sensors.kwh_min, default=0))

    def get_kwh_max(self):
        return float(self.get_state(sensors.kwh_max, default=0))

    def get_kwh_consumption_lastmonth(self):
        return float(self.get_state(sensors.kwh_consumption_lastmonth, default=0))

    def get_total_accumulated_kwh_month(self):
        return float(self.get_state(sensors.kwh_consumption_thismonth, default=0))

    def get_total_accumulated_kwh_today(self):
        return float(self.get_state(sensors.kwh_consumption_today, default=0))

    def get_total_accumulated_kwh(self):
        return float(self.get_state(sensors.kwh_consumption_total, default=0))

    def get_daily_prize_accumulated_with_fees(self):
        return float(self.get_state(sensors.daily_prize_accumulated_with_fees, default=0))
    
    def get_monthly_prize_accumulated_with_fees(self):
        return float(self.get_state(sensors.monthly_prize_accumulated_with_fees, default=0))

    def get_yearly_prize_accumulated_with_fees(self):
        return float(self.get_state(sensors.yearly_prize_accumulated_with_fees, default=0))

    def get_daily_kwh_price_with_compensation(self):
        return float(self.get_state(sensors.daily_prize_accumulated_with_compensation, default=0))

    def get_kwh_price_with_compensation(self):
        return float(self.get_state(sensors.kwh_price_with_compensation, default=0))

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