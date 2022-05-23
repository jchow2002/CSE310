# Jacky Chow 113268425 Programming assignment 2 Submission 2 03-11-2022
# The explanation/summary will explain most of the code operation/process.
import dpkt
import dpkt.pcap
import dpkt.ethernet
import dpkt.ip
import dpkt.tcp
import dpkt.http
import socket
import datetime

# Prompt the user to enter the pcap file
while True:
    try:
        file = input("Enter the pcap file: ")
        f = open(file, "rb")
        break
    except:
        print("Error Input! Make sure the file is in the same folder path or enter a correct pcap file.")


SOURCE_IP = '130.245.145.12'
DEST_IP = '128.208.2.198'

pcap = dpkt.pcap.Reader(f)

# list of all the source ports except 80
sportlist = []
for a, (timestamp, buf) in enumerate(pcap):
    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    tcp = ip.data

    if tcp.sport != 80:
        if tcp.sport not in sportlist:
            sportlist.append(tcp.sport)

# creating an empter list for the byte result list
resultbytelist = []
for i in sportlist:
    resultbytelist.append(0)

# analysis function


def pcapanalysis(file):
    f = open(file, "rb")
    pcap = dpkt.pcap.Reader(f)
    count = 1
    port_dict = {}
    port_dict[80] = []
    ip_dict = {}
    sip = [-1]
    rip = [-1]
    SYNtimes = [-1]
    port_dict2 = {}
    timelasted = {}
    SYNACKtimes = [-1]

    # iterating through the pcap file
    for a, (timestamp, buf) in enumerate(pcap):
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data
        tcp = ip.data

        # avoiding non TCP/HTTP packets
        if eth.type != dpkt.ethernet.ETH_TYPE_IP or ip.p != dpkt.ip.IP_PROTO_TCP:
            continue

        # adding all the bytes to the respective source ports.
        i = 0
        j = 0
        for i in sportlist:
            if(tcp.sport == sportlist[j] and not ((tcp.flags & dpkt.tcp.TH_FIN)) and not ((tcp.flags & dpkt.tcp.TH_SYN))):
                resultbytelist[j] = resultbytelist[j] + len(tcp)
            j += 1

        # This is the SYN packet, adding the keys(ports) for dictionary, and getting their ip and timestamp.
        if (tcp.flags & dpkt.tcp.TH_SYN) and not (tcp.flags & dpkt.tcp.TH_ACK):
            port_dict[tcp.sport] = []
            port_dict2[tcp.sport] = []
            timelasted[tcp.sport] = timestamp
            ip_dict[socket.inet_ntoa(ip.src)] = []
            sip.append(socket.inet_ntoa(ip.src))
            rip.append(socket.inet_ntoa(ip.dst))

            # timestamps for SYN packets
            SYNtimes.append(timestamp)

        # timestamps for SYN/ACK packets
        if (tcp.flags & dpkt.tcp.TH_SYN) and (tcp.flags & dpkt.tcp.TH_ACK):
            SYNACKtimes.append(timestamp)

        # Subtract the time from the SYN to FIN for part A) c.
        if tcp.flags & dpkt.tcp.TH_FIN and tcp.sport in sportlist:
            timelasted[tcp.sport] = timestamp - timelasted[tcp.sport]

        if tcp.sport in port_dict2.keys() and (not (tcp.flags & dpkt.tcp.TH_SYN) or not (tcp.flags & dpkt.tcp.TH_ACK)):
            port_dict2[tcp.sport].append(tcp)

        if tcp.sport in port_dict.keys():
            port_dict[tcp.sport].append((timestamp, ip))

    # Adding the RTTs into the RTTlist
    RTTlist = []
    o = 1
    for o in range(len(SYNACKtimes)):
        RTTlist.append(SYNACKtimes[o] - SYNtimes[o])
    RTTlist.remove(0)
    print(RTTlist)

    # for h, key in enumerate(port_dict):
    # if key != 80:
    # print(timestamp)

    # Transfering the result into this new list.
    timelist = []
    for i in timelasted:
        timelist.append(timelasted[i])

    # Print total num of flows
    print('----------------------------------------------------------------------------------------------------------------------------------')
    print("Total number of flows: " + str(len(port_dict) - 1))

    # Iterating through the dictionary.
    d = 1
    g = 0
    for i, key in enumerate(port_dict):

        # Printing flows info
        if key != 80:
            print(
                '----------------------------------------------------------------------------------------------------------------------------------')
            print("Flow number: " + str(d))
            print("Source port: " + str(key) + " Destination port: " + str(tcp.dport) + " Sender IP: " + str(sip[d]) +
                  " Receiver IP: " + str(rip[d]) + ' Timestamp: ' + str(datetime.datetime.utcfromtimestamp(SYNtimes[d])))
            count = count + 1

            print("Transaction: " + '1')
            print("Source ip: " + socket.inet_ntoa(port_dict[key][2][1].src) + " Destination ip: " + socket.inet_ntoa(port_dict[key][2][1].dst) + "\nSequence number: " + str(port_dict[key][2][1].data.seq) +
                  " Ack number: " + str(port_dict[key][2][1].data.ack) + " Window Size: " + str(
                      port_dict[key][2][1].data.win))
            # Loop to find the coresponding recieving packet and add the ack number to a list to avoid this packet again in transcation 2.
            tempcount = 0
            templist = []
            for (ts, ip) in port_dict[80]:
                tempcount += 1
                if ip.data.seq == port_dict[key][2][1].data.ack and key == ip.data.dport:
                    new = ip
                    templist.append(ip.data.ack)
                    break

            print("Source ip: " + socket.inet_ntoa(new.src) + " Destination ip: " + socket.inet_ntoa(new.dst) + "\nSequence number: " + str(new.data.seq) +
                  " Ack number: " + str(new.data.ack) + " Window Size: " + str(new.data.win))

            print("Transaction: " + '2')
            # print("sip: " + inet_to_str(ip.src) +
            # " dip: " + inet_to_str(ip.dst))
            print("Source ip: " + socket.inet_ntoa(port_dict[key][3][1].src) + " Destination ip: " + socket.inet_ntoa(port_dict[key][3][1].dst) + "\nSequence number: " + str(port_dict[key][3][1].data.seq) +
                  " Ack number: " + str(port_dict[key][3][1].data.ack) + " Window Size: " + str(
                      port_dict[key][1][1].data.win))
            # print("!!!" + str(port_dict[80][2][1].data.ack))
            # print("!!!" + str(port_dict[80][3][1].data.ack))

            # Loop to find the coresponding recieving packet and using the list created from the previous comment mentioned.
            for (ts, ip2) in port_dict[80]:
                if ip2.data.seq == port_dict[key][3][1].data.ack and key == ip2.data.dport:
                    if ip2.data.ack in templist:
                        continue
                    new2 = ip2
                    break

            # print("sip: " + inet_to_str(ip2.src) +
                  # " dip: " + inet_to_str(ip2.dst))
            print("Source ip: " + socket.inet_ntoa(new2.src) + " Destination ip: " + socket.inet_ntoa(new2.dst) + "\nSequence number: " + str(new2.data.seq) +
                  " Ack number: " + str(new2.data.ack) + " Window Size: " + str(new2.data.win))

            print("Total bytes sent: " + str(resultbytelist[g]) + " bytes")

            # Sender throughtput is the total amount of bytes divided by the time.
            print("Sender throughput: " +
                  str(resultbytelist[g] / timelist[g]) + " bytes per second")

            # Part B, will or will not be updated at a later submission during grace period.
            print('\n')

            # Unable to get congestion window size, printed RTTs.
            print("RTT for the flow: " + str(RTTlist[g]))
            print("Congestion Window Sizes: []")
            # [14, 20, 41]
            # [12, 22, 33]
            # [20, 42, 41]
            print("Total number of retransmission: ")
            print("Retransmission due to triple dup ack: ")
            print("Retransmission due to Timeout: ")

            g += 1
            d += 1


pcapanalysis(file)
