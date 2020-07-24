### Ported from https://github.com/Lehkeda/SP108E_controller/blob/v1/controller.php
import socket
import binascii
import sys

CONTROLLER_IP = "192.168.87.110"
CONTROLLER_PORT = 8189

mono_animations = {
	"meteor" : "cd",
	"breathing" : "ce",
	"wave" : "d1",
	"catch up" : "d4",
	"static" : "d3",
	"stack" : "cf",
	"flash" : "d2",
	"flow" : "d0"
}
def get_animation(x):
	try:
		animation = [k for k, v in mono_animations.items() if v == x][0]
		return animation
	except IndexError:
		return x

chip_types = {
	"SM16703": "00",
	"TM1804": "01",
	"UCS1903": "02",
	"WS2811": "03",
	"WS2801": "04",
	"SK6812": "05",
	"LPD6803": "06",
	"LPD8806": "07",
	"APA102": "08",
	"APA105": "09",
	"DMX512": "0a",
	"TM1914": "0b",
	"TM1913": "0c",
	"P9813": "0d",
	"INK1003": "0e",
	"P943S": "0f",
	"P9411": "10",
	"P9413": "11",
	"TX1812": "12",
	"TX1813": "13",
	"GS8206": "14",
	"GS8208": "15",
	"SK9822": "16",
	"TM1814": "17",
	"SK6812_RGBW": "18",
	"P9414": "19",
	"P9412": "1a"
}
get_chip_type = lambda x: [k for k, v in chip_types.items() if v == x][0]



color_orders = {
	"RGB": "00",
	"RBG": "01",
	"GRB": "02",
	"GBR": "03",
	"BRG": "04",
	"BGR": "05"
}
get_color_order = lambda x: [k for k, v in color_orders.items() if v == x][0]



def dec_to_even_hex(decimal: int, output_bytes: int=None):
	hex_length = len(hex(decimal)) - 2
	out_length = hex_length + (hex_length % 2)
	if output_bytes:
		out_length = output_bytes * 2
	return f"{decimal:0{out_length}x}"
		
		

def transmit_data(
	data: str, # the command and it's value(if it has a value)
	expect_response: bool, # set to true if you expect a response
	response_length: int # how long the response is
):
	s = socket.create_connection((CONTROLLER_IP, CONTROLLER_PORT))
	cleaned_data = data.replace(" ", "")
	s.send(binascii.unhexlify(cleaned_data))
	if expect_response:
		return s.recv(response_length)

def is_device_ready():
	return transmit_data("38 000000 2f 83", True, 1)

def send_data(data: str, expect_response: bool=False, response_length: int=0):
	response = transmit_data(data, expect_response, response_length)
	return response

def change_color(color: str):
	# color in hex format
	color = color.replace("#", "")
	
	send_data(f"38 {color} 22 83")

def change_speed(speed: int):
	if not 0 <= speed <= 255:
		raise ValueError("speed must be between 0 and 255")
	send_data(f"38 {speed} ")

def change_brightness(brightness: int):
	if not 0 <= brightness <= 255:
		raise ValueError("brightness must be between 0 and 255")
	send_data(f"38 {dec_to_even_hex(brightness)} 0000 2a 83")

def get_name():
	result = send_data("38 000000 77 83", True, 18);
	return result


def get_device_raw_settings():
	result = send_data("38 000000 10 83", True, 17);
	return binascii.hexlify(result).decode("ascii")


def is_active():
	raw_settings = get_device_raw_settings()
	turned_on = int(raw_settings[2:4], 16)
	ret = 1 if turned_on == 1 else 0
    
	return ret
	
def get_device_settings():
	
	raw_settings = get_device_raw_settings()
	
	current_animation = get_animation(raw_settings[4:6])
	chip_type = get_chip_type(raw_settings[26:28])
	color_order = get_color_order(raw_settings[10:12])
	turned_on = int(raw_settings[2:4], 16)
	current_color = raw_settings[20:26].upper()
	
	settings = {
		"turned_on": turned_on,
		"current_animation": current_animation,
		"animation_speed": int(raw_settings[6:8], 16),
		"current_brightness": int(raw_settings[8:10], 16),
		"color_order": color_order,
		"leds_per_segment": int(raw_settings[12:16], 16),
		"segments": int(raw_settings[16:20], 16),
		"current_color": current_color,
		"chip_type": chip_type,
		"recorded_patterns": int(raw_settings[28:30], 16),
		"white_channel_brightness": int(raw_settings[30:32], 16)
	}
	
	return settings
	

def change_mono_color_animation(index):
	#	 Mono animations
	#		0xcd => Meteor
	#		0xce => Breathing
	#		0xd1 => Wave
	#		0xd4 => Catch up
	#		0xd3 => Static
	#		0xcf => Stack
	#		0xd2 => Flash
	#		0xd0 => Flow
	

	send_data(f"38 {index} 0000 2c 83")
	
	
def change_mixed_colors_animation(index):
	# 0x00 (first animation 1) -> 0xb3 (last animation 180)
	send_data(f"38 {dec_to_even_hex(index - 1)} 0000 2c 83") # specific animation


def enable_multicolor_animation_auto_mode():
	send_data("38 000000 06 83") #auto mode


def toggle_off_on():
	send_data("38 000000 aa 83")

def change_white_channel_brightness(brightness=255):
	if not 0 <= brightness <= 255:
		raise ValueError("brightness must be between 0 and 255")
	send_data(f"38	{dec_to_even_hex(brightness)}0000 08 83")

def set_number_of_segments(segments: int=1):
	send_data(f"38 {dec_to_even_hex(segments, 2)} 00 2e 83")

def set_number_of_leds_per_segment(leds: int=50):
	send_data(f"38 {dec_to_even_hex(leds, 2)} 00 2d 83")

args = sys.argv

if args[1] == "toggle":
	toggle_off_on()
	
if args[1] == "is_active":
	print(is_active())