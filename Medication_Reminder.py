# -*- coding: utf-8 -*-
"""
Medication Reminder Script
Created on Tue Dec 17 13:35:53 2019

@author: David
"""

from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import json
import pandas as pd
from datetime import time
from datetime import timedelta

file_dir = 'C:/Users/David/Documents/Python/Github/Medication_Reminder/'
#%% Import Credentials 
with open(file_dir + 'credentials.json') as json_data:
    credentials = json.load(json_data)

# %% Start the Service
account_sid = credentials['account_sid']
auth_token = credentials['auth_token']
client = Client(account_sid,auth_token)
phone_number = credentials['to_phone_number']

# %% Import Schedule of Medication
med_schedule = pd.read_csv(file_dir + 'MedicationInstructions.csv')

#parse instructions and break into amount, time
#regex to find the amount 
#search for tablet, capsule, pill, pills

#search for 2 (two) times daily, X hours, twice a day
#for now, hardcode for simplicity + GSD
#med_schedule['schedule'] = med_schedule['Instructions'].str.extract(r'(\d\s\w)',expand=True)

med_schedule['amount'] = [1,1,1,1,2,2,1]
med_schedule['schedule'] = ['2x a day','2x a day','As Needed','6 Hours', '8 Hours','2x a day','2x a day']

#Use the schedule to create trigger times
#times to take medicine
morning = time(9,0,00)
evening = time(6,30,00)
med_schedule['trigger_1'] = morning


# %% Monitor the Time & Update Trigger Alerts
#take pills at 9:30 am and 3:30 pm
#take Aspirin and Ceftin with food

while True:
    try:
        #get current time
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        for index,row in med_schedule.iterrows():
            if current_time == row['trigger_1']:
                
                #time to take pills
                med_to_take = row['Medication']
                txt_msg = "At " + row['trigger_1'] + " it is time to take " + med_to_take
                
                #send the text message
                message = client.messages.create(
                    body = txt_msg,
                    from_ = credentials['from_phone_number'],
                    to = credentials['to_phone_number'])
                
                #reset trigger based on instructions
                if row['schedule'] == '2x a day':
                    new_trigger = now + datetime.timedelta(hours=8)
                elif row['schedule'] == '6 Hours':
                    new_trigger = now + datetime.timedelta(hours=6)
                elif row['schedule'] == '8 Hours':
                    new_trigger = now + datetime.timedelta(hours=8)
                
                #Add new trigger back to dataframe
                new_trigger_time = new_trigger.strftime("%H:%M:%S")
                row['trigger_1'] = new_trigger_time
    
    
    except KeyboardInterrupt:
        print('Program has stopped running')
        


