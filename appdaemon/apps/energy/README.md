# ha-energy
This is an AppDaemon automation of my AMS energy monitoring in Home Assistant. 

# why
It provides additional information such as:
- Electricity price with and without VAT & Energy factor (energiledd)
- Real time kWh price with compensation from the Norwegian goverment, based on the current monthly average price.


# Installation

1. This requires AppDeamon installed and configured (follow the documentation on their web site).
2. Make sure that `datetime` are incuded in the `python_packages` option
3. Copy the content of the energy directory from this repository to your home assistant `/config/appdaemon` folder
4. Add configuration to your Home Assistant's `/config/appdaemon/apps/apps.yaml`


In apps.yaml add these modules:

```yaml
global_modules:
  - sensors
  - constants

kapasitetsledd:
  module: kapasitetsledd
  class: kapasitetsledd
  global_dependencies:
    - sensors
    - constants

energiledd:
  module: energiledd
  class: energiledd
  global_dependencies:
    - constants

compensation:
  module: compensation
  class: Compensation
  global_dependencies:
    - sensors
    - constants

notification:
  module: notification
  class: Notification

core:
  module: core
  class: Core
  global_dependencies:
    - sensors
    - constants
  dependencies:
    - compensation
    - store
    - energiledd
```
