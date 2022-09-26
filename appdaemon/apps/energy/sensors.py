
###### Global Sensors #######

# Electricity price without VAT
sensor_electricity_price = "sensor.nordpool_kwh_krsand_nok_3_095_0"

# Power in watt usage ( polled every 10 sec from Tibber API )
sensor_watt_consumption = "sensor.power_eigeland_50"

# These sensors should be created in home assistant beforhand.
monthly_net_consumption_eigeland_50 = "sensor.monthly_net_consumption_eigeland_50"
accumulated_consumption_eigeland_50 = "sensor.accumulated_consumption_eigeland_50"
energy_compensation_this_month = "sensor.energy_compensation_this_month"
energy_compensation_daily = "sensor.energy_compensation_daily"
monthly_peak_hour_consumption_eigeland_50 = "sensor.monthly_peak_hour_consumption_eigeland_50"
monthly_power_peak_prize = "sensor.monthly_power_peak_prize"


#
#These input_numbers must be created in home assistant beforhand.
#The main reason we use input_number is to keep values persistent between restart of HA.
#
monthly_avg_kwh_price = "input_number.monthly_avg_kwh_price"
daily_prize_accumulated_with_fees = "input_number.daily_prize_accumulated_with_fees"
monthly_prize_accumulated_with_fees = "input_number.monthly_prize_accumulated_with_fees"
yearly_prize_accumulated_with_fees = "input_number.yearly_prize_accumulated_with_fees"
daily_prize_accumulated_with_compensation = "input_number.daily_prize_accumulated_with_compensation"
electricity_price_eigeland_50_with_compensation = "input_number.electricity_price_eigeland_50_with_compensation"
electricity_price_eigeland_50_with_fees = "input_number.electricity_price_eigeland_50_with_fees"
energiledd = "input_number.energiledd"
