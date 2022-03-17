# Suncatcher

<b>Capabilities Summary</b>
<ul>
  <li>During the day Suncatcher (on a 10 min interval) 1/ determines if electricty is being pulled from the grid (consumption in the home is greater than current solar production) or being pushed to the grid (current solar production is greater than electricity consumption).
  <li>Suncatcher adjusts the Tesla charging rate based on how much electricity is being pushed to or pulled from the grid - with the goal being to have all solar output either being consumed by the home or sent to the car.  When electricity is being pulled from the grid the car charging rate is reduced.  When electricity is being sent to the grid the car charging rate is increased. 
  <li>Suncatcher will charge the car at night (from the grid) to a minimum level - as specified by the user.  The intent/assumption is that a minimum charge is desired to be had at the end of the day in case of unexpected emergencies.  (e.g. drive to the hospital in the middle of the night).  The author's use case causes this to be set to 50%.
  <li>Suncatcher will stop car charging during the day when a certain battery percentage has been reached.  Ex:  The author rarely needs more than 15% of battery for normal, daily driving.  Suncatcher will stop charging during the day when battery charge is 15% higher than the minimum required night time charge.  The presumption is any amount needed over what is needed for daily driving is best sold back to the utility for bill credit.  
  <li>A detailed log is written every 10 minutes to /home/pi/Desktop/Tesla/Logs - with each day (starting at 5:00am) having it's own log file.
</ul>  
<b>Requirements</b>
<ul>
  <li>Eagle-200 energy gateway from Rainforest Automation.  Connects wirelessly (via zigbee) to consumer's smart electric meter.  Connecting the Eagle-200 with the smart meter reuires coordination with the utility.  The utility goes through a procurement process to permit the meter to connect with the energy gateway.  This process can take 3-8 days total.</li>
  <li>Device that can run Python. (PC, Linux system, Raspberry Pi)</li>
  <li>Solaredge solar panel inverter.  Having this inverter isn't <b>really</b> a requirement.  The software is set up to capture current solar panel output - which gets written to the log file every 10 minutes.  This information isn't essential to effective Tesla charging control, but it is interesting information to have in order to track solar production along with charging rate.  If the user does not have a Solaredge inverter calls to the 'solar' function can simply be commented out.
</ul>
<b>Configuration (assumes Raspberry Pi)</b>
<ul>
  <li>Create directory:  /home/pi/Desktop/Tesla
  <li>Create directory:  /home/pi/Desktop/Tesla/Logs
  <li>Install Python packages:  teslapy, ast, requests
  <li>Place commands.xml in /home/pi/Desktop/Tesla. This file contains the commands needed for the Eagle-200 energy gateway.
  <li>Place Suncatcher source in /home/pi/Desktop/Tesla
  <li>Make necessary changes to Suncatcher source:
    <ul>
      <li>Line 13:  Enter email address for Tesla account that contains car to be charged using Suncatcher.
      <li>Line 50:  Enter local IP address for Eagle-200.
      <li>Line 52:  Enter 32-character authorization token for Eagle-200. The most reliable way to generate the token is using the Advanced REST Client.  Enter Eagle-2-- cloudID as the username and its install code as the password.  The REST Client will generate the token - which can be entered into the Suncatcher code. 
      <li>Line 117:  Solaredge Inverter API key.  This can be obtained from Solaredge or your solar panel installer.
      <li>Line 118:  Solaredge Site ID:  This can be found in your Solaredge account.
      <li>Line 159:  Adjust location where logs are to be written as desired.
      <li>Line 173:  Minimum car battery % Suncatcher should charge to at night - using electricity from the grid.
      <li>Line 174:  Maximum car battery % Suncatcher should charge to during the day.
      <li>Line 175:  Latitude of user's home.
      <li>Line 176:  Longitude of user's home.
      <li>Line 177:  Hour peak electric pricing begins.
      <li>Line 178:  Hour peak electric pricing ends.
      <li>Line 179:  Minimum amount of electricity that is being pulled from the grid to cause a re-calculation of car charging rate to be done.  (pulling less than this amount will cause the car charging rate to not be changed.)
      <li>Line 180:  Minimum amount of electricity that is being pushed to the grid to cause a re-calculation of car charging rate to be done.  (pushing less than this amount will cause the car charging rate to not be changed.)
      </ul>
</ul>

<b>First Use</b>     
The Tesla API requires authorization tokens in order to get information from the car as well as change car settings.  When the program is first run a web browser will be launched with fields to enter Tesla account credentials (email and password).  The resulting web page will have an error displayed.  However the URL in the browser needs to be copied in its entirety and pasted into the field presented by the software.  The resulting tokens will be written to a file.  This login sequence will only need to be done the first time the software is run.  
        
<b>Stability / Bugs</b><br>
The code is reasonably stable.  Error checking has not been implemented in some areas (such as getting status from the Eagle-200) which can cause the software to crash.  It needs to be monitored to see if it has crashed.  No auto-restart capability has yet been implemented in the event of a crash.
        
        
    

