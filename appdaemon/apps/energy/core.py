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

    self.cost_daily = float(self.get_state(sensors.daily_prize_accumulated_with_fees, default=0))
    self.cost_monthly = float(self.get_state(sensors.monthly_prize_accumulated_with_fees, default=0))
    self.cost_yearly = float(self.get_state(sensors.yearly_prize_accumulated_with_fees, default=0))

    self.kwh_consumption = float(self.get_state(sensors.kwh_consumption_total, default=0))
    self.kwh_consumption_today = float(self.get_state(sensors.kwh_consumption_today, default=0))
    self.kwh_consumption_this_month = float(self.get_state(sensors.kwh_consumption_thismonth, default=0))
    self.kwh_consumption_this_year = float(self.get_state(sensors.kwh_consumption_thisyear, default=0))

    self.kwh_consumption_startofday = float(self.get_state(sensors.kwh_consumption_startofday, default=0))
    
    # # kwh usage
    self.kwh_power = 0
    self.kwh_power_min = float(self.get_state(sensors.kwh_min, default=0))
    self.kwh_power_max = float(self.get_state(sensors.kwh_max, default=0))
    self.kwh_prize = 0
    self.watt_usage = 0
    self.total_kwh_usage = 0

    # # Run task every hour
    self.run_hourly(self.run_every_hour, time(0, 0, 0))

    # # Run every day at 23:59
    self.run_daily(self.run_every_day, time(23, 59, 0))

    # # Run every month at first day 00:00
    today = date.today()
    first_day = today.replace(day=1) + relativedelta(months=1)
    runt_date = first_day.strftime("%Y-%m-%d %H:%M:%S")
    self.run_at(self.run_every_month, runt_date)
    
    # run every year
    first_d = today.replace(day=1, month=1) + relativedelta(years=1)
    runt_yearly = first_d.strftime("%Y-%m-%d %H:%M:%S")
    self.run_at(self.run_every_year, runt_yearly)

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
      
      self.set_value(sensors.kwh_min, round(self.kwh_power_min, 2))
      self.set_value(sensors.kwh_max, round(self.kwh_power_max, 2))

      self.set_value(sensors.kwh_active_usage, round(kwh_usage, 2))
      # kwh usage now

      # accumulate kwh usage
      self.kwh_consumption_startofday = float(self.get_state(sensors.kwh_consumption_startofday, default=0))
      self.kwh_consumption_startofmonth = float(self.get_state(sensors.kwh_consumption_startofmonth, default=0))
      self.kwh_consumption_startofyear = float(self.get_state(sensors.kwh_consumption_startofyear, default=0))

      self.total_kwh_usage = float(self.get_state(sensors.kamstrup_power_import_total, default=0))
      self.kwh_consumption = self.total_kwh_usage
      # self.log(self.kwh_consumption_startofday)
      # self.kwh_consumption_startofday = 8863.66
      # self.set_value(sensors.kwh_consumption_startofday, 8863.66)

      # manipulate consumption
      # self.set_value(sensors.kwh_consumption_startofmonth, round(12478.66, 2))

      self.kwh_consumption_today = self.total_kwh_usage - self.kwh_consumption_startofday
      self.kwh_consumption_this_month = self.total_kwh_usage - self.kwh_consumption_startofmonth
      self.kwh_consumption_this_year = self.total_kwh_usage - self.kwh_consumption_startofyear

      ############## using total measurement from ams instead ###############
      # self.kwh_consumption +=  self.watt_usage / 3600 * 10 / 1000
      # self.kwh_consumption_today +=  self.watt_usage / 3600 * 10 / 1000
      # self.kwh_consumption_this_month +=  self.watt_usage / 3600 * 10 / 1000
      # self.kwh_consumption_today = 12.95
      # self.kwh_consumption_this_month = 245.0 
      # self.kwh_consumption = 7839
      # 

      self.set_value(sensors.kwh_consumption_total, round(int(self.kwh_consumption), 4))
      self.set_value(sensors.kwh_consumption_today, round(self.kwh_consumption_today, 2))
      self.set_value(sensors.kwh_consumption_thismonth, round(self.kwh_consumption_this_month, 2))
      self.set_value(sensors.kwh_consumption_thisyear, round(self.kwh_consumption_this_year, 2))
      

  def prize_calculation(self):
    """Event handler: watt consumption changed"""
    if self.kwh_prize == 0:
      return
    # prize with energy factor based on time of day
    # Add VAT to the kwh price and add energiledd that already has VAT from agder energi.
    kwh_prize_with_energyfactory = (float(self.kwh_prize) * constants.VAT) + energiledd.energy_factor(self)

    # spred watts to each seconds and multiply by the api call time diffrence.
    # spread to 10sec interval. AMS publish new data every 10sec
    self.watt_pr_sec_prize = kwh_prize_with_energyfactory / 60 / 60 * 10
    
    # calcualte cost based on 10min prize and watt usage. Divide watt usage by 1k to get kwh value
    self.cost_daily += self.watt_pr_sec_prize * (self.watt_usage / 1000)
    self.cost_monthly += self.watt_pr_sec_prize * (self.watt_usage / 1000)
    # self.cost_monthly = 326.98
    self.cost_yearly += self.watt_pr_sec_prize * (self.watt_usage / 1000)
    # self.cost_daily = 17.72
    # self.cost_yearly = 17743.0
    # set state with updated prize
    # self.set_value(sensors.cost_lastmonth, round(3738.54, 2))

    self.set_value(sensors.kwh_price, round(self.kwh_prize, 2))
    self.set_value(sensors.daily_prize_accumulated_with_fees, round(self.cost_daily, 2))
 
    self.set_value(sensors.monthly_prize_accumulated_with_fees, round(self.cost_monthly, 2))
    self.set_value(sensors.yearly_prize_accumulated_with_fees, round(self.cost_yearly, 2))
    self.set_value(sensors.energiledd, round(energiledd.energy_factor(self), 2))
    self.set_value(sensors.kwh_price_with_fees, round(kwh_prize_with_energyfactory, 2))
 
    # create new sensor with energy price and compensation substracted
    self.set_value(sensors.daily_prize_accumulated_with_compensation, round(self.cost_daily - self.compensation_api_class.daily_compensation, 2))

    # calculate current kwh price with compensation
    kwh_vat = float(self.kwh_prize) / 100 * 25
    kwh_price_with_compensation = (float(self.kwh_prize) - self.compensation_api_class.kwh_compensation()) + (float(self.kwh_prize) / 100 * 25) + energiledd.energy_factor(self)

    # self.log((self.kwh_prize * 1.25) + energiledd.energy_factor(self))
    # Price based on current kwh usage
    self.set_value(sensors.price_usage_now, round((self.watt_usage / 1000) * ((self.kwh_prize * 1.25) + energiledd.energy_factor(self)), 2))

    # set_kwh_price_with_compensation
    self.set_value(sensors.kwh_price_with_compensation, round(kwh_price_with_compensation, 2))

  """ -----------  Interval ------------- """
  def run_every_hour(self, kwargs):
    # run cleanup functions and shift numbers for new hour / min / day
    self.log("function run_every_hour " + str(datetime.now()))
    

  def run_every_day(self, kwargs):
    # run cleanup functions and shift numbers for new hour / min / day 
    self.log("cleanup function run_every_day " + str(datetime.now()))
    self.set_value(sensors.kwh_consumption_startofday, round(self.total_kwh_usage, 2))

    self.set_value(sensors.kwh_consumption_lastday, round(self.kwh_consumption_today, 2))
    self.set_value(sensors.cost_lastday, round(self.cost_daily, 2))
    self.cost_daily = 0
    self.kwh_consumption_today = 0

  def run_every_month(self, kwargs):
    # run cleanup functions and shift numbers for new hour / min / day
    self.log("cleanup function run_every_month " + str(datetime.now()))
    self.set_value(sensors.kwh_consumption_lastmonth, round(self.kwh_consumption_this_month, 2))
    self.set_value(sensors.kwh_consumption_startofmonth, round(self.self.total_kwh_usage, 2))

    self.set_value(sensors.cost_lastmonth, round(self.cost_monthly, 2))
    self.kwh_consumption_startofmonth = self.total_kwh_usage
    self.kwh_power_min = 0
    self.kwh_power_max = 0
    self.cost_monthly = 0
    self.kwh_consumption_this_month = 0

  def run_every_year(self, kwargs):
    self.log("function run_every_year " + str(datetime.now()))
    self.set_value(sensors.kwh_consumption_startofyear, round(self.total_kwh_usage, 4))

    self.set_value(sensors.cost_lastyear, round(self.cost_yearly, 4))
    self.cost_yearly = 0

    self.set_value(sensors.kwh_consumption_lastyear, round(self.kwh_consumption_this_year, 2))
    self.kwh_consumption_this_year = 0

    import appdaemon.plugins.hass.hassapi as hass

# class EnergyConsumption(hass.Hass):
#   def initialize(self):
#     self.listen_state(self.calculate_values, "sensor.kamstrup_active_power_import")

#   def calculate_values(self, entity, attribute, old, new, kwargs):
#     # Calculate total consumption in kWh
#     kwh_consumption_total = self.get_state("sensor.kamstrup_active_power_import_total")

#     # Calculate consumption in the last day in kWh
#     last_day = datetime.now() - timedelta(days=1)
#     kwh_consumption_lastday = self.get_state("sensor.kamstrup_active_power_import", last_day)

#     # Calculate consumption this month in kWh
#     this_month_start = datetime.now().replace(day=1)
#     kwh_consumption_thismonth = self.get_state("sensor.kamstrup_active_power_import", this_month_start)

#     # Calculate consumption this year in kWh
#     this_year_start = datetime.now().replace(month=1, day=1)
#     kwh_consumption_thisyear = self.get_state("sensor.kamstrup_active_power_import", this_year_start)

#     # Calculate consumption last month in kWh
#     last_month_start = this_month_start - timedelta(days=1)
#     last_month_end = this_month_start - timedelta(seconds=1)
#     kwh_consumption_lastmonth = self.
