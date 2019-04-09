# Using the Raspberry Pi as an access point to share an internet connection (bridge)

One common use of the Raspberry Pi as an access point is to bridge internet from an Ethernet port to any wireless connection.

To do this, a 'bridge' needs to put in place between the wireless device and the Ethernet device on the access point Raspberry Pi.
This bridge will pass all traffic between the two interfaces. Install the following packages to enable the access point setup and bridging.

```
sudo apt-get install hostapd bridge-utils
```

Since the configuration files are not ready yet, turn the new software off as follows:
```
sudo systemctl stop hostapd
```
Bridging creates a higher-level construct over the two ports being bridged. It is the bridge that is the network device, so we need to stop the eth0 and wlan0 ports being allocated IP addresses by the DHCP client on the Raspberry Pi.
```
sudo nano /etc/dhcpcd.conf
```
Add `denyinterfaces wlan0` and `denyinterfaces eth0` to the end of the file (but above any other added interface lines) and save the file.

Add a new bridge, which in this case is called br0.
```
sudo brctl addbr br0
```
Connect the network ports. In this case, connect eth0 to the bridge br0.
```
sudo brctl addif br0 eth0
```
Now the interfaces file needs to be edited to adjust the various devices to work with bridging. sudo nano /etc/network/interfaces make the following edits.

Add the bridging information at the end of the file.
```
# Bridge setup
auto br0
iface br0 inet manual
bridge_ports eth0 wlan0
```

The access point setup is almost the same as that shown in the previous section. Follow all the instructions in the  Configuring the access point host software (hostapd) section above to set up the hostapd.conf file and the system location, but add bridge=br0 below the interface=wlan0 line, and remove or comment out the driver line. The passphrase must be between 8 and 64 characters long.

To use the 5 GHz band, you can change the operations mode from 'hw_mode=g' to 'hw_mode=a'. The possible values for hw_mode are:

* a = IEEE 802.11a (5 GHz)
* b = IEEE 802.11b (2.4 GHz)
* g = IEEE 802.11g (2.4 GHz)
* ad = IEEE 802.11ad (60 GHz). Not available on Raspberry Pi.

```
interface=wlan0
bridge=br0
#driver=nl80211
ssid=NameOfNetwork
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=AardvarkBadgerHedgehog
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

Now reboot the Raspberry Pi.
```
sudo reboot
```

There should now be a functioning bridge between the wireless LAN and the Ethernet connection on the Raspberry Pi, and any device associated with the Raspberry Pi access point will act as if it is connected to the access point's wired Ethernet.

The ifconfig command will show the bridge, which will have been allocated an IP address via the wired Ethernet's DHCP server. The wlan0 and eth0 no longer have IP addresses, as they are now controlled by the bridge. It is possible to use a static IP address for the bridge if required, but generally, if the Raspberry Pi access point is connected to a ADSL router, the DHCP address will be fine.
