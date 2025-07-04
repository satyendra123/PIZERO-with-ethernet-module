# PIZERO-with-ethernet-module
PI zero ko humne ENC28j60 module ke sath connect kiya tha kota turnstile project

step-1
ENC28J60 Pin	Raspberry Pi GPIO
VCC	- 3.3V (Pin 1)
GND	- GND (Pin 6)
SCK	- GPIO11 (Pin 23)
SO (MISO)	- GPIO9 (Pin 21)
SI (MOSI)	- GPIO10 (Pin 19)
CS (or NSS)	- GPIO8 (Pin 24)

step-2
Enable SPI on Raspberry Pi
sudo raspi-config
Interface Options → SPI → Yes (enable)
sudo reboot

step-3
Enable ENC28J60 in config.txt
dtoverlay=enc28j60
Press Ctrl + X, then Y, then Enter
sudo reboot

step-4
Set a Static IP Address
sudo nano /etc/dhcpcd.conf
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 1.1.1.1


step-5
ifconfig eth0

 
