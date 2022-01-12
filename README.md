# Suncatcher

Capabilities Summary
<ul>
  <li>During the day, Suncatcher (on a 10 min interval) 1/ determines if electricty is being pulled from the grid (consumption greater than current solar production) or being pushed to the grid (consumption is less than current solar production).
  <li>Suncatcher adjusts the Tesla charging rate based on how much electricity is being pushed to or pulled from the grid - with the goal being to have all solar output either being consumed by the home or sent to the car.  When electricity is being pulled from the grid the car charging rate is reduced.  When electricity is being sent to the grid the car charging rate is increased. 
  <li>Suncatcher will charge the car at night (from the grid) to a minimum level - as specified by the user.  The intent/assumption is that a minimum charge is desired to be had at the end of the day in case of unexpected emergencies.  (e.g. drive to the hospital in the middle of the night).  The author's use case causes this to be set to 50%.
  <li>Suncatcher has implemented the capability to stop car charging during the day when a certain battery percentage has been reached.  Ex:  The author rarely needs more than 15% of battery for normal, daily driving.  Suncatcher will stop charging during the day when battery charge is 15% higher than the minimum required night time charge.  The presumption is any amount needed over what is needed for daily driving is best sold back to the utility for bill credit.  Therefore, the author's use case causes this setting to be 65%.
  <li>A detailed log is written every 10 minutes to /home/pi/Desktop/Tesla/Logs - with each day (starting at 5:00am) having it's own log file.
</ul>  
Requirements
<ul>
  <li>Eagle-200 device from Rainforest Automation.  Connects wirelessly (via zigbee) to consumer's smart electric meter.</li>
  <li>Device that can run Python. (PC, Linux system, Raspberry Pi)</li>
</ul>
Configuration (assumes Raspberry Pi)
<ul>
  <li>Create directory:  /home/pi/Desktop/Tesla
  <li>Create directory:  /home/pi/Desktop/Tesla/Logs
  <li>Install Python packages:  teslapy, ast, requests
  <li>Place commands.xml in /home/pi/Desktop/Tesla
  <li>Place Suncatcher source in /home/pi/Desktop/Tesla
  <li>Make necessary changes to Suncatcher source:
    <ul>
      <li>Line 14:  Enter email address for Tesla account that contains car to be charged using Suncatcher.
      <li>Line 51:  Enter local IP address for Eagle-200.
      <li>Line 53:  Enter 32-character authorization token for Eagle-200. The token is created by encoding <6 character cloudID>;<16 character install code> to Base64.  (**IMPORTANT**:  Note semi-colon between cloudID and install code.)  These two values are found on the back of the Eagle-200 device.  This encoder is one that the author has used:  https://www.base64encode.org/
      <li>Line 119:  Solaredge Inverter API key.  This can be obtained from Solaredge or your solar panel installer.
      <li>Line 120:  Solaredge Site ID:  This can be found in your Solaredge account.
      <li>Line 175:  Minimum car battery % Suncatcher should charge to at night - using electricity from the grid.
      <li>Line 176:  Maximum car battery % Suncatcher should charge to during the day.
      <li>Line 177:  Latitude of user's home.
      <li>Line 178:  Longitude of user's home.
      <li>Line 179:  Hour peak electric pricing begins.
      <li>Line 180:  Hour peak electric pricing ends.
      <li>Line 181:  Minimum amount of electricity that is being pulled from the grid to cause a re-calculation of car charging rate to be done.  (pulling less than this amount will cause the car charging rate to not be changed.)
      <li>Line 182:  Minimum amount of electricity that is being pushed to the grid to cause a re-calculation of car charging rate to be done.  (pushing less than this amount will cause the car charging rate to not be changed.)
        </ul>
        </ul>
        
    

