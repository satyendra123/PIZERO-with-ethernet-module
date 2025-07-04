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
Note- yaha se hume static ip mil jayega jo humne set kiya hai wo hi hai yaa nahi

step-6
There are 2 types of UART interface existed on Raspberry Pi, mini UART & PL011 UART. By default, /dev/ttyS0 maps to mini UART; on the other hand, /dev/ttyAMA0 maps to PL011 UART. Software Setup Open a terminal and change the file config.txt in /boot directory with root privilege.

$ sudo su

vim /boot/config.txt
add following lines at the end of the file

enable serial interface
enable_uart=1 dtoverlay=uart0 dtoverlay=uart1 dtoverlay=uart2 dtoverlay=uart3 dtoverlay=uart4 dtoverlay=uart5 save & exit, then reboot !

Check system open the serial by command $ ls -al /dev/ttyAMA* $ ls -al /dev/ttyAMA* crw-rw---- 1 root dialout 204, 64 Dec 16 16:01 /dev/ttyAMA0 crw-rw---- 1 root dialout 204, 65 Dec 16 16:01 /dev/ttyAMA1 crw-rw---- 1 root dialout 204, 66 Dec 16 16:01 /dev/ttyAMA2 crw-rw---- 1 root dialout 204, 67 Dec 16 16:01 /dev/ttyAMA3 crw-rw---- 1 root dialout 204, 68 Dec 16 16:01 /dev/ttyAMA4

Hardware Setup Raspberry Pi Pin pair with uart : TXD RXD Communication Port uart0 : GPIO 14 GPIO 15 /dev/ttyAMA0 uart1 : GPIO 0 GPIO 1 /dev/ttyAMA1 uart2 : GPIO 4 GPIO 5 /dev/ttyAMA2 uart3 : GPIO 8 GPIO 9 /dev/ttyAMA3 uart4 : GPIO 12 GPIO 13 /dev/ttyAMA4
