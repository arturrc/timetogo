import time
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

import sys
import os
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5_V2
import logging
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.INFO)                           #Enable log-information for debbuging

# Define paths
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the JSON schema
with open(os.path.join(script_dir, 'wait_time_schema.json'), 'r') as file:
    wait_time_schema = json.load(file)

# Load stop names
with open(os.path.join(script_dir, 'stop_names.json'), 'r') as file:
    stop_names = json.load(file)

# Define display parameters
min_wait_time = 0*60 # minimum wait time to display
max_wait_time = 60*60 # maximum wait time to display

# Prepare font and parameters
font_size = 35
font = ImageFont.truetype(os.path.join(script_dir, "Font.ttc"), font_size)

# Prepare EPD object
epd = epd7in5_V2.EPD()
epd.init()
epd.Clear()
epd.sleep()

# Display parameters
screen_pad = (20, 20, 20, 20) # up, right, bottom, left
font_pad = 10
Himage = Image.new('L', (epd.width, epd.height), 255)           #Clear the frame (255 = white)
draw = ImageDraw.Draw(Himage)
font_width, font_height = draw.textsize("N", font=font)
line_height = font_height + 2*font_pad
circle_square_size = font_height*1.1
circle_square_lateral_pad = 40
n_lines = (epd.height - screen_pad[0] - screen_pad[2])//line_height

# Initialize partial refresh counter
partials = 0

while True:
	# Load latest wait times
	with open(os.path.join(script_dir, 'tmp/wait_times.json'), 'r') as file:
	    wait_times = json.load(file)

	# Order wait times based on wait time
	wait_times.sort(key = lambda x: x['wait_time'])

	# Reduce to only as many lines fit on the screen
	n_stations = len(list(dict.fromkeys([x['stop_id'] for x in wait_times])))
	wait_times = wait_times[0:min(len(wait_times), n_lines - n_stations + 1)]

	# Split wait times based on station
	wait_times_split = {}
	for wait_time in wait_times:
		if wait_time['stop_id'] in wait_times_split:
			wait_times_split[wait_time['stop_id']] += [wait_time]
		else:
			wait_times_split[wait_time['stop_id']] = [wait_time]

	# Initialize display buffer
	Himage = Image.new('L', (epd.width, epd.height), 255)           #Clear the frame (255 = white)
	draw = ImageDraw.Draw(Himage)                                   #Create new image buffer
	y0 = screen_pad[0]

	# Go through wait times and print them nicely
	current_time = int(time.time())
	formatted_time = time.strftime('%H:%M', time.localtime())

	# Print current time, right-justified
	text_width, text_height = draw.textsize(formatted_time, font=font)
	draw.text((epd.width - screen_pad[3] - text_width, epd.height - y0 - text_height), formatted_time, font = font, fill = 0)

	# Print wait times
	for stop_id, cur_wait_times in wait_times_split.items():
		draw.rectangle((0, y0, epd.width, y0 + line_height), fill = 0)
		draw.text((screen_pad[3] + font_pad, y0 + font_pad), f"{stop_names[stop_id]}", font = font, fill = 255)
		y0 += line_height

		for x in cur_wait_times:
			wait_time = (x['wait_time'] + x['recorded_time']) - current_time

			if wait_time < min_wait_time or wait_time > max_wait_time:
				continue

			neg_wait_time = False
			if wait_time < 0:
				neg_wait_time = True
				wait_time = -wait_time

			min_num = wait_time//60
			sec_num = 30*((wait_time%60)//30)

			if neg_wait_time:
				min_display = f"-{min_num:1d}"
			else:
				min_display = f"{min_num:2d}"

			sec_display = f"{sec_num:02d}"

			# Draw train line
			draw.chord((screen_pad[3] + circle_square_lateral_pad, y0 + line_height/2 - circle_square_size/2,
				screen_pad[3] + circle_square_lateral_pad + circle_square_lateral_pad, y0 + line_height/2 + circle_square_size/2),
				0, 360, fill = 50)
			draw.text((screen_pad[3] + circle_square_lateral_pad + circle_square_size/4, y0 + line_height/2 - font_height/2), f"{x['train_id']}", font = font, fill = 255)

			# Write waiting time
			if min_num == 0 and sec_num == 0:
				# draw.text((screen_pad[3] + font_pad, y0 + font_pad), f"({x['train_id']}) : arriving", font = font, fill = 0)
				draw.text((screen_pad[3] + 2*circle_square_lateral_pad + circle_square_size, y0 + font_pad), f"arriving", font = font, fill = 0)
				y0 += line_height
			elif sec_num == 0:
				# draw.text((screen_pad[3] + font_pad, y0 + font_pad), f"({x['train_id']}) : {min_display}min", font = font, fill = 0)
				draw.text((screen_pad[3] + 2*circle_square_lateral_pad + circle_square_size, y0 + font_pad), f"{min_display}min", font = font, fill = 0)
				y0 += line_height
			else:
				# draw.text((screen_pad[3] + font_pad, y0 + font_pad), f"({x['train_id']}) : {min_display}min{sec_display}", font = font, fill = 0)
				draw.text((screen_pad[3] + 2*circle_square_lateral_pad + circle_square_size, y0 + font_pad), f"{min_display}min{sec_display}", font = font, fill = 0)
				y0 += line_height

	# Display it on the screen
	#epd.init()
	#epd.Clear()
	#Himage = Himage.transpose(Image.Transpose(2))
	if partials <= 10:
		partials += 1
		epd.init_part()
		epd.display_Partial(epd.getbuffer(Himage), 0, 0, epd.width, epd.height)
	else:
		partials = 0
		epd.init()
		epd.Clear()
		print("CLEARED")
		epd.display(epd.getbuffer(Himage))                              #Display the buffer on the screen
	epd.sleep()
	time.sleep(30)
