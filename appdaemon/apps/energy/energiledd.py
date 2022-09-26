import hassapi as hass
from enum import Enum
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta
import constants

"""
All prices has VAT included
https://www.aenett.no/nettleie/tariffer/

Prisene er inkl. den statlige energifondsavgiften (Enova) på 1,25 øre/kWh, og forbruksavgiften (elavgiften) på 19,26 øre/kWh.
Alle priser er inkl. mva.
"""

# Declare Class
class energiledd(hass.Hass):
    def initialize(self):
        self.energy_factor()

    def energy_factor(self):
        current_time = datetime.now()
        if current_time.hour < 22 and current_time.hour >= 6:
            return constants.ENERGY_FACTOR_DAY 
        return constants.ENERGY_FACTOR_NIGHT