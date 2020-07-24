# sp108e-ha
This project is here because I didn't find anywhere on Internet the solution for controlling a SP108e led controller threw Home Assistant.
There is a forum where we discuss this subject :
https://community.home-assistant.io/t/sp108e-digital-wifi-light-strip-controller

For the moment, the python script and associated flow only controls ON/OFF state of the SP108e.
You have then to define the color and brightness of the SP108e once with the official app and then use my script.

# Setup

* One RPi that runs NodeRed (RPi1) with fixed ip address
* One RPi that runs HA (RPi2)

# Installation

On RPi1:
* Put the python script (included here) in a "/home/pi/scripts/" folder.
* Edit the python file and change the CONTROLLER_IP value to have your SP108e ip address.
* In NodeRed, import the flow (included here).

On RPi2:
* Add these lines to configuration.yaml (changing the line 'resource' with the IP address of the RPi1) :
```
switch:
 - platform: rest
   name: LedsTV
   resource: http://ip_address_Rpi1:1880/ledstv
   body_on: '{"active": "true"}'
   body_off: '{"active": "false"}'
   is_on_template: '{{ value_json.is_active }}'
   headers:
     Content-Type: application/json
   verify_ssl: false
``` 
    
* Add a button with this model :
```
entity: switch.ledstv
hold_action:
  action: more-info
icon_height: 40px
show_icon: true
show_name: true
tap_action:
  action: toggle
type: button
```

Should work and tell you the state of the SP108E (on/off)
