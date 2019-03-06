# C Implementation

In order to lower hardware costs without compromising performace, a C version of **MAGNETO** and **LOCAR** were developed for the Raspberry Pi.

## Installation

0.  **Prepare Raspberry Pi**
    1.  Install latest version of Raspbian Stretch
        > **NOTE:** The following guide was tested on **2018-11-13-raspbian-stretch**
        
        > **NOTE:** Our team has not evaluated the program's performance on Raspbian Lite or other optimized variants of the Raspbian OS
    
    
1.  **Clone the _nagneto_ repo.**
    ```
    git clone https://github.com/pd3d/magneto
    ```

    > **NOTE:** Release version of **LOCAR** will be available in the _**master**_ branch. Continued development will be located in the         _**locar**_ branch.

2.  **Build magneto**
    For simplicity, our team has automated the build process using a shell script.
    
    1.  Navigate to the **C** directory
        ```
        cd .../.../magneto/Builds/LOCAR/Software/Raspberry Pi/C
        ```
    2.  Run _build.sh_
        ```
        sudo build.sh
        ```
        
