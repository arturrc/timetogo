import time
import requests
from google.transit import gtfs_realtime_pb2
from requests.exceptions import HTTPError

stop_names = {
	'R34N' : 'Prospect Av.',
	'F23N' : '4 Av./9 St.'
}

# Print wait times
def get_times(url, api, stop_ids):
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

	for entity in feed.entity:
		if entity.HasField('trip_update'):
			trip_update = entity.trip_update
			# Check if tje stop time updates include the desired stations
			for x in trip_update.stop_time_update:
				if x.stop_id in stop_ids:
					cur_stop_id = [stop_id for stop_id in stop_ids if x.stop_id == stop_id][0]
					min_to_arrival = (x.arrival.time - current_time)//60
					sec_to_arrival = (x.arrival.time - current_time)%60
					print(f"{trip_update.trip.route_id} train headed {x.stop_id[-1]} arriving in {min_to_arrival}min{sec_to_arrival} at {stop_names[cur_stop_id]}")

# Main ==================================================
# Your API key
api_key = 'n4JkD2b0u45dlXLxs0Yb8spjUkntJbx1siyCzyZ9'

# The API endpoints
url_yellow = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw'
url_orange = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm'
url_green = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g'

# Stop ids
stop_ids = ['R34N', 'F23N']

# Print wait times
get_times(url_yellow, api_key, stop_ids)
get_times(url_orange, api_key, stop_ids)
get_times(url_green, api_key, stop_ids)
