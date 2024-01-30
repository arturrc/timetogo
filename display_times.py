import time
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Load the JSON schema
with open('wait_time_schema.json', 'r') as file:
    wait_time_schema = json.load(file)

# Load stop names
with open('stop_names.json', 'r') as file:
    stop_names = json.load(file)

# Load latest wait times
with open('tmp/wait_times.json', 'r') as file:
    wait_times = json.load(file)

# Define display parameters
min_wait_time = -2*60 # minimum wait time to display
max_wait_time = 20*60 # maximum wait time to display

# Go through wait times and print them nicely
current_time = int(time.time())
for x in wait_times:
	cur_time_to_arrival = (x['wait_time'] + x['recorded_time']) - current_time

	if cur_time_to_arrival < min_wait_time or cur_time_to_arrival > max_wait_time:
		continue

	min_display = cur_time_to_arrival//60
	sec_remainder = cur_time_to_arrival%60
	sec_display = 15*(sec_remainder//15)
	if min_display == 0:
		if sec_display == 0:
			print(f"({x['train_id']}) : arriving")
		else:
			print(f"({x['train_id']}) : {sec_display}s")
	elif sec_display == 0:
		print(f"({x['train_id']}) : {min_display}min")
	else:
		print(f"({x['train_id']}) : {min_display}min{sec_display}")
