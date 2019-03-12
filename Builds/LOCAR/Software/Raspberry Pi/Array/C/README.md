# C Implementation

In order to lower hardware costs without compromising performace, a C version of **MAGNETO** and **LOCAR** were developed for the Raspberry Pi.

## Installation

0.  **Prepare Raspberry Pi**
    1.  Install latest version of Raspbian Stretch
        > **NOTE:** The following guide was tested on **2018-11-13-raspbian-stretch**
        
        > **NOTE:** Our team has not evaluated the program's performance on Raspbian Lite or other optimized variants of the Raspbian OS
        
    2.  Eanble I2C Communication
        1.  ```Applications Menu (Start) > Preferences > Raspberry Pi Configuration```
        2.  Under the **Interfaces** tab, check the **enable** button next to **I2C**
    
1.  **Clone the _nagneto_ repo.**
    ```
    git clone https://github.com/pd3d/magneto
    ```

    > **NOTE:** Release version of **LOCAR** will be available in the _**master**_ branch. Continued development will be located in the         _**locar**_ branch.

2.  **Build magneto**
    For simplicity, our team has automated the build process using a shell script.
    
    1.  Navigate to the **C** directory
        ```
        cd .../.../magneto/Builds/LOCAR/Software/Raspberry Pi/C/
        ```
    2.  Run _build.sh_
        ```
        sudo sh build.sh
        ```
        After the build process has terminated successfully, **magneto** and **LOCAR** will be ready to run!
        
        > **NOTE:** More information and troubleshooting can be found in the **Building magneto, extended** section below

## Execution
1.  Navigate to the **C** directory
    ```
    cd .../.../magneto/Builds/LOCAR/Software/Raspberry Pi/C/
    ```
2.  Execute _**magneto**_
    ```
    ./magneto
    ```

---
### Troubleshooting

*   **ERROR:** When executing _**magneto**_ :: `Unable to open I2C device: No such file or directory`
    *   **PROBLEM:** I2C interface has not been enabled on the Pi
    *   **SOLUTION:** Enable the I2C interface
    
### Building magneto, extended...

