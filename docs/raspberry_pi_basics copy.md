# Raspberry Pi basics

######################################################
######################################################
######################################################

## ADVANCED TOPICS

TODO...

######################################################
######################################################
######################################################

### Configuration files.

In WURB there is a clear difference between settings and configuration. Settings are something that the user can control via the user interface and these take effect immediately. Configuration, on the other hand, is something that takes effect at startup

### Shortcuts

If you need to start and stop the services that run Wurb and Wirc, there are some practical
commands that can be activated.
There are also some commands that can be used to update the program code to the latest version
as well as to test run the code for better error printing.

Install these like this:

cp ...
chmod ...
source /etc/bash.bashrc

The commands that will then be available are:

- wurb-on
- wurb-off
- wirc-on
- wirc-off

### Updating the software

sudo apt update
sudo apt upgrade -y

- wurb-gitpull
- wirc-gitpull

- wurb-run
- wirc-run
- search for rpi in local network.

## Troubleshooting

1. a
2. b
3. c
4. d

For Raspberry Pi 5, there are a few tricks that can work in cases where you have problems with the power supply or cables. If you have your own power supply that you know can deliver 5A at 5V, you can add these two lines to the end of the "/boot/firmvare/config.txt" file:

PWD_??????=5000000
????=1

Another way to prevent it from shutting down is to limit the CPU clock frequency to the idle frequency.
This is done by adding this line to the end of the file "/boot/firmvare/config.txt":

arm_freq=5000000

One problem, however, is that for some reason it does not start the Pettersson M500-384 if it is connected when the detector starts. There is a solution to this, see below under recommended microphones.


Please contact me if  there are more commonly used microphones that should be added to the list of automatically supported microphones.

 