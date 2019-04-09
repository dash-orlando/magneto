# LOCAR Control Pi
The following information pertains to the Control Raspberry Pi of the LOCAR system

---
## Installation
The Control Pi performs two tasks:
1. Operates all Array Pis of the LOCAR system through a secure, local wireless network
2. Operates the Pi camera and NeoPixel LED Ring of the LOCAR system

To install these features onto a fresh Raspbian image, the user may:
1. **QUICK & DIRTY** Write a pre-installed image of the Control Pi _(contact dev. team for copy)_
   > **NOTE:** Pre-installed images may only performed on the same hardware and software from which the image was read/ripped/cloned
   *  We recommend using **[Win32 Disk Imager](https://sourceforge.net/projects/win32diskimager/)** for reading/writing Raspbian images

2. **RECOMMENDED** Follow standard installation guides below;
   > **NOTE:** The proper installation of the Control Pi requires the **sequential and orderly** completion of the following steps
   1. **Prepare the Raspbian image for Pi camera and NeoPixel control, as done [here](https://github.com/pd3d/magneto/tree/locar/Builds/LOCAR/Software/Raspberry%20Pi/Control/Python)**
      * The user may, alternatively, write a pre-compiled image of the Control Pi _(contact dev. team for copy)_
   2. **Prepare the Raspbian image to operate as an access point in a standalone network (NAT), as done [here](https://github.com/pd3d/magneto/blob/locar/Builds/LOCAR/Software/Raspberry%20Pi/Control/README_pinat_install.md)**
