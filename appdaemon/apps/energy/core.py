import hassapi as hass
from enum import Enum
# import voluptuous as vol
# import helper as vol_help
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta
from energiledd import energiledd
import json
import sensors
import constants

# Declare Class 
class Core(hass.Hass):
  def initialize(self):
    self.compensation_api_class = self.get_app("compensation")
    self.store_class = self.get_app("store")

    self.cost_daily = self.store_class.get_daily_prize_accumulated_with_fees()
    self.cost_monthly = self.store_class.get_monthly_prize_accumulated_with_fees()
    self.cost_yearly = self.store_class.get_yearly_prize_accumulated_with_fees()
    self.kwh_consumption = self.store_class.get_total_accumulated_kwh()
    self.kwh_consumption_today = self.store_class.get_total_accumulated_kwh_today()
    self.kwh_consumption_this_month = self.store_class.get_total_accumulated_kwh_month()

    # # kwh usage
    self.kwh_power = 0
    self.kwh_power_min = self.store_class.get_kwh_min()
    self.kwh_power_max = self.store_class.get_kwh_max()
    self.kwh_prize = 0
    self.watt_usage = 0

    # # Run task every hour
    self.run_hourly(self.run_every_hour, time(0, 0, 0))

    # # Run every day at 23:59
    self.run_daily(self.run_every_day, time(23, 59, 0))

    # # Run every month at first day 00:00
    today = date.today()
    first_day = today.replace(day=1) + relativedelta(months=1)
    runt_date = first_day.strftime("%Y-%m-%d %H:%M:%S")
    self.run_at(self.run_every_month, runt_date)
    
    self.listen_state(self.watt_consumption_handler, sensors.sensor_watt_consumption, immediate=True)
    self.listen_state(self.kwh_price_handler, sensors.sensor_electricity_price, immediate=True)
    
  def kwh_price_handler(self, entity, attribute, old, new, kwargs):
      """Event handler: kwh price changed"""
      if not new:
          return
      self.kwh_prize = float(new)

  def watt_consumption_handler(self, entity, attribute, old, new, kwargs):
      """Event handler: watt consumption changed"""
      # do not continue if watt reading is 0
      if not new:
          return
      self.watt_usage = float(new)

      self.watt_kwh_consumption()
      # call price calculation when watt has changed
      self.prize_calculation()

  def watt_kwh_consumption(self):

      kwh_usage = self.watt_usage / 1000

      # set min max
      if self.kwh_power_min == 0:
          self.kwh_power_min = kwh_usage
          self.kwh_power_max = kwh_usage

      if kwh_usage < self.kwh_power_min:
        self.kwh_power_min = kwh_usage

      if kwh_usage > self.kwh_power_max:
        self.kwh_power_max = kwh_usage
      
      self.store_class.set_kwh_min(round(self.kwh_power_min, 2))
      self.store_class.set_kwh_max(round(self.kwh_power_max, 2))
      
      self.store_class.set_kwh_active_usage(round(kwh_usage, 2))
      # kwh usage now
        
      # convert to kwh usage
      self.kwh_consumption +=  self.watt_usage / 3600 * 10 / 1000
      self.kwh_consumption_today +=  self.watt_usage / 3600 * 10 / 1000
      self.kwh_consumption_this_month +=  self.watt_usage / 3600 * 10 / 1000

      #self.kwh_consumption = 3615.07
      self.store_class.set_total_accumulated_kwh(self.kwh_consumption)
      self.store_class.set_total_accumulated_kwh_today(round(self.kwh_consumption_today, 2))
      self.store_class.set_total_accumulated_kwh_month(round(self.kwh_consumption_this_month, 2))
      
      # self.log(self.kwh_consumption)

  def prize_calculation(self):
    """Event handler: watt consumption changed"""
    if self.kwh_prize == 0:
      return

    # prize with energy factor based on time of day
    # Add VAT to the kwh price and add energiledd that already has VAT from agder energi.
    kwh_prize_with_energyfactory = float(self.kwh_prize) * constants.VAT + energiledd.energy_factor(self)

    # spred watts to each seconds and multiply by the api call time diffrence.
    # spread to 10sec interval as this is the api call time from tibber.
    self.watt_pr_sec_prize = kwh_prize_with_energyfactory / 60 / 60 * 10

    # calcualte cost based on 10min prize and watt usage. Divide watt usage by 1k to get kwh value
    self.cost_daily += self.watt_pr_sec_prize * (self.watt_usage / 1000)
    self.cost_monthly += self.watt_pr_sec_prize * (self.watt_usage / 1000)
    self.cost_yearly += self.watt_pr_sec_prize * (self.watt_usage / 1000)
    # self.cost_daily = 77.25
    
    # set state with updated prize
    self.store_class.set_daily_prize_accumulated_with_fees(round(self.cost_daily, 2))
    self.store_class.set_monthly_prize_accumulated_with_fees(round(self.cost_monthly, 2))
    self.store_class.set_yearly_prize_accumulated_with_fees(round(self.cost_yearly, 2))
    self.store_class.set_energiledd(round(energiledd.energy_factor(self), 2))
    self.store_class.set_kwh_price_with_fees(round(kwh_prize_with_energyfactory, 2))
 
    # create new sensor with energy price and compensation substracted
    self.store_class.set_daily_accumulated_kwh_price_with_compensation(round(self.cost_daily - self.compensation_api_class.daily_compensation, 2))

    # calculate current kwh price with compensation
    kwh_vat = float(self.kwh_prize) / 100 * 25
    kwh_price_with_compensation = (float(self.kwh_prize) - self.compensation_api_class.kwh_compensation()) + (float(self.kwh_prize) / 100 * 25) + energiledd.energy_factor(self)

    # set_kwh_price_with_compensation
    self.store_class.set_kwh_price_with_compensation(round(kwh_price_with_compensation, 2))

  """ -----------  Interval ------------- """
  def run_every_hour(self, kwargs):
    # run cleanup functions and shift numbers for new hour / min / day
    self.log("function run_every_hour " + str(datetime.now()))
    

  def run_every_day(self, kwargs):
    # run cleanup functions and shift numbers for new hour / min / day 
    self.log("cleanup function run_every_day " + str(datetime.now()))
    self.store_class.set_kwh_consumption_lastday(round(self.kwh_consumption_today, 2))
    self.store_class.cost_lastday(round(self.cost_daily, 2))
    self.cost_daily = 0
    self.kwh_consumption_today = 0


  def run_every_month(self, kwargs):
    # run cleanup functions and shift numbers for new hour / min / day
    self.log("cleanup function run_every_month " + str(datetime.now()))
    self.store_class.set_kwh_consumption_lastmonth(round(self.kwh_consumption_this_month, 2))

    self.cost_monthly = 0
    self.kwh_consumption_this_month = 0