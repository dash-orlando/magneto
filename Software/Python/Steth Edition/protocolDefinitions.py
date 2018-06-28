"""
protocolDefinitions.py

The following module consists of a list of commands or definitions to be used in the communication between devices and the control system

Michael Xynidis
Fluvio L Lobo Fenoglietto
09/26/2016
"""
# Definition                            Name                                                Value           Class
# ----------                            ----                                                -----           -----
SOH = chr(0x01)					#		Start of Heading									0x01			STD
ENQ = chr(0x05)                 #       Enquiry                                             0x05            STD
EOT = chr(0x04)                 #       End of Transmission                                 0x04            STD
ACK = chr(0x06)                 #       Positive Acknowledgement                            0x06            STD
NAK = chr(0x15)                 #       Negative Acknowledgement                            0x15            STD
CAN = chr(0x18)                 #       Cancel Current Command                              0x18            STD

# Device Control Commands
#   We have extended the four (4) standard "device control" commands by means of a two-byte communication protocol

DC1 = chr(0x11)                 #       Device Control 1: Diagnostic Functions              0x11            STD
DC1_DEVICEID = chr(0x00)        #           Device Identification
DC1_SDCHECK = chr(0x01)         #           SD Card Check                                   0x00            ORG
#                                                                                           0xFF            ORG

DC2 = chr(0x12)                 #       Device Control 2: Operational Functions             0x12            STD
DC2_SENDWAV = chr(0x00)         #           Send .WAV File                                  0x00            ORG
DC2_DELVOLATILE = chr(0x01)     #           Delete Volatile Files                           0x01            ORG
#                                                                                           0xFF            ORG

DC3 = chr(0x13)                 #       Device Control 3: Device-Specific Functions         0x13            STD
DC3_STARTREC = chr(0x00)        #           Start Recording                                 0x00            ORG
DC3_STOPREC = chr(0x01)         #           Stop Recording                                  0x01            ORG
DC3_STARTPLAY = chr(0x02)       #           Start Playback                                  0x02            ORG
DC3_STOPPLAY = chr(0x03)        #           Stop Playback                                   0x03            ORG
DC3_STARTSTREAM = chr(0x04)     #           Start Microphone Stream                         0x04            ORG
DC3_STARTTRACKING = chr(0x05)   #           Start Tracking Microphone Stream for Peaks      0x05            ORG
DC3_STOPTRACKING = chr(0x06)    #           Stop Tracking Microphone Stream for Peaks       0x06            ORG
#                                                                                           0xFF            ORG

DC4 = chr(0x14)                 #       Device Control 4: Simulation Functions              0x14            STD
DC4_NORMALHB = chr(0x00)        #           Playback of Normal Heart Beat                   0x00            ORG
DC4_ESHMURMUR = chr(0x01)       #           Playback of Early Systolic Heart Beat           0x01            ORG
#                                                                                           0xFF            ORG

# Legend
# STD - Standard terminology / Standard reference for command
# ORG - Original or custom-made command and reference
