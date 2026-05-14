# DSIM_Data_Nodes


The DSIM_Data_Nodes encompass the acquisition of the angle of the servos direction and sensor data. 

----------------------------------------
Angle Acquisition:

The scripts to capture the angle position of the servos is found in Servo_Angles. The directory is composed of two scripts that need to run simultaneously to properly acquire data. The multi_servo_angle_node_new.py file creates a publisher node that will collect data from the servo-back-and-forth-new.ino script and then publish it as a topic for subscriber nodes to pick up information.

This directory is important as it is necessary to keep track of the the angular position of the sensors to properly estimate the position of the source and the central position of the submarine itself. 

Further Details:
The servo-back-and-forth-new.ino script is home to an oscillating function that will move the sensors around while also tracking their angular positions.
Notice that the servo-back-and-forth-new.ino script is not in python but in Arduino Language as the servos are directly controlled by an Arduino Controller. Thus, when modifying servo-back-and-forth-new.ino, make sure to employ the appropriate language. 

The creation of the multi_servo_angle_node_new.py was inspired by a tutorial found on the internet. For further information, please refer to Appendix, ROS2 Tutorial.

Any other details about the code can be found in the scripts themselves. 

----------------------------------------
Sensor Data Acquisition:

~ ~ ~

----------------------------------------

----------------------------------------
Appendix

Parallax Feedback 360° High-Speed Servo Documentation: https://www.pololu.com/file/0J1395/900-00360-Feedback-360-HS-Servo-v1.2.pdf

ROS2 Tutorial: https://www.youtube.com/watch?v=0aPbWsyENA8&list=PLLSegLrePWgJudpPUof4-nVFHGkB62Izy 

Useful Tools:

Graph Digitizer: https://huangziyuan10-a11y.github.io/graph-digitizer-web/
