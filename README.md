# Suncatcher

Suncatcher automates various aspects of Tesla EV charging:
<ul>
  <li>Adjusts rate of car charging based on solar panel output.  (The objective is for all "unused" power coming from solar to be directed into the car.)</li>
  <li>For those that have time-of-day electric pricing, charge only during the off-peak timeframes.</li>
  <li>Charge the car to a minimum amount each night; to satisfy a desired base level of charge one would want to have available.</li>
</ul>

Requirements for running Suncatcher:
<ul>
  <li>Eagle-200 device from Rainforest Automation.  Connects wirelessly (via zigbee) to consumer's smart electric meter.</li>
  <li>Device that can run Python. (PC, Linux system, Raspberry Pi)</li>
  <li>Required Python packages:  ast, requests, teslapy</li>
</ul>


