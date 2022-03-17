import sys
import requests
import ast
import datetime
import time
import teslapy

def tesla_plugged_in():
    global cardata
    global vehicles
    success = 0
    while (success == 0):
        with teslapy.Tesla('<**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH EMAIL ADDRESS USED TO LOG INTO YOUR TESLA ACCOUNT**>') as tesla:
            try:
                vehicles = tesla.vehicle_list()
            except:
                print("Get vehicle_list failed.")
                time.sleep(10)
                continue
            try:
                vehicles[0].sync_wake_up()
            except:
                print("Vehicle wake_up failed.")
                time.sleep(5)
                continue
            try:
                cardata = vehicles[0].get_vehicle_data()
                success = 1
            except:
                print("Get Vehicle Data Failed.")
                time.sleep(10)
                continue
    lat_raw = cardata['drive_state']['latitude']
    longitude_raw = cardata['drive_state']['longitude']
    plug_status = cardata['charge_state']['charge_port_door_open']
    charge_limit = cardata['charge_state']['charge_limit_soc']
    
    if (lat_home - .0002) <= lat_raw <= (lat_home + .0002) and (long_home - .0002) <= longitude_raw <= (long_home + .0002):
        at_home = "At Home"
    else:
        at_home = "Not At Home"
    if plug_status:
        tpi = "Plugged In"
    else:
        tpi = "Not Plugged In"
    return at_home, tpi, charge_limit

def get_meter_reading():
    x = open('commands.xml', 'r').read()  # Commands to be processed by the Eagle-200
    url = "http://<**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH LOCAL IP ADDRESS OF EAGLE-200**>/cgi-bin/post_manager"  # Location of the Eagle-200
    HEADERS = {'Content-type': 'multi-part/form-data',
               'Authorization': 'Basic <**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH EAGLE-200 AUTHORIZATION TOKEN**>'}
    r = requests.post(url, data=x, headers=HEADERS)
    structure = ast.literal_eval(r.text)
    meter_now = float(structure['Device']['Components']['Component']['Variables']['Variable']['Value'])
    return meter_now

def offpeak():
    now = datetime.datetime.now()
    now_hour = now.hour
    today = now.weekday()
    if peak_start <= now_hour < peak_end and 0 <= today <= 4:
        offpeak = "Peak"
    elif 5 <= today <= 6:
        offpeak = "Off-Peak"
    else:
        offpeak = "Off-Peak"
    return offpeak

def charging_status():
    success = 0
    while (success == 0):
        if cardata['charge_state']['charging_state'] == "Charging":
            currently_charging = "Charging"
            current_amps = int(cardata['charge_state']['charge_amps'])
        else:
            currently_charging = "Not Charging"
            current_amps = 0
        charge_level = cardata['charge_state']['battery_level']
        success = 1
    return currently_charging, current_amps, charge_level

def start_charging():
    success = 0
    while (success == 0):
        try:
            vehicles[0].command('START_CHARGE')
            success = 1
        except:
            time.sleep(10)
            continue
    return

def stop_charging():
    success = 0
    while (success == 0):
        try:
            vehicles[0].command('STOP_CHARGE')
            success = 1
        except:
            time.sleep(10)
            continue
    return

def set_charging_rate(amps):
    success = 0
    while (success == 0):
        try:
            vehicles[0].command('CHARGING_AMPS', charging_amps=amps)
            success = 1
        except:
            time.sleep(10)
            continue     
    return

def solar():
    api_key = '<**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH SOLAREDGE API KEY**>'
    site_id = '<**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH SOLAREDGE SITE ID**>'
    solaredge = 'https://monitoringapi.solaredge.com/%20site/'+ site_id + '/overview.json?api_key=' +api_key
    json_data = requests.get(solaredge).json()
    global resultK_short
    
    class solaredge():
        @staticmethod
        def solardata():
            lastupdatetime = json_data['overview']['lastUpdateTime']
            totalenergythisyear = json_data['overview']['lifeTimeData']['energy']/1000
            lastyearenergy = json_data['overview']['lastYearData']['energy']/1000
            lastmonthenergy = json_data['overview']['lastMonthData']['energy']/1000
            lastdayenergy = json_data['overview']['lastDayData']['energy']/1000
            currentpower = json_data['overview']['currentPower']['power']
            productiontoday = json_data['overview']
            return {'lastupdatetime':lastupdatetime,'totalenergythisyear': totalenergythisyear,'lastyearenergy': lastyearenergy,'lastmonthenergy': lastmonthenergy,'lastdayenergy': lastdayenergy,'currentpower':currentpower}

    result = solaredge.solardata()
    resultK = result['currentpower'] / 1000
    resultK_short = round(resultK, 2)
    return resultK_short

def write_log():
    global counter
    global fn
    if counter is None:
        counter = 0
    fn_now = time.strftime("%b%d%G")
    now = datetime.datetime.now()
    today = datetime.datetime.today()
    current_time = now.strftime("%H:%M:%S")
    battery_level = cardata['charge_state']['battery_level']
    odometer = cardata['vehicle_state']['odometer']
    odometer_short = round(odometer, 1)
    current_meter_short = round(current_meter_reading, 2)
    
    if now_hour == 5 and counter >= 5:
        counter = 1
        fn = fn_now
    else:
        counter += 1
    with open(("/home/pi/Desktop/RichardTesla/Logs/%s.csv" % fn), "a") as f:
        f.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (today, current_time, at_home, tpi, current_meter_short, current_amps, battery_level, odometer_short))
    return

#
#
#   Main Program - Suncatcher v1.0
#   Written initially by Jim Haselmaier  (c) 2022
#   http://jimhaselmaier.com/suncatcher.html
#   https://github.com/Haselmaier/Suncatcher
#
#
#
#   Adjustable Program Settings
min_night_charge = 70       # Battery % car is to be charged to at night - using energy from grid.
max_day_battery_level = 90  # Maximum battery % to be charged to using solar during the day. 
lat_home = XXXXXXXXX        # Car's latitude when parked at user's home
long_home = YYYYYYYY      # Car's longitude when parked at user's home
peak_start = 17             # Hour peak electric pricing begins (24 hour clock)
peak_end = 21               # Hour peak electric pricing ends (24 hour clock)
meter_threshold = .240      # Meter Instantaneous Deman needs to be larger than this value - in either direction - to warrant a change in car charging rate.  Value of .240 represents 1 Amp change on 240V circuit
sunrise_hour = 7
sunset_hour = 18
counter = 0
prev_meter_reading = 0
fn = time.strftime("%b%d%G")
print("\n")
print("\n")
while(1):
    now = datetime.datetime.now()
    now_hour = now.hour

#  Nightime (Off-Peak)  If battery below min nighttime level, charge it.  Otherwise do nothing.    
    while peak_end <= now_hour or now_hour < 5:   
        at_home, tpi, charge_limit = tesla_plugged_in()
        currently_charging, current_amps, charge_level = charging_status()
        while at_home == "At Home" and tpi == "Plugged In" and charge_level < min_night_charge and charge_level < charge_limit:
            if currently_charging == "Charging":
                new_amps = 32
                print("%s  Charging to minimum nighttime charge. Battery level = %s   Min nighttime charge = %s" % (time.ctime(),charge_level,min_night_charge))
                resultK_short = 0
                write_log()
            else:
                start_charging()
                new_amps = 32
                set_charging_rate(new_amps)
                print("%s  Minimum nighttime charge not reached.  Battery level = %s  Starting charging." % (time.ctime(),charge_level))
                resultK_short = 0
                write_log()
            time.sleep(1200)
            at_home, tpi, charge_limit = tesla_plugged_in()
            currently_charging, current_amps, charge_level = charging_status()
        if at_home == "At Home" and currently_charging == "Charging":
            print("%s Minimum nighttime charge reached.  Stopping charging.\n" % time.ctime())
            stop_charging()
            new_amps =0
            write_log()
        print("%s Minimum nighttime charge reached or car not home.  Sleeping for 1 hour." % time.ctime())
        sys.stdout.flush()
        time.sleep(3600)
        now = datetime.datetime.now()
        now_hour = now.hour
 
 #  Daytime.  This is when solar production is happening.
    while now_hour >= 5 and now_hour < peak_start: 
        at_home, tpi, charge_limit = tesla_plugged_in()
        currently_charging, current_amps, charge_level = charging_status()
        current_meter_reading = get_meter_reading()
        if abs(current_meter_reading) < meter_threshold:
            incremental_amps = 0
        else:
            incremental_amps = round(current_meter_reading * -1000 / 245)
        new_amps = current_amps + incremental_amps    
        while at_home == "At Home" and tpi == "Plugged In" and charge_level < max_day_battery_level and now_hour < peak_start and charge_level < (charge_limit-1):
            if new_amps > 0:
                if currently_charging == "Charging":
                    print("%s  Car is charging. Current amps: %s  Meter reading: %s Battery Level: %s Setting amps to %s." % (time.ctime(), current_amps,current_meter_reading,charge_level,new_amps))
                    set_charging_rate(new_amps)
                else:
                    print("%s  Car not charging. Meter reading=%s Battery Level=%s Charge Limit=%s  New Amps=%s." % (time.ctime(),current_meter_reading,charge_level,charge_limit,new_amps))
                    start_charging()
                    set_charging_rate(new_amps)
                solar()
                write_log()
            else:
                if currently_charging == "Charging":
                    print("%s  Car is charging.  Meter reading:  %s  Battery Level:  %s  Stopping charging." % (time.ctime(),current_meter_reading,charge_level))
                    stop_charging()
                else:
                    print("%s  Car not charging.   Meter reading:  %s   Making no changes." % (time.ctime(),current_meter_reading))
                solar()
                new_amps = 0
                write_log()
            time.sleep(600)
            at_home, tpi, charge_limit = tesla_plugged_in()
            currently_charging, current_amps, charge_level = charging_status()
            current_meter_reading = get_meter_reading()
            incremental_amps = round(current_meter_reading * -1000 / 245)
            new_amps = current_amps + incremental_amps
            now = datetime.datetime.now()
            now_hour = now.hour
            if now_hour == peak_start and currently_charging == "Charging":
                print("%s  Maximum daytime charge not reached.  Peak pricing starting.  Stopping charging.\n" % time.ctime())
                solar()
                new_amps = 0
                write_log()
        if at_home == "At Home" and tpi == "Plugged In" and currently_charging == "Charging":
            stop_charging()
            new_amps = 0
            solar()
            write_log()
        print("%s  Daytime.  Charging not needed or not possible.  At_Home = %s    Charge_level = %s." % (time.ctime(),at_home,charge_level))
        time.sleep(600)       
        now = datetime.datetime.now()
        now_hour = now.hour

# In peak pricing.  Do no charging.  Sell back as much as possible.
    while peak_start <= now.hour and now.hour < peak_end:  
        current_meter_reading = get_meter_reading()
        if abs(current_meter_reading - prev_meter_reading) >= .75:
            at_home, tpi, charge_limit = tesla_plugged_in()
            currently_charging, current_amps, charge_level = charging_status()
            if at_home == "At Home" and currently_charging == "Charging":
                print("%s  Charging during peak pricing.  Stopping charging." % time.ctime())
                new_amps = 0
                resultK_short = 0
                stop_charging()
                write_log()
        print("%s  In peak pricing.  Doing nothing." % time.ctime())
        prev_meter_reading = current_meter_reading
        time.sleep(60)
        now = datetime.datetime.now()
        now_hour = now.hour
        
        
 