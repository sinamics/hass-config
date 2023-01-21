import sensors
import os
from datetime import datetime, date
import appdaemon.plugins.hass.hassapi as hass
import constants
from ast import literal_eval
import json
import pickle as pickle

class TopThreeHours(hass.Hass):
    def initialize(self):
        # Read saved values from file if app is restarted
        self.top_hours = []
        self.reset_date = date.today()

        top_hours_str = self.load_from_file(constants.TOP_THREE_KWH_HOURS_FILE)
        if top_hours_str is not None:
            self.top_hours = top_hours_str

        # Listen for updates to the kWh consumption value
        self.listen_state(self.update_top_hours, sensors.kwh_active_usage, immediate=True)

    def update_top_hours(self, entity, attribute, old, new, kwargs):
        # Check if it's time to reset the top hours list
        current_time = datetime.now()
        if current_time.day == 1 and current_time.hour == 0 and current_time.minute == 0:
            self.reset_top_hours()

        # Update the top hours list with the new consumption value
        consumption = float(new)
        self.top_hours.append((consumption, current_time))
        self.top_hours = sorted(self.top_hours, key=lambda x: x[0], reverse=True)[:3]
        # self.log(self.top_hours)
        # Calculate and output the average of the top three hours
        average = sum([x[0] for x in self.top_hours]) / len(self.top_hours)

        self.set_value(sensors.monthly_kwh_peak_hour, round(average, 2)) 
        # self.log("TopThreeHours: {}, Day: {}, Date: {}".format(average, self.top_hours[0][1].strftime("%A"), self.top_hours[0][1].strftime("%m/%d/%Y")))

    def reset_top_hours(self):
        # Reset the top hours list and update the reset date
        self.top_hours = []
        self.reset_date = datetime.now().date()

        # Save the new values to file
        self.save_to_file(constants.TOP_THREE_KWH_HOURS_FILE, self.top_hours)

    def load_from_file(self, name):
        # Load a value from file (if it exists)
        try:
            if os.path.getsize(name) > 0:
                with open(name, "rb") as f:
                    return pickle.load(f)
            else:
                return None
        except FileNotFoundError:
            self.log(f"file {name} not found")
            return None

    def save_to_file(self, name, value):
        if len(value) == 0:
            return self.log(f"value is empty:: {value}")
