
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
        #print("Top of while loop in tesla_plugged_in function.")
        with teslapy.Tesla('<**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH EMAIL ADDRESS FOR REGISTERED TESLA ACCOUNT**>') as tesla:
            try:
                vehicles = tesla.vehicle_list()
            except:
                time.sleep(10)
                continue
            try:
                vehicles[0].sync_wake_up()
            except:
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
    battery_level = cardata['charge_state']['battery_level']
    
    print("lat_raw = %s" % lat_raw)
    print("longitude_raw = %s" % longitude_raw)
    
    if (lat_home - .0002) <= lat_raw <= (lat_home + .0002) and (long_home - .0002) <= longitude_raw <= (long_home + .0002):
        at_home = "At Home"
    else:
        at_home = "Not At Home"
    if plug_status:
        tpi = "Plugged In"
    else:
        tpi = "Not Plugged In"
    return at_home, tpi, battery_level

def get_meter_reading():
    x = open('commands.xml', 'r').read()  # Commands to be processed by the Eagle-200
    url = "http://<**EAGLE-200 IP ADDRESS**>/cgi-bin/post_manager"  # Location of the Eagle-200
    HEADERS = {'Content-type': 'multi-part/form-data',
               'Authorization': 'Basic <**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH EAGLE 32-char AUTH TOKEN**>'}  #  See documentation
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
    api_key = '<**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH SOLAREDGE INVERTER API KEY**>'  #  See documentation
    site_id = '<**REPLACE ANGLE BRACKETS AND EVERYTHING IN BETWEEN WITH SOLAREDGE SITE ID**>'           #  See documentation
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
    
    if now_hour == 5 and counter >= 25:
        counter = 1
        fn = fn_now
    else:
        counter += 1
    with open(("/home/pi/Desktop/Tesla/Logs/%s.csv" % fn), "a") as f:
        f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (today, current_time, at_home, tpi, rate, current_amps, resultK_short, current_meter_short, battery_level, odometer_short))
    return

#
#
#   Main Program - Suncatcher v0.9
#   Written initially by Jim Haselmaier  (c) 2022
#   http://jimhaselmaier.com/suncatcher.html
#   https://github.com/Haselmaier/Suncatcher
#
#
#
#   Adjustable Program Settings
min_night_charge = 50       # Battery % car is to be charged to at night - using energy from grid
max_day_battery_level = 65  # Maximum battery % to be charged to using solar during the day
lat_home = 40.5069          # Car's latitude when parked at user's home
long_home = -105.0854       # Car's longitude when parked at user's home
peak_start = 17             # Hour peak electric pricing begins (24 hour clock)
peak_end = 21               # Hour peak electric pricing ends (24 hour clock)
pull_threshold = .40        # Max amount (kWh) that is willing to be pulled from the grid without changing car charging rate
push_threshold = .240       # Min amount (kWh) that must be pushed to the grid to cause car charging rate to be changed


counter = 0
fn = time.strftime("%b%d%G")

while(1):
    print("\n")
    now = datetime.datetime.now()
    now_hour = now.hour
    print(time.ctime())
    while peak_end <= now_hour or now_hour < 5:
        at_home, tpi, battery_level = tesla_plugged_in()
        currently_charging, current_amps, charge_level = charging_status()
        rate = offpeak()
        current_meter_reading = get_meter_reading()
        print("at_home = %s" % at_home)
        print("currently_charging = %s" % currently_charging)
        print("current_amps = %s" % current_amps)
        print("charge_level = %s" % charge_level)
        if currently_charging == "Charging" and at_home == "At Home" and charge_level <= min_night_charge and tpi == "Plugged In":
            print("\nNight time.  Car is charging.  Battery level below Min Night Time Charge.")
            new_amps = 32
        elif currently_charging == "Charging" and at_home == "At Home" and charge_level > min_night_charge and tpi == "Plugged In":
            print("\nNight time.  Min Night Time Charge reached.  Charging being stopped.")
            stop_charging()
            new_amps = 0
        elif currently_charging == "Not Charging" and at_home == "At Home" and charge_level < min_night_charge and tpi == "Plugged In":
            print("\nNight time.  Not charging.  Min Night Time Charge not reached.  Starting charging.")
            start_charging()
            time.sleep(20)
            set_charging_rate(32)
            new_amps = 32
        else:
            print("\nNight time.  Not charging.  Min Night Time Charge reached.  No action taken.")
            new_amps = 0
        resultK_short = 0
        write_log()
        time.sleep(600)   #  Sleep for 10 minutes
        now = datetime.datetime.now()
        now_hour = now.hour

    at_home, tpi = tesla_plugged_in()
    rate = offpeak()
    currently_charging, current_amps, charge_level = charging_status()

    print("\nCar Location:  %s" % at_home)
    print("Charging Cable:  %s" % tpi)
    print("Electricity Cost Rate:  %s" % rate)
    print("Current Car Charging Status:  %s" % currently_charging)
    print("Current Amp Setting:  %s" % current_amps)
    current_meter_reading = get_meter_reading()
    if at_home == "At Home" and tpi == "Plugged In" and rate == "Off-Peak" and battery_level <= max_day_battery_level:
        print("Meter currently reads %s kW." % current_meter_reading)
        incremental_amps = round(current_meter_reading * -1000 / 245)
        new_amps = current_amps + incremental_amps
        print("incremental_amps = %s" % incremental_amps)
        print("new_amps = %s" % new_amps)
        if current_meter_reading >= pull_threshold:
            if currently_charging == "Charging":
                if new_amps <= 0:
                    print("\nResult:  Solar production insufficient to cover home consumption.  Car charging being stopped.\n\n")
                    stop_charging()
                    new_amps = 0
                    solar()
                    write_log()
                else:
                    print("\nResult:  Electricity being pulled from grid.  Reducing rate of car charging.")
                    print("         New amp setting:  %s Amps\n\n" % new_amps)
                    set_charging_rate(new_amps)
                    solar()
                    write_log()
            else:
                print("\nResult:  Eletricity being pulled from grid.  Car is not charging.  Making no changes.\n\n")
                new_amps = 0
                solar()
                write_log()
        elif current_meter_reading < pull_threshold:
            if currently_charging == "Charging":
                print("\nResult:  Sending power to grid.  Car is charging.  Increasing car charge rate.")
                print("         New amp setting:  %s Amps\n\n" % new_amps)
                set_charging_rate(new_amps)
                solar()
                write_log()
            else:
                print("\nResult:  Sending power to grid.  Car is not charging.  Start charging.")
                print("         New amp setting:  %s Amps\n\n" % new_amps)
                start_charging()
                set_charging_rate(new_amps)
                solar()
                write_log()
        else:
            print("\nResult:  Consumption matches solar production.  No changes will be made.")
            print("current_amps = %s\n\n" % current_amps)
            new_amps = current_amps
            solar()
            write_log()
    else:
        if currently_charging == "Charging":
            print("\nResult:  Car is charging but should not be.  Charging will be stopped.")
            solar()
            stop_charging()
            new_amps = 0
            solar()
            write_log()
        else:
            print("\nResult:  Car not able to be charged.  No action taken.")
            new_amps = 0
            solar()
            write_log()
    print("**********************")
    time.sleep(600)   #  Sleep for 10 mins
