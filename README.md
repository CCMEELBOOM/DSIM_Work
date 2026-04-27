# DSIM_Work Overview

<u><strong>CAD Folder</strong></u> <br>

Contains housing desing for side hydrophones. Housing was printed in PETG. <br>

<img width="732" height="662" alt="DSIM_BlueRov_with_attachments_isotropic" src="https://github.com/user-attachments/assets/2c04db84-df4a-4d9f-97c8-9e135e1f634b" />
<br>

<u><strong>CODE Folder</strong></u> <br>

This folder contains code for two nodes that publish cost data to the ESC algorithm. <br>

**Node 1**  <br>

The first node take angle data from the feedback wire of a Parallax 360 servo and publishes it to /servo_angles topic. <br>

The .ino is run locally on the Arduino which is mounted on the BlueROV2. This sketch is uploded before anything else. <br>

Then the talk-to-pc.py file is run on the Rasberry Pi mounted on the BlueRov2 to relay angle data to  the PC. <br>

**Node 2** <br>

This node take voltage values from the hydrophones, converts these values to pressure and then converts pressure values to decibels. <br>

The data processeing occurs locally on the Rasberry Pi and the process data is relayed to ROS 2 running locally on the PC. 
