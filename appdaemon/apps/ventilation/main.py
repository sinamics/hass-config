import hassapi as hass
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta

# Declare Class
class Main(hass.Hass):
    def initialize(self):
        self.target_temperature = 0
        self.is_auto = False

        self.low_temp = 15
        self.high_temp = 24

        ## Run task every hour
        self.run_hourly(self.run_every_hour, time(0, 0, 0))
        ## Listen for auto state
        self.listen_state(self.temp_listner, "input_boolean.ventilation_auto", immediate=True)
        self.listen_state(self.home_listner,"device_tracker.adrian_samsung_s20")
        self.listen_state(self.outside_temperature,"sensor.1f_house_outside_laundryroom_termometer_temperature", immediate=True)

    def temp_listner(self, entity, attribute, old, new, kwargs):
        if new == "off":
            self.is_auto = False
            return

        self.is_auto = True
        self.set_temperature()

    def outside_temperature(self, entity, attribute, old, new, kwargs):
        try:
            new_float = float(new)
        except ValueError:
            self.log(f"Unable to convert {new} to float. Ignoring update.")
            return

        if new_float >= 15:
            self.high_temp = 21
        else:
            self.high_temp = 24

        self.set_temperature()

    def home_listner(self, entity, attribute, old, new, kwargs):
        self.set_temperature()

    def set_temperature(self):
        if self.is_auto == False:
            return

        current_time = datetime.now()
        if current_time.weekday() < 5 and current_time.hour >= 6 and current_time.hour < 8:
            # daytime   
            self.log("wakeup temperature")
            self.target_temperature = self.high_temp

        # mid day settings
        elif current_time.hour >= 6 and current_time.hour < 15:
            # daytime   
            self.log("daytime temperature")
            if self.anyone_home():
                self.target_temperature = self.high_temp
            else:
                self.target_temperature = self.low_temp

        elif current_time.hour >= 15 and current_time.hour < 22:
            # evening   
            self.log("evening temperature")
            self.target_temperature = self.high_temp

        else:
            self.target_temperature = self.low_temp

        # fan_modes: auto, 1, 2, 3, 4, 5
        # swing_modes: auto, 1_up, 2, 3, 4, 5_down, swing
        # hvac_modes: off, heat, dry, cool, fan_only, heat_cool

        # call service: 
        self.call_service("climate/set_temperature", entity_id  = "climate.hvac_eigeland", temperature = self.target_temperature)
        self.call_service("climate/set_hvac_mode", entity_id  = "climate.hvac_eigeland", hvac_mode = "heat_cool")
        self.call_service("climate/set_fan_mode", entity_id  = "climate.hvac_eigeland", fan_mode = "auto")
        self.call_service("climate/set_swing_mode", entity_id  = "climate.hvac_eigeland", swing_mode = "auto")

    """ -----------  Interval ------------- """
    def run_every_hour(self, kwargs):
        self.log("ventilation function run_every_hour " + str(datetime.now()))
        self.set_temperature()
    