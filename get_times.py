import time
import os
import requests
import sys
from google.transit import gtfs_realtime_pb2
from requests.exceptions import HTTPError
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Define paths
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the JSON schema
with open(os.path.join(script_dir, 'wait_time_schema.json'), 'r') as file:
    wait_time_schema = json.load(file)

# Load stop names
with open(os.path.join(script_dir, 'stop_names.json'), 'r') as file:
    stop_names = json.load(file)

# Print wait times
def get_times(url, api, stop_ids, verbose=False):
	# Make GET request
	headers = {
		'x-api-key': api_key
	}

	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()

	except HTTPError as http_err:
		print(f"HTTP error occurred: {http_err}")
		raise  # Optionally re-raise the exception to stop the program

	# Process the response here
	feed = gtfs_realtime_pb2.FeedMessage()
	feed.ParseFromString(response.content)

	current_time = int(time.time())

	wait_times = []

	for entity in feed.entity:
		if entity.HasField('trip_update'):
			trip_update = entity.trip_update
			# Check if tje stop time updates include the desired stations
			for x in trip_update.stop_time_update:
				if x.stop_id in stop_ids:
					cur_stop_id = [stop_id for stop_id in stop_ids if x.stop_id == stop_id][0]
					time_to_arrival = x.arrival.time - current_time

					if verbose:
						print(f"{trip_update.trip.route_id} train headed {x.stop_id[-1]} arriving in {time_to_arrival//60}min at {stop_names[cur_stop_id]}")

					cur_obj = [{
						'train_id' : trip_update.trip.route_id,
						'stop_id' : cur_stop_id,
						'wait_time' : time_to_arrival,
						'recorded_time' : current_time
					}]

					wait_times += cur_obj

	return wait_times

# Main ==================================================
# Get command line argument
if len(sys.argv) > 1:
	output_path = sys.argv[1]
else:
	output_path = os.path.join(script_dir, 'tmp/wait_times.json')

# Your API key
api_key = 'n4JkD2b0u45dlXLxs0Yb8spjUkntJbx1siyCzyZ9'

# The API endpoints
url_yellow = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw'
url_orange = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm'
url_green = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g'

# Stop ids
stop_ids = ['R34N', 'F23N']

# Print wait times
wait_times = get_times(url_yellow, api_key, stop_ids)
wait_times += get_times(url_orange, api_key, stop_ids)
wait_times += get_times(url_green, api_key, stop_ids)

# Validate JSON data
try:
    validate(instance=wait_times, schema=wait_time_schema)
except ValidationError as e:
    print("JSON data is invalid:", e)
    raise

# Output JSON wait times
with open(output_path, 'w') as file:
    json.dump(wait_times, file, indent = 4)
