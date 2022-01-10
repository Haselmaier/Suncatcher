# Suncatcher

Suncatcher automates various aspects of Tesla EV charging:
<ul>
  <li>Adjusts rate of car charging based on solar panel output.  (The objective is for all "unused" power coming from solar to be directed into the car.)</li>
  <li>For those that have time-of-day electric pricing, charge only during the off-peak timeframes.</li>
  <li>Charge the car to a minimum amount each night; to satisfy a desired base level of charge one would want to have available.</li>
</ul>

Suncatcher - Capability Summary
<ul>
  <li>During the day, Suncatcher (on a 10 min interval) 1/ determines if electricty is being pulled from the grid (consumption greater than current solar production) or being pushed to the grid (consumption is less than current solar production).
  <li>Suncatcher adjusts the Tesla charging rate based on how much electricity is being pushed to or pulled from the grid - with the goal being to have all solar output either being consumed by the home or sent to the car.  When electricity is being pulled from the grid the car charging rate is reduced.  When electricity is being sent to the grid the car charging rate is increased. 
  <li>Suncatcher will charge the car at night (from the grid) to a minimum level - as specified by the user.  The intent/assumption is that a minimum charge is desired to be had at the end of the day in case of unexpected emergencies.  (e.g. drive to the hospital in the middle of the night).  The author's use case causes this to be set to 50%.
  <li>Suncatcher has implemented the capability to stop car charging during the day when a certain battery percentage has been reached.  Ex:  The author rarely needs more than 15% of battery for normal, daily driving.  Suncatcher will stop charging during the day when battery charge is 15% higher than the minimum required night time charge.  The presumption is any amount needed over what is needed for daily driving is best sold back to the utility for bill credit.  Therefore, the author's use case causes this setting to be 65%.
  <li>A detailed log is written every 10 minutes to /home/pi/Desktop/Tesla/Logs - with each day (starting at 5:00am) having it's own log file.
    
Requirements for running Suncatcher:
<ul>
  <li>Eagle-200 device from Rainforest Automation.  Connects wirelessly (via zigbee) to consumer's smart electric meter.</li>
  <li>Device that can run Python. (PC, Linux system, Raspberry Pi)</li>
</ul>


