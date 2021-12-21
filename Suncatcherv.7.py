
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
        with teslapy.Tesla('<email for your Tesla account at tesla.com>') as tesla:
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
    lat = cardata['drive_state']['latitude']
    long = cardata['drive_state']['longitude']
    plug_status = cardata['charge_state']['charge_port_door_open']
    if lat_home-.0001 <= lat <= lat_home+.0001 and long_home-.0001 <= long <= long_home+.0001:
        at_home = "At Home"
    else:
        at_home = "Not At Home"
    if plug_status:
        tpi = "Plugged In"
    else:
        tpi = "Not Plugged In"
    return at_home, tpi

def get_meter_reading():
    x = open('commands.xml', 'r').read()  # Commands to be processed by the Eagle-200
    url = "http://<Eagle-200 IP Address>/cgi-bin/post_manager"  # IP Address of Eagle-200
    HEADERS = {'Content-type': 'multi-part/form-data',
               'Authorization': 'Basic MDA2NmIwOjEwY2IxN2M0NmQyNmM2ZDU='}
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

def write_log(current_amps):
    api_key = '<Your Solaredge API key>'
    site_id = '<Your Solaredge Site ID>'
    solaredge = 'https://monitoringapi.solaredge.com/%20site/'+ site_id + '/overview.json?api_key=' +api_key
    json_data = requests.get(solaredge).json()

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
    now = datetime.datetime.now()
    today = datetime.datetime.today()
    current_time = now.strftime("%H:%M:%S")
    battery_level = cardata['charge_state']['battery_level']
    odometer = cardata['vehicle_state']['odometer']
    odometer_short = round(odometer, 1)
    resultK = result['currentpower'] / 1000
    resultK_short = round(resultK, 2)
    current_meter_short = round(current_meter_reading, 2)
    with open("TeslaLog.csv", "a") as f:
        f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (today, current_time, at_home, tpi, rate, current_amps, resultK_short, current_meter_short, battery_level, odometer_short))

#
#
#
#  Suncatcher - Tesla charging automation software
#  Initially written by Jim Haselmaier; Dec 2021
#
#
#  SETTINGS
min_night_charge = 50  #<--- Battery percent user wants the software to charge to at night time
lat_home = xxx  #<---  Latitude of user's home (charging location).  Enter # to at least 4 decimal places.
long_home = yyy  #<---  Longitude of user's home (charging location)  Enter # to at least 4 decimal places.
poll_interval = 10  #<--- Number of minutes to wait between checks to see if charging needs to be updated
#
#  The following settings need to be updated manually when the time-of-day rate change occurs in the Spring & Fall.
peak_start = 17  #<--- Time peak electric charge rate begins.
peak_end = 21  #<---  Time peak electric charge rate ends.

while(1):
    print("\n")
    now = datetime.datetime.now()
    now_hour = now.hour
    print(time.ctime())
    while 21 <= now_hour or now_hour < 6:
        at_home, tpi = tesla_plugged_in()
        currently_charging, current_amps, charge_level = charging_status()
        rate = offpeak()
        current_meter_reading = get_meter_reading()
        print("currently_charging = %s" % currently_charging)
        print("current_amps = %s" % current_amps)
        print("charge_level = %s" % charge_level)
        if currently_charging == "Charging" and at_home == "At Home" and charge_level < min_night_charge+2 and tpi == "Plugged In":
            print("\nNight time.  Car is charging.  Battery level below Min Night Time Charge.")
            current_amps = 32
        elif currently_charging == "Charging" and at_home == "At Home" and charge_level > min_night_charge and tpi == "Plugged In":
            print("\nNight time.  Min Night Time Charge reached.  Charging being stopped.")
            stop_charging()
            current_amps = 0
        elif currently_charging == "Not Charging" and at_home == "At Home" and charge_level < min_night_charge and tpi == "Plugged In":
            print("\nNight time.  Not charging.  Min Night Time Charge not reached.  Starting charging.")
            start_charging()
            time.sleep(20)
            set_charging_rate(32)
            current_amps = 32
        else:
            print("\nNight time.  Not charging.  Min Night Time Charge reached.  No action taken.")
            time.sleep(1200)
            current_amps = 0
        write_log(current_amps)
        time.sleep(poll_interval*60)
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
    if at_home == "At Home" and tpi == "Plugged In" and rate == "Off-Peak":
        print("Meter currently reads %s kW." % current_meter_reading)
        incremental_amps = round(current_meter_reading * -1000 / 245)
        new_amps = current_amps + incremental_amps
        print("incremental_amps = %s" % incremental_amps)
        print("new_amps = %s" % new_amps)
        if current_meter_reading >= 0.40:
            if currently_charging == "Charging":
                if new_amps <= 0:
                    print("\nResult:  Solar production insufficient to cover home consumption.  Car charging being stopped.\n\n")
                    stop_charging()
                    write_log(0)
                else:
                    print("\nResult:  Electricity being pulled from grid.  Reducing rate of car charging.")
                    print("         New amp setting:  %s Amps\n\n" % new_amps)
                    set_charging_rate(new_amps)
                    write_log(new_amps)
            else:
                print("\nResult:  Eletricity being pulled from grid.  Car is not charging.  Making no changes.\n\n")
                write_log(0)
        elif current_meter_reading < -0.10:
            if currently_charging == "Charging":
                print("\nResult:  Sending power to grid.  Car is charging.  Increasing car charge rate.")
                print("         New amp setting:  %s Amps\n\n" % new_amps)
                set_charging_rate(new_amps)
                write_log(new_amps)
            else:
                print("\nResult:  Sending power to grid.  Car is not charging.  Start charging.")
                print("         New amp setting:  %s Amps\n\n" % new_amps)
                start_charging()
                time.sleep(20)
                set_charging_rate(new_amps)
                write_log(new_amps)
        else:
            print("\nResult:  Consumption matches solar production.  No changes will be made.")
            print("current_amps = %s\n\n" % current_amps)
            write_log(current_amps)
    else:
        if currently_charging == "Charging":
            print("\nResult:  Car is charging but should not be.  Charging will be stopped.")
            stop_charging()
        else:
            print("\nResult:  Car not able to be charged.  No action taken.")
            write_log(0)
    print("**********************")
    time.sleep(poll_interval*60)
