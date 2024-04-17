There are 2 types of UART interface existed on Raspberry Pi, mini UART & PL011 UART.
By default, /dev/ttyS0 maps to mini UART; on the other hand, /dev/ttyAMA0 maps to PL011 UART.
Software Setup
Open a terminal and change the file config.txt in /boot directory with root privilege.

$ sudo su
# vim /boot/config.txt
add following lines at the end of the file

# enable serial interface
enable_uart=1
dtoverlay=uart0
dtoverlay=uart1
dtoverlay=uart2
dtoverlay=uart3
dtoverlay=uart4
dtoverlay=uart5
save & exit, then reboot !

Check system open the serial by command $ ls -al /dev/ttyAMA*
$ ls -al /dev/ttyAMA*
crw-rw---- 1 root dialout 204, 64 Dec 16 16:01 /dev/ttyAMA0
crw-rw---- 1 root dialout 204, 65 Dec 16 16:01 /dev/ttyAMA1
crw-rw---- 1 root dialout 204, 66 Dec 16 16:01 /dev/ttyAMA2
crw-rw---- 1 root dialout 204, 67 Dec 16 16:01 /dev/ttyAMA3
crw-rw---- 1 root dialout 204, 68 Dec 16 16:01 /dev/ttyAMA4

Hardware Setup
Raspberry Pi Pin pair with uart :
           TXD       RXD         Communication Port
uart0 :  GPIO 14    GPIO 15         /dev/ttyAMA0 
uart1 :  GPIO 0     GPIO 1          /dev/ttyAMA1
uart2 :  GPIO 4     GPIO 5          /dev/ttyAMA2
uart3 :  GPIO 8     GPIO 9          /dev/ttyAMA3
uart4 :  GPIO 12    GPIO 13         /dev/ttyAMA4
