import sys
import serial
import serial.tools.list_ports
from pymavlink.mavutil import x25crc

PACKET_LENGTH = 1
PACKET_SEQ_LOC = 2
K1_LOC_BYTE1 = 22
SL1_LOC_BYTE1 = 24
S1_LOC_BYTE1 = 26
S2_LOC_BYTE1 = 28

initpacket = b'\xFE\x03\x00\x01\x00\x00\x00\x01\x02\x00\x01\x00\x00'
commandmsg = b'\xFE\x1A\x00\x01\x00\x02\x00\x01\x9D\x0A\xE6\xFF\xFD\xFF\x97\x25\x1F\x00\x01\x00\x00\x00\x02\x08\x56\x0D\x00\x08\xAB\x02\x88\x08\xF4\x01\x00\x00'

k1_command = bytearray(b'\x00\x08')
sl1_command = bytearray(b'\x00\x08')
s1_command = bytearray(b'\x00\x08')
s2_command = bytearray(b'\x00\x08')

def updatemsg(msg: bytearray) -> bytearray:
    # Update packet sequence
    msg[PACKET_SEQ_LOC] = updatemsg.packet_seq

    if (msg[PACKET_LENGTH] == 0x1A):
        msg[K1_LOC_BYTE1] = k1_command[0]
        msg[K1_LOC_BYTE1+1] = k1_command[1]
        msg[SL1_LOC_BYTE1] = sl1_command[0]
        msg[SL1_LOC_BYTE1+1] = sl1_command[1]
        msg[S1_LOC_BYTE1] = s1_command[0]
        msg[S1_LOC_BYTE1+1] = s1_command[1]
        msg[S2_LOC_BYTE1] = s2_command[0]
        msg[S2_LOC_BYTE1+1] = s2_command[1]
    
    # crc_init(&tempchecksum); // done by x25crc
    #length from packet + 10 header bytes - CRC
    # for (uint8_t j=1;j<msg[1]+8;j=j+1) {
    #     crc_accumulate(msg[j],&tempchecksum);
    # }
    crc = x25crc(msg)

    # Add the CRC_EXTRA Byte which seems to be 0
    #crc_accumulate(0,&tempchecksum);
    crc.accumulate(b'\x00')
    
    # Append the checksum to the message
    # little endian: MSB is at end of byte array (PACKET_LENGTH+9)
    # C code:
        #msg[msg[1]+8]=tempchecksum & 0x00FF;
        #msg[msg[1]+9]=((tempchecksum >> 8)&0x00FF);
    crc_bytearray = bytearray(crc.crc.to_bytes(2, byteorder='little', signed=False))
    msg += crc_bytearray

    # Increment packet sequence
    if (updatemsg.packet_seq == 255):
        updatemsg.packet_seq = 0
    else:
        updatemsg.packet_seq = updatemsg.packet_seq + 1
    
    # Return the changed packet
    return msg
updatemsg.packet_seq = 0 # initialization

def send_command():
    send_command.commandmsg_buf = updatemsg(send_command.commandmsg_buf)
    cgo3_serial.write(send_command.commandmsg_buf)
send_command.commandmsg_buf = bytearray(commandmsg) # initialization

def init_gimbal():
    cgo3_serial.reset_input_buffer()

    # Send 5 init packets, until data is received back
    initpacket_array = bytearray(initpacket)
    while (cgo3_serial.in_waiting < 15):
        for i in range(5):
            initpacket_array = updatemsg(initpacket_array)
            print('.')
            cgo3_serial.write(initpacket_array)




###### MAIN PROGRAM ######

# Get arguments
if len(sys.argv) != 2:
    print("Usage: cgo3-python.py <serial port>")
    exit(1)

# Setup serial port
cgo3_serial = serial.Serial(sys.argv[1], baudrate=115200)

init_gimbal()

# Read from console/stdin and send to port
while (True):
    command = input("Enter a command {c(enter),u(p),d(own), m(iddle),r(ight),l(eft), a/v (tilt mode),f/g (pan mode)}:")
    command_char = command[0]
    if command_char == 'c':
        sl1_command[0] = 0x02
        sl1_command[1] = 0x08
    elif command_char == 'u':
        sl1_command[0] = 0xAB
        sl1_command[1] = 0x02
    elif command_char == 'd':
        sl1_command[0] = 0x56
        sl1_command[1] = 0x0d
    elif command_char == 'm':
        k1_command[0] = 0x02
        k1_command[1] = 0x08
    elif command_char == 'r':
        k1_command[0] = 0xAB
        k1_command[1] = 0x02
    elif command_char == 'l':
        k1_command[0] = 0x56
        k1_command[1] = 0x0d
    elif command_char == 'a':
        s1_command[0] = 0xAB
        s1_command[1] = 0x02
    elif command_char == 'v':
        s1_command[0] = 0x54
        s1_command[1] = 0x0D
    elif command_char == 'f':
        s2_command[0] = 0xAB
        s2_command[1] = 0x02
    elif command_char == 'g':
        s2_command[0] = 0x54
        s2_command[1] = 0x0D
    elif command_char == 'i':
        init_gimbal()
        continue
    else:
        print("Invalid command.")
        continue

    send_command()
