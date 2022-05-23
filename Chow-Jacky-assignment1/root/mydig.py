# Jacky chow 113268425
# Programming assignment 1
import dns.message
import dns.query
from datetime import datetime
import time

today = datetime.now()
datestring = today.strftime("%m/%d/%Y %H:%M:%S")
root_server = '198.41.0.4'
domain = input('Enter your domain: ')
start_time = time.time()
request = dns.message.make_query(domain, 1)
root_server_list = ['198.41.0.4', '199.9.14.201', '192.33.4.12', '199.7.91.13', '192.203.230.10', '192.5.5.241',
                    '192.112.36.4', '198.97.190.53', '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42', '202.12.27.33']

check = False
i = 0
while not check:
    # This part is for the inital reponse, and it will be using a list of root servers, if one does not work it will go to the next one.
    try:
        response = dns.query.udp(request, root_server_list[i], timeout=5)
        additional = []
        for i in range(0, len(response.sections[3])):
            item = str(response.sections[3][i].__getitem__(0))
            if item.find(":") == -1:
                additional.append(item)
                i += 1
        check = True
    except:
        print('Trying next')
        i = i + 1
        if(i > len(root_server_list) - 1):
            print("Error")
            raise RuntimeError("No working root server")
        continue


def solver():
    # This checks for the reponses that returns no addtional and no answer. In this case we will be changing the domain to one of the name server and proceed from there.
    special_response = dns.query.udp(request, additional[0])

    if (len(special_response.sections[1]) == 0 and len(special_response.sections[3]) == 0):
        new_domain = str(special_response.sections[2][0].__getitem__(0))

        new_request = dns.message.make_query(new_domain, 1)
        new_response = dns.query.udp(new_request, root_server)

        new_additional = []
        # creating a list of name server ips
        for i in range(0, len(new_response.sections[3])):
            item = str(new_response.sections[3][i].__getitem__(0))
            if item.find(":") == -1:
                new_additional.append(item)
                i += 1

        new_notfound = False
        count = 0
        while not new_notfound:
            try:
                final_response = dns.query.udp(
                    new_request, new_additional[count])
                new_additional.clear()

                # if(len(final_response.sections[1]) == 0 and len(final_response.sections[2]) != 0 and len(final_response.sections[3]) == 0):
                # return
                if (len(final_response.sections[1]) == 0):
                    for i in range(0, len(final_response.sections[3])):
                        item = str(
                            final_response.sections[3][i].__getitem__(0))
                        if item.find(":") == -1:
                            new_additional.append(item)
                            i += 1
                # Returns the reponse (Special case: no additional + no asnwer after first query.)
                elif (len(final_response.sections[1]) != 0):
                    print('QUESTION SECTION:')
                    print(domain + ". In A" + '\n')
                    print('ANSWER SECTION:')
                    print(str(final_response.sections[1][0]) + '\n')
                    print(
                        'Query time: ' + str((time.time() - start_time) * 1000) + 'ms')
                    print('WHEN: ' + datestring)
                    new_notfound = True

            except:
                if count < len(new_additional):
                    # Increment if the first server on the list isnt working, then try the following ip on the list.
                    count += 1
                else:
                    print(
                        "Error")
                    break

                continue
        return

    found = False
    count = 0
    while not found:
        # This part if for the regular query such as google.com where there is no special response case and CNAME.
        try:
            response1 = dns.query.udp(request, additional[count])
            additional.clear()

            if (len(response1.sections[1]) == 0):
                for i in range(0, len(response1.sections[3])):
                    item = str(response1.sections[3][i].__getitem__(0))
                    if item.find(":") == -1:
                        additional.append(item)
                        i += 1
            # This part is when the answer section returns a CNAME, and it will replace the domain name as a CNAME, and it will proceed from there.
            elif ('CNAME' in str(response1.sections[1])) and (len(response1.sections[1]) != 0):
                cname = str(response1.sections[1][0].__getitem__(0))
                crootserver = '198.41.0.4'
                crequest = dns.message.make_query(cname, 1)
                cresponse = dns.query.udp(crequest, crootserver)

                cadditional = []
                # creating a list of cname server ips
                for i in range(0, len(cresponse.sections[3])):
                    item = str(cresponse.sections[3][i].__getitem__(0))
                    if item.find(":") == -1:
                        cadditional.append(item)
                        i += 1
                cfound = False
                while not cfound:
                    try:
                     # This part is when the answer section returns a CNAME and then CANME returns a special case mentioned before, where there is no asnwer and additonal ips.
                     # It will replace the CNAME with the name server, and it will proceed from there.

                        cresponse = dns.query.udp(crequest, cadditional[0])
                        cadditional.clear()

                        if(len(cresponse.sections[1]) == 0 and len(cresponse.sections[2]) != 0 and len(cresponse.sections[3]) == 0):
                            NSdoamin = str(
                                cresponse.sections[2][0].__getitem__(0))
                            NSrequest = dns.message.make_query(NSdoamin, 1)
                            NSresponse = dns.query.udp(NSrequest, crootserver)
                            NSadditional = []
                            # creating a list of cname server ips
                            for i in range(0, len(NSresponse.sections[3])):
                                item = str(
                                    NSresponse.sections[3][i].__getitem__(0))
                                if item.find(":") == -1:
                                    NSadditional.append(item)
                                    i += 1

                            NSfound = False
                            while not NSfound:
                                NSresponse = dns.query.udp(
                                    NSrequest, NSadditional[count])
                                NSadditional.clear()
                                if (len(NSresponse.sections[1]) == 0):
                                    for i in range(0, len(NSresponse.sections[3])):
                                        item = str(
                                            NSresponse.sections[3][i].__getitem__(0))
                                        if item.find(":") == -1:
                                            NSadditional.append(item)
                                            i += 1
                                    continue
                                # Returns the reponse of the CNAME special case.
                                elif len(NSresponse.sections[1]) != 0:
                                    print('QUESTION SECTION:')
                                    print(domain + ". In A" + '\n')
                                    print('ANSWER SECTION:')
                                    print(
                                        str(NSresponse.sections[1][0]) + '\n')
                                    print(
                                        'Query time: ' + str((time.time() - start_time) * 1000) + 'ms')
                                    print('WHEN: ' + datestring)
                                    cfound = True
                                    NSfound = True
                                    found = True

                            return

                        elif (len(cresponse.sections[1]) == 0):
                            for i in range(0, len(cresponse.sections[3])):
                                item = str(
                                    cresponse.sections[3][i].__getitem__(0))
                                if item.find(":") == -1:
                                    cadditional.append(item)
                                    i += 1
                            continue

                        if(len(cresponse.sections[1]) != 0):
                            if 'CNAME' in str(cresponse.sections[1]):

                                cname2 = str(
                                    cresponse.sections[1][0].__getitem__(0))
                                crequest2 = dns.message.make_query(cname2, 1)
                                cresponse2 = dns.query.udp(
                                    crequest2, root_server)

                                cadditional2 = []
                                # creating a list of name server ips
                                for i in range(0, len(cresponse2.sections[3])):
                                    item = str(
                                        cresponse2.sections[3][i].__getitem__(0))
                                    if item.find(":") == -1:
                                        cadditional2.append(item)
                                        i += 1

                                cnotfound2 = False
                                count = 0
                                while not cnotfound2:
                                    try:
                                        cresponse2 = dns.query.udp(
                                            crequest2, cadditional2[count])
                                        cadditional2.clear()
                                        if(len(cresponse2.sections[1]) == 0 and len(cresponse2.sections[2]) != 0 and len(cresponse2.sections[3]) == 0):
                                            # This part is when the answer section returns a CNAME  and then returns another CNAME and then the second CANME returns a special case mentioned before, where there is no asnwer and additonal ips.
                                            # It will replace the CNAME with the name server, and it will proceed from there.
                                            NSdoamin2 = str(
                                                cresponse2.sections[2][0].__getitem__(0))
                                            NSrequest2 = dns.message.make_query(
                                                NSdoamin2, 1)
                                            NSresponse2 = dns.query.udp(
                                                NSrequest2, crootserver)
                                            NSadditional2 = []
                                            # creating a list of cname server ips
                                            for i in range(0, len(NSresponse2.sections[3])):
                                                item = str(
                                                    NSresponse2.sections[3][i].__getitem__(0))
                                                if item.find(":") == -1:
                                                    NSadditional2.append(item)
                                                    i += 1

                                            NSfound2 = False
                                            while not NSfound2:
                                                NSresponse2 = dns.query.udp(
                                                    NSrequest2, NSadditional2[count])
                                                NSadditional2.clear()
                                                if (len(NSresponse2.sections[1]) == 0):
                                                    for i in range(0, len(NSresponse2.sections[3])):
                                                        item = str(
                                                            NSresponse2.sections[3][i].__getitem__(0))
                                                        if item.find(":") == -1:
                                                            NSadditional2.append(
                                                                item)
                                                            i += 1
                                                    continue

                                                elif len(NSresponse2.sections[1]) != 0:
                                                    print('QUESTION SECTION:')
                                                    print(
                                                        domain + ". In A" + '\n')
                                                    print('ANSWER SECTION:')
                                                    print(
                                                        str(NSresponse2.sections[1][0]) + '\n')
                                                    print(
                                                        'Query time: ' + str((time.time() - start_time) * 1000) + 'ms')
                                                    print(
                                                        'WHEN: ' + datestring)
                                                    cfound = True
                                                    NSfound2 = False
                                                    found = True
                                                return

                                        elif (len(cresponse2.sections[1]) == 0):
                                            # This part is when the answer section returns a CNAME  and then returns another CNAME.
                                            # It will replace the CNAME with the new CNAME, and it will proceed from there. (Example: www.instagram.com)
                                            for i in range(0, len(cresponse2.sections[3])):
                                                item = str(
                                                    cresponse2.sections[3][i].__getitem__(0))
                                                if item.find(":") == -1:
                                                    cadditional2.append(item)
                                                    i += 1
                                        elif (len(cresponse2.sections[1]) != 0):
                                            print('QUESTION SECTION:')
                                            print(domain + ". In A" + '\n')
                                            print('ANSWER SECTION:')
                                            print(
                                                str(cresponse2.sections[1][0]) + '\n')
                                            print(
                                                'Query time: ' + str((time.time() - start_time) * 1000) + 'ms')
                                            print('WHEN: ' + datestring)
                                            cnotfound2 = True
                                        cfound = True
                                        found = True
                                    except:
                                        if count < len(additional):
                                            # Increment if the first server on the list isnt working, then try the following ip on the list.
                                            count += 1
                                        else:
                                            print("Error")
                                            break
                                        continue

                            else:
                                print('QUESTION SECTION:')
                                print(domain + ". In A" + '\n')
                                print('ANSWER SECTION:')
                                print(str(cresponse.sections[1][0]) + '\n')
                                print(
                                    'Query time: ' + str((time.time() - start_time) * 1000) + 'ms')
                                print('WHEN: ' + datestring)
                                cfound = True
                                found = True
                    except:
                        if count < len(cadditional):
                            # Increment if the first server on the list isnt working, then try the following ip on the list.
                            count += 1
                        else:
                            print("Error")
                            break
                        continue

            # Returns the reponse (Regular case)
            elif (len(response1.sections[1]) != 0):
                print('QUESTION SECTION:')
                print(domain + ". In A" + '\n')
                print('ANSWER SECTION:')
                print(str(response1.sections[1][0]) + '\n')
                print('Query time: ' + str((time.time() - start_time) * 1000) + 'ms')
                print('WHEN: ' + datestring)
                found = True

        except:
            if count < len(additional):
                # Increment if the first server on the list isnt working, then try the following ip on the list.
                count += 1
            else:
                print("Error")
                break
            continue


# if SOA meaing that there is an error report, then we throw/print error.
if 'SOA' in str(response.sections[2]):
    print('Error')
else:
    solver()
