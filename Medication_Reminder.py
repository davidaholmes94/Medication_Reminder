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
from datetime import datetime, timedelta
import time

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


#INPUT TIMES TO TAKE MEDICINE HERE
current_day = datetime.now()
wake_up = current_day.replace(hour=11, minute=35,second=0,microsecond=0)
breakfast = current_day.replace(hour=8, minute=0,second=0,microsecond=0)
morning = current_day.replace(hour=9, minute=30,second=0,microsecond=0)
as_needed = current_day.replace(hour=23, minute=59,second=59,microsecond=0)

def med_start_time(medicine):
    if (medicine == 'Tylenol') | (medicine == 'Tramadol'):
        #when you wake up
        med_start_time = wake_up
    elif (medicine == 'Aspirin') | (medicine == 'Gabapentin'):
        #when you eat breakfast
        med_start_time = breakfast
    elif (medicine == 'Ceftin') | (medicine == 'Stool Softener'):
        #general morning
        med_start_time = morning
    else:
        med_start_time = as_needed
    return med_start_time
    
med_schedule['trigger_1'] = med_schedule.apply(lambda row: med_start_time(row['Medication']),axis=1)
# %% Monitor the Time & Update Trigger Alerts
#take pills at 9:30 am and 3:30 pm
#take Aspirin and Ceftin with food
while True:
    try:
        #get current time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        #Iterate through every row of the medication schedule dataframe
        for i in med_schedule.index:
            #if the current time is within 1 minute of the trigger time
            if (now > med_schedule['trigger_1'][i] - timedelta(seconds=59)) & (now < med_schedule['trigger_1'][i] + timedelta(seconds=59)):
              
                #get the medication information
                med_to_take = med_schedule.Medication[i]
                
                #send the text message
                #form the text message
                txt_msg = "At " + current_time + " it is time to take " + med_to_take
                
                message = client.messages.create(
                    body = txt_msg,
                    from_ = credentials['from_phone_number'],
                    to = credentials['to_phone_number'])
                time.sleep(1)
                #log info
                print('The following text message was sent at: ' + current_time)
                print(txt_msg)
                
                #reset trigger based on instructions
                if med_schedule['schedule'][i] == '2x a day':
                    new_trigger = now + timedelta(hours=8)
                    new_trigger = new_trigger.replace(second=0,microsecond=0)
                elif med_schedule['schedule'][i] == '6 Hours':
                    new_trigger = now + timedelta(hours=6)
                    new_trigger = new_trigger.replace(second=0,microsecond=0)
                elif med_schedule['schedule'][i] == '8 Hours':
                    new_trigger = now + timedelta(hours=8)
                    new_trigger = new_trigger.replace(second=0,microsecond=0)
                else:
                    new_trigger = med_schedule['trigger_1'][i]
                
                med_schedule.at[i,'trigger_1'] = new_trigger
                
                #log info
                new_trigger_time = new_trigger.strftime("%H:%M:%S")
                print('You will take this medicine again at: ' + new_trigger_time)
                
   
    except KeyboardInterrupt:
        print('Program has stopped running')
        break
    
        


