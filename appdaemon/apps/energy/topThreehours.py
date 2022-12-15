
import sensors
from datetime import datetime, date
import appdaemon.plugins.hass.hassapi as hass
import constants
import datetime

class TopThreeHours(hass.Hass):
    def initialize(self):
        # Read saved values from file if app is restarted
        self.top_hours = self.load_from_file(constants.TOP_THREE_KWH_HOURS_FILE)
        self.reset_date = self.load_from_file(constants.TOP_THREE_KWH_HOURS_RESET_FILE)

        # If no saved values exist, initialize top_hours and reset_date
        if self.top_hours is None:
            self.top_hours = []
        if self.reset_date is None:
            self.reset_date = datetime.date.today()

        # Listen for updates to the kWh consumption value
        self.listen_state(self.update_top_hours, sensors.kwh_active_usage, immediate=True)

    def update_top_hours(self, entity, attribute, old, new, kwargs):
        # Check if it's time to reset the top hours list
        today = datetime.date.today()
        if today > self.reset_date:
            self.reset_top_hours()

        # Update the top hours list with the new consumption value
        consumption = float(new)
        self.top_hours.append((consumption, datetime.datetime.now()))
        self.top_hours = sorted(self.top_hours, key=lambda x: x[0], reverse=True)[:3]

        # Calculate and output the average of the top three hours
        average = sum([x[0] for x in self.top_hours]) / len(self.top_hours)
        self.set_value(sensors.monthly_kwh_peak_hour, round(average, 2)) 
        self.log("TopThreeHours: {}, Day: {}, Date: {}".format(average, self.top_hours[0][1].strftime("%A"), self.top_hours[0][1].strftime("%m/%d/%Y")))

    def reset_top_hours(self):
        # Reset the top hours list and update the reset date
        self.top_hours = []
        self.reset_date = datetime.date.replace(self.reset_date, month=self.reset_date.month+1)

        # Save the new values to file
        self.save_to_file(constants.TOP_THREE_KWH_HOURS_FILE, self.top_hours)
        self.save_to_file(constants.TOP_THREE_KWH_HOURS_RESET_FILE, self.reset_date)

    def load_from_file(self, name):
        # Load a value from file (if it exists)
        try:
            with open(name, "r") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def save_to_file(self, name, value):
        # Save a value to file
        with open(name, "w") as f:
            f.write(str(value))
