# LOCAR Control Pi
The following information pertains to the Control Raspberry Pi of the LOCAR system

---
## Installation
The Control Pi performs two tasks:
1.  Operates all Array Pis of the LOCAR system through a secure, local wireless network
2.  Operates the Pi camera and NeoPixel LED Ring of the LOCAR system

The proper installation of the Control Pi requires the **sequential and orderly** completion of the following steps:
1.  **Prepare the Raspbian image for Pi camera and NeoPixel control, as done [here](https://github.com/pd3d/magneto/tree/locar/Builds/LOCAR/Software/Raspberry%20Pi/Control/Python)**
    * The user may, alternatively, write a pre-compiled image of the Control Pi (contact dev. team)
2.  **Prepare the Raspbian image to operate as an access point in a standalone network (NAT), as done [here](https://github.com/pd3d/magneto/blob/locar/Builds/LOCAR/Software/Raspberry%20Pi/Control/pinat_manual_install.md)**
