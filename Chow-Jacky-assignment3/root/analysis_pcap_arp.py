import dpkt
import binascii
import socket

#f = open("assignment3_my_arp.pcap", "rb")
#pcap = dpkt.pcap.Reader(f)

# Prompt the user to enter the pcap file
while True:
    try:
        file = input("Enter the pcap file: ")

        f = open(file, "rb")
        pcap = dpkt.pcap.Reader(f)

        break
    except:
        print("Error Input! Make sure the code is being ran in the right file path or make sure the file is in the same folder path or enter a correct pcap file.")

# 3 lists to sotre the arp packets, arp requests and arp reply
arps = []
arps_request = []
arps_reply = []


def byte_interpreter():
    # counter for how many arp packets are in the pcap file
    arp_count = 0
    request_count = 0
    reply_count = 0
    arp_probe_count = 0

    for ts, buf in pcap:
        # if protocol is ARP
        if binascii.hexlify(buf[12:14]) == b'0806':
            arps.append(buf)
            arp_count += 1

            # decode by bytes with wireshark
            hardware = binascii.hexlify(buf[14:16])
            protocols = binascii.hexlify(buf[16:18])
            hardware_size = binascii.hexlify(buf[18:19])
            protocol_size = binascii.hexlify(buf[19:20])
            opcode = binascii.hexlify(buf[20:22])
            sender_mac_address = binascii.hexlify(buf[22:28])
            sender_ip = binascii.hexlify(buf[28:32])
            target_mac_address = binascii.hexlify(buf[32:38])
            target_ip = binascii.hexlify(buf[38:42])

            packet = arp_tostring(hardware, protocols,
                                  hardware_size, protocol_size, opcode, sender_mac_address, sender_ip, target_mac_address, target_ip)

            # Filtering probe packets
            if sender_ip != b'00000000':

                # placing the request and reply packets to the corresponding list.
                if (opcode == b'0001'):
                    arps_request.append(packet)
                    request_count += 1
                elif (opcode == b'0002'):
                    arps_reply.append(packet)
                    reply_count += 1
            if sender_ip == b'00000000':
                arp_probe_count += 1

    print("\nThis pcap file contains " + str(arp_count) + " ARP packets and " + str(request_count) +
          " ARP Request packets and " + str(reply_count) + " ARP Reply packets and " + str(arp_probe_count) + " ARP Probe packets.\n")
    print("Below is One ARP Exchange: \n")

    # we are only print one exhange, so we are print the first index of the coressponding list
    print(arps_request[0] + '\n')
    print(arps_reply[0])


# This function is made for converting the bytes to the correct format like string, which includes all of the header element of the arp packet.
def arp_tostring(hardware, protocols, hardware_size, protocol_size, opcode, sender_mac_address, sender_ip, target_mac_address, target_ip):
    # we want to check if the packets can possibly have different hardware or protocals, so i provided multiple.
    if hardware == b'0000':
        hardware = 'Reserved'
    elif hardware == b'0001':
        hardware = 'Ethernet'
    elif hardware == b'0002':
        hardware = 'Experimental Ethernet'

    if protocols == b'0800':
        protocols = 'IPv4'
    elif protocols == b'86DD':
        protocols = 'IPv6'

    # 0001 means its a request and 0002 its a reply
    if opcode == b'0001':
        opcode = str(int(opcode)) + ' REQUEST'
    elif opcode == b'0002':
        opcode = str(int(opcode)) + ' REPLY'

    sender_mac_address = sender_mac_address.decode("utf-8")
    # sender_mac = sender_mac[0:2] + ":" + sender_mac[2:4] + ":" + sender_mac[4:6] + \
    #    ":" + sender_mac[6:8] + ":" + \
    #    sender_mac[8:10] + ":" + sender_mac[10:12]
    sender_mac_address = '{}:{}:{}:{}:{}:{}'.format(
        sender_mac_address[0:2], sender_mac_address[2:4], sender_mac_address[4:6], sender_mac_address[6:8], sender_mac_address[8:10], sender_mac_address[10:12])

    # we want to convert them from hex form, which is why we have 16 here.
    hardware_size = str(int(hardware_size, 16))
    protocol_size = str(int(protocol_size, 16))

    sender_ip = sender_ip.decode("utf-8")
    # sender_ip = str(int(sender_ip[0:2], 16)) + \
    #    "." + str(int(sender_ip[2:4], 16)) + "." + str(int(sender_ip[4:6], 16)) + \
    #    "." + str(int(sender_ip[6:8], 16))

    # we want to convert them from hex form, which is why we have 16 here.
    sender_ip = '{}.{}.{}.{}'.format(str(int(sender_ip[0:2], 16)), str(int(
        sender_ip[2:4], 16)), str(int(sender_ip[4:6], 16)), str(int(sender_ip[6:8], 16)))

    target_mac_address = target_mac_address.decode("utf-8")
    target_mac_address = '{}:{}:{}:{}:{}:{}'.format(
        target_mac_address[0:2], target_mac_address[2:4], target_mac_address[4:6], target_mac_address[6:8], target_mac_address[8:10], target_mac_address[10:12])

    target_ip = target_ip.decode("utf-8")
    # target_ip = str(int(target_ip[0:2], 16)) + \
    #    "." + str(int(target_ip[2:4], 16)) + "." + str(int(target_ip[4:6], 16)) + \
    #    "." + str(int(target_ip[6:8], 16))

    # we want to convert them from hex form, which is why we have 16 here.
    target_ip = '{}.{}.{}.{}'.format(str(int(target_ip[0:2], 16)), str(int(
        target_ip[2:4], 16)), str(int(target_ip[4:6], 16)), str(int(target_ip[6:8], 16)))

    # final printing result
    arp_string = ("Hardware Type: " + hardware + "\nProtocol Type: " + protocols + "\nHardware size: " +
                  hardware_size + "\nProtocal Size: " + protocol_size
                  + "\nOpcode: " + opcode + "\nSender MAC address: " + sender_mac_address + "\nSender IP: " + sender_ip + "\nTarget MAC address: " + target_mac_address + "\nTarget IP: " + target_ip)

    return arp_string


if __name__ == '__main__':
    byte_interpreter()
