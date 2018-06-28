"""
protocolDefinitions.py

The following module consists of a list of commands or definitions to be used in the communication between devices and the control system

Michael Xynidis
Fluvio L Lobo Fenoglietto
11/10/2017
"""


### ASCII Byte Codes -- used for communication protocol
## General Commands
ENQ				= chr(0x05)       # Enquiry: "Are you ready for commands?"										[resp: ACK | NAK]
ACK             = chr(0x06)       # Positive Acknowledgement: "Command/Action successful."						[resp: ACK | NAK]
NAK             = chr(0x15)       # Negative Acknowledgement: "Command/Action UNsuccessful."					[resp: ACK | NAK]

### Device Control Commands
## Diagnostic Functions ============================================================================================================= //
DEVICEID       	= chr(0x11)       # Device Identification                                    					[resp: Device Code]
SDCHECK         = chr(0x12)       # System Check: "Run system check and report"              					[resp: ACK | NAK]
SENDWAV         = chr(0x13)       # Send .WAV file (audio recording) via serial port         					[resp: ACK | NAK]
DELVOLATILE     = chr(0x14)       # Erase volatile files (all)                               					[resp: ACK | NAK]

## Device-Specific Functions ======================================================================================================== //                     
STARTREC        = chr(0x16)       # Start Recording                                          				[resp: ACK | NAK]
STARTCREC       = chr(0x32)       # Start Custom Recording                                                              [resp: ACK | NAK]         
STOPREC         = chr(0x17)       # Stop Recording                                           				[resp: ACK | NAK]
STARTPLAY       = chr(0x18)       # Start Playback                                           				[resp: ACK | NAK]
STOPPLAY        = chr(0x19)       # Stop Playback                                            				[resp: ACK | NAK]
STARTPASSTHRU   = chr(0x1A)       # Start Audio passthrough from mic to ear monitors         				[resp: ACK | NAK]
STARTHBMONITOR  = chr(0x1B)       # Start Monitoring Heart Beat                              				[resp: ACK | NAK]
STOPHBMONITOR   = chr(0x1C)       # Stop Monitoring Heart Beat                               				[resp: ACK | NAK]
STARTBLEND      = chr(0x1F)       # Start Blending
STOPBLEND       = chr(0x20)       # Stop Blending
PSTRING         = chr(0x31)       # Parse String

## Simulation Functions ============================================================================================================= // 
NHBSYN          = chr(0x1D)       # Playback of Synthetic, Normal Heart Beat                           			[resp: ACK | NAK]
ESMSYN          = chr(0x1E)       # Playback of Synthetic, Early Systolic Heart Murmur                 			[resp: ACK | NAK]
NHBREC          = chr(0x21)       # Blend Normal Heart Beat Recorded                                   			[resp: ACK | NAK]
EHBREC          = chr(0x22)       # Blend Exercised Heart Beat Recorded                                			[resp: ACK | NAK]
STARTBPNORM     = chr(0x26)       # Start BP Cuff augmentation -- Normal heartrate                     			[resp: ACK | NAK]
STARTBPBRADY    = chr(0x27)       # Start BP Cuff augmentation -- Bradycardia                          			[resp: ACK | NAK]
STARTBPTACHY    = chr(0x28)       # Start BP Cuff augmentation -- Tachycardia                          			[resp: ACK | NAK]
STOPBPALL       = chr(0x29)       # Stop BP Cuff augmentation                                          			[resp: ACK | NAK]
KOROT           = chr(0x30)       # Playback of Korotkoff Sound                                        			[resp: ACK | NAK] 
