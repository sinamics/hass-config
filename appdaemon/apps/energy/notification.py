import hassapi as hass
from energiledd import energiledd
import sensors

# Declare Class 
class Notification(hass.Hass):
    def initialize(self):    
        self.listen_state(self.notify_high_prize, sensors.kwh_price_with_fees, immediate=True)
        self.listen_state(self.notify_price_is_negative, sensors.kwh_price_with_compensation, immediate=True)

    """ -----------  Notification ------------- """
    def notify_high_prize(self, entity, attribute, old, new, kwargs):  
        if not new:
            return
        if float(new) > 7.0 and new > old:
            self.notify("Prisen er for øyeblikket {0}kWh inkludert moms og energiledd på {1} øre".format(new, energiledd.energy_factor(self)), title = "Høy Strømpris")
            self.log("high prize " + str(new))

    def notify_price_is_negative(self, entity, attribute, old, new, kwargs):
        if not new:
            return
        if float(new) < 0:
            self.notify("BILLIG strøm. Nå tjener vi penger {0}kWh".format(new), title = "Negativ Strømpris")
            self.log("Negativ Strompris " + str(new))