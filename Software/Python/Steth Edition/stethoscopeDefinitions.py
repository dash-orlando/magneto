"""
protocolDefinitions.py

The following module consists of a list of commands or definitions to be used in the communication between devices and the control system

Michael Xynidis
Fluvio L Lobo Fenoglietto
11/10/2017
"""


### ASCII Byte Codes -- used for communication protocol
## General Commands
ENQ		= chr(0x05)       # Enquiry: "Are you ready for commands?"										[resp: ACK | NAK]
ACK             = chr(0x06)       # Positive Acknowledgement: "Command/Action successful."						[resp: ACK | NAK]
NAK             = chr(0x15)       # Negative Acknowledgement: "Command/Action UNsuccessful."					[resp: ACK | NAK]

### Device Control Commands
## Diagnostic Functions ============================================================================================================= //
DEVICEID       	= chr(0x11)       # Device Identification                                    					[resp: Device Code]
SDCHECK         = chr(0x12)       # System Check: "Run system check and report"              					[resp: ACK | NAK]
SENDWAV         = chr(0x13)       # Send .WAV file (audio recording) via serial port         					[resp: ACK | NAK]
DELVOLATILE     = chr(0x14)       # Erase volatile files (all)                               					[resp: ACK | NAK]
SENDRAW         = chr(0x37)       # send raw file...

## Device-Specific Functions ======================================================================================================== //                     
STARTREC        = chr(0x16)       # Start Recording                                          				[resp: ACK | NAK]
STARTCREC       = chr(0x32)       # Start Custom Recording                                                              [resp: ACK | NAK]         
STARTMREC       = chr(0x38)
STOPREC         = chr(0x17)       # Stop Recording                                           				[resp: ACK | NAK]
STARTPLAY       = chr(0x18)       # Start Playback                                           				[resp: ACK | NAK]
STOPPLAY        = chr(0x19)       # Stop Playback                                            				[resp: ACK | NAK]
STARTHBMONITOR  = chr(0x1B)       # Start Monitoring Heart Beat                              				[resp: ACK | NAK]
STOPHBMONITOR   = chr(0x1C)       # Stop Monitoring Heart Beat                               				[resp: ACK | NAK]
STARTBLEND      = chr(0x1F)       # Start Blending
STOPBLEND       = chr(0x20)       # Stop Blending
PSTRING         = chr(0x31)       # Parse String
RECMODE         = chr(0x41)       # Parse recording mode
SETIDLE         = chr(0x26)       # set to idle

## Simulation Functions ============================================================================================================= // 
STARTSIM        = chr(0x70)       # simulation byte
STOPSIM         = chr(0x71)       # simulation byte

## Blending Audio Files and Reference Bytes ========================================================================================= //
### Blending Files
n_blend_files       = 16
blendFiles          = (["AORSTE",
                        "S4GALL",
                        "ESMSYN",
                        "KOROT1",
                        "KOROT2",
                        "KOROT3",
                        "KOROT4",
                        "RECAOR",
                        "RECMIT",
                        "RECPUL",
                        "RECTRI",
                        "BRONCH",
                        "DEARAT",
                        "POLWHE",
                        "STRIDO",
                        "WHEEZI"])

### Associated Bytes (self-assembling)
n_blend_bytes       = n_blend_files
blend_byte_offset   = 60
blendInt            = []
blendByte           = []
for i in range( 0, n_blend_bytes ):
    blendInt.append(  blend_byte_offset + i )
    blendByte.append( chr( blend_byte_offset + i ) )

### Associated Matching Function
def blendByteMatching( blendFileName, blendFiles ):
    matchIndex = -1
    n_blend_files = len( blendFiles )
    for i in range( 0, n_blend_files ):
        if blendFiles[i] == blendFileName:
            matchIndex = i
    return matchIndex
