###### Global Sensors #######

# Electricity price without VAT
sensor_electricity_price = "sensor.nordpool_kwh_krsand_nok_3_095_0"

# Power in watt usage ( polled every 10 sec mqtt) 
sensor_watt_consumption = "sensor.kamstrup_active_power_import"

# Total ams 
kamstrup_power_import_total = "sensor.kamstrup_active_power_import_total"

# forbruk
kwh_consumption_total = "input_number.kwh_consumption_total"
kwh_consumption_today = "input_number.kwh_consumption_today"
kwh_consumption_lastday = "input_number.kwh_consumption_lastday"
kwh_consumption_thismonth = "input_number.kwh_consumption_thismonth"
kwh_consumption_thisyear = "input_number.kwh_consumption_thisyear"
kwh_consumption_lastmonth = "input_number.kwh_consumption_lastmonth"
kwh_consumption_startofday = "input_number.kwh_consumption_startofday"
kwh_consumption_startofmonth = "input_number.kwh_consumption_startofmonth"
kwh_consumption_startofyear = "input_number.kwh_consumption_startofyear"
kwh_active_usage = "input_number.kwh_active_usage"
kwh_max = "input_number.kwh_max"
kwh_min = "input_number.kwh_min"

energy_compensation_this_month = "sensor.energy_compensation_this_month"
energy_compensation_lastmonth = "sensor.energy_compensation_lastmonth"
energy_compensation_daily = "sensor.energy_compensation_daily"

monthly_kwh_peak_hour = "input_number.monthly_kwh_peak_hour"
monthly_power_peak_prize = "input_number.monthly_power_peak_prize"


#
#These input_numbers must be created in home assistant beforhand.
#The main reason we use input_number is to keep values persistent between restart of HA.
#
daily_prize_accumulated_with_fees = "input_number.daily_prize_accumulated_with_fees"
daily_prize_accumulated_with_compensation = "input_number.daily_prize_accumulated_with_compensation"
cost_lastday = "input_number.cost_lastday"
cost_lastmonth = "input_number.cost_last_month"
monthly_prize_accumulated_with_fees = "input_number.monthly_prize_accumulated_with_fees"
monthly_avg_kwh_price = "input_number.monthly_avg_kwh_price"
yearly_prize_accumulated_with_fees = "input_number.yearly_prize_accumulated_with_fees"
kwh_price_with_compensation = "input_number.kwh_price_with_compensation"
kwh_price_with_fees = "input_number.kwh_price_with_fees"
kwh_price = "input_number.kwh_price"
energiledd = "input_number.energiledd"
price_usage_now = "input_number.price_usage_now"
