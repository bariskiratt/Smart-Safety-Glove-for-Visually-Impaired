import RPi.GPIO as GPIO
import time
import os
import glob

# Wire for DS18B20
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Pins (BOARD numbering)
TRIG = 11 
ECHO = 12
BUZZER = 13
VIBRATOR = 15

#Get all the filenames begin with 28 in the path base_dir
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# Vibrator logic
ACTIVE_LOW_VIBRATOR = False
V_ON  = GPIO.LOW  if ACTIVE_LOW_VIBRATOR else GPIO.HIGH
V_OFF = GPIO.HIGH if ACTIVE_LOW_VIBRATOR else GPIO.LOW

def setup():
    #Setup the GPIO pins for Buzzer,Vibrator, and Ultrasonic Sensor
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    # Ultrasonic
    GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ECHO, GPIO.IN)

    # Outputs
    GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(VIBRATOR, GPIO.OUT, initial=V_OFF)

def distance():
    # Measure the distance with ultrasonic sensor

    GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        pass
    time1 = time.time()
    
    while GPIO.input(ECHO) == 1:
        pass
    time2 = time.time()

    duration = time2 - time1
    return (duration * 340 / 2) * 100  # Convert to centimeters
  
def buzzer_on():
    # Set buzzer on
    GPIO.output(BUZZER, GPIO.LOW)

def buzzer_off():
    # Set buzzer of
    GPIO.output(BUZZER, GPIO.HIGH)

def vibrator_on():
    # Set vibrator on
    GPIO.output(VIBRATOR, V_ON)

def vibrator_off():
    # Set vibrator off
    GPIO.output(VIBRATOR, V_OFF)

def beep(duration):
    # Set the beep for a specified duration
    buzzer_on()
    time.sleep(duration)
    buzzer_off()
    time.sleep(duration)

#For temperature sensor
def read_rom():
	name_file=device_folder+'/name'
	f = open(name_file,'r')
	return f.readline()
 
def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines
 
def read_temp():
    lines = read_temp_raw()
    #Analyze if the last 3 charracters are "YES"
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    #Fix the index of t= in the string
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    
def loop():
    # Main loop that checks the distance,temperature and controls the buzzer and vibrator 
    while True:
        dis = distance()
        temp_celsius , temp_fahrenheit = read_temp()
        print(dis, 'cm')  # Print distance measurement

        if dis < 5:  # If the object is within 5 cm, vibrate continuously
            vibrator_on()
        else:
            vibrator_off()  # Turn off vibrator if object is far
        
        if temp_fahrenheit > 100:  # If more than 100 fahrenheit, beep continuously
            buzzer_on()
        elif temp_fahrenheit < 100 and temp_fahrenheit > 80 :  # If within 80 and 100 fahrenheit, beep with decreasing interval
            beep_interval = (temp_fahrenheit - 60) / 50.0  # Adjust beep interval
            beep(beep_interval)
        else:
            buzzer_off()  # Turn off buzzer if object is far"""

        time.sleep(0.3)

def destroy():
    # Cleanup function to reset GPIO settings
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
