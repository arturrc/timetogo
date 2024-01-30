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

# ANSI escape code for yellow
RED = "\033[1;31m"
YELLOW = "\033[93m"
GREEN = "\033[1;32m"
RESET = "\033[0m"
STATION = "\033[1;30m\033[1;47m"
col_dict = {
	"R" : YELLOW,
	"F" : RED,
	"G" : GREEN
}

# Order wait times based on wait time
wait_times.sort(key = lambda x: x['wait_time'])

# Split wait times based on station
wait_times_split = {}
for wait_time in wait_times:
	if wait_time['stop_id'] in wait_times_split:
		wait_times_split[wait_time['stop_id']] += [wait_time]
	else:
		wait_times_split[wait_time['stop_id']] = [wait_time]

# Go through wait times and print them nicely
current_time = int(time.time())

for stop_id, cur_wait_times in wait_times_split.items():
	print(f"{STATION}{stop_names[stop_id]}{RESET}")

	for x in cur_wait_times:
		wait_time = (x['wait_time'] + x['recorded_time']) - current_time

		if wait_time < min_wait_time or wait_time > max_wait_time:
			continue

		neg_wait_time = False
		if wait_time < 0:
			neg_wait_time = True
			wait_time = -wait_time

		min_num = wait_time//60
		sec_num = 15*((wait_time%60)//15)

		if neg_wait_time:
			min_display = f"-{min_num:1d}"
		else:
			min_display = f"{min_num:2d}"

		sec_display = f"{sec_num:02d}"

		if min_num == 0 and sec_num == 0:
			print(f"{col_dict[x['train_id']]}({x['train_id']}){RESET} : arriving")
		elif sec_num == 0:
			print(f"{col_dict[x['train_id']]}({x['train_id']}){RESET} : {min_display}min")
		else:
			print(f"{col_dict[x['train_id']]}({x['train_id']}){RESET} : {min_display}min{sec_display}")
