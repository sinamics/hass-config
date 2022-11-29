import hassapi as hass
import os
from enum import Enum
from datetime import datetime, time, timedelta, date
from dateutil.relativedelta import relativedelta
import sensors
import constants
import mysql.connector as mariadb
from dotenv import load_dotenv

load_dotenv()

# Declare Class
class Hourly_peak(hass.Hass):
  def initialize(self):
    self.test = 0 

  def query_data():
    database = mariadb.connect(user=os.getenv('MARIADB_USER'), password=os.getenv('MARIADB_PASSWORD'), host=os.getenv('MARIADB_HOST'), database=os.getenv('MARIADB_DB'))
    self.cursor = database.cursor(dictionary=True)
    try:
      query =   "SELECT mean FROM `statistics` WHERE `metadata_id` = 122 AND `created` BETWEEN '2022-10-01T00:00:00.00' AND '2022-10-31T23:59:59.999' ORDER BY `mean` DESC limit 3;"
      self.log("Performing query {} with cursor {}".format(query, self.cursor))
      response = self.cursor.execute(query, params=None, multi=True)
      self.log("Query response {} with cursor {}".format(response, self.cursor))
    except:
      self.log("Error with query: {}".format(query))
      raise
    
    self.cursor.execute(query)
    data = self.cursor.fetchall()
    for d in data:
      self.log(d["mean"])


    self.log("SQL Results: {}".format(self.cursor))
    database.close()
