#!/usr/bin/env python
import serial, time, sys, signal, json, argparse
import paho.mqtt.client as mqtt
__author__ = 'Jon Stratton'
# mosquitto_pub -h localhost -t 'vacuum/command' -m 'clean_spot'

# Get config file
parser = argparse.ArgumentParser()
parser.add_argument('-c', action='store', dest='config_file', help='json config file')
args = parser.parse_args()
with open( args.config_file ) as json_data_file:
   config = json.load(json_data_file)
broker_address  = config.get( 'broker_address', '' )
serial_dev      = config.get( 'serial_dev', '' )
roomba_commands = config.get( 'roomba_commands', [] )

# Just write some digits to the serial port
def roomba_do( command_list ):
   success = False
   try:
      ser = serial.Serial( serial_dev, 115200 )
      for num in command_list:
         ser.write(chr(num))
         time.sleep(.25)
      ser.close()
      success = True
   except:
      pass
   return success

def on_message(client, userdata, message):
   command = str(message.payload.decode("utf-8"))
   if roomba_commands.get( command, [] ):
      print( 'Got: %s' % command )
      if roomba_do( roomba_commands.get( command, [] ) ):
         print( 'Command: %s' % ( command ) )

# cleanup on sigint
def signal_handler( sig, frame ):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
   client = mqtt.Client('RoombaSerialMQTT')
   client.on_message=on_message
   client.connect(broker_address)
   client.subscribe('vacuum/command')
   client.loop_forever()

main()
