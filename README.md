# Intermapper probe for Comtrend DSL modem

I wanted to keep track of the Signal to Noise Ratio (SNR) for my DSL modem. 
I was losing connections overnight, and wanted to prove to my ISP that this was happening. 

Intermapper now monitors and plots the SNR continually, so it's easy to see dips in the signal quality, and the times they occur. 
This helped my ISP figure out what was happening.

## The Probe

This probe demonstrates a detailed InterMapper command-line probe, using the IMDC Python interpreter.

This probe connects to a Comtrend DSL modem's web interface, and retrieves its SNR values and uptime values. 
This has been tested with a Comtrend AR-5381U modem.
Here's the Status Window:

![Probe for Comtrend Modem](https://github.com/richb-hanover/IMProbe-Comtrend/blob/master/ComtrendModem.png?raw=true)

**To use the probe** 

1. Use **File->Import Probe** and select the probe file `com.blueberryhillsoftware.comtrend.txt`
2. Select the probe from **Miscellaneous/Comtrend DSL Stats**

**To edit the probe**

1. Edit the probe file `com.blueberryhillsoftware.comtrend.txt` to change the appearance of the Status Window, or...
2. Edit and test the Python program in the `im_comtrend.py` file then copy/paste its contents into the `<tool> ... </tool>` section of the `com.blueberryhillsoftware.comtrend.txt` probe file and re-import it.

See the full documentation at: [https://github.com/richb-hanover/IMProbe-Comtrend](https://github.com/richb-hanover/IMProbe-Comtrend)

--------
Copyright (c) 2017 - Rich Brown, [Blueberry Hill Software](http://blueberryhillsoftware.com), an Intermapper consultancy

MIT License - See the LICENSE file for the full statement
