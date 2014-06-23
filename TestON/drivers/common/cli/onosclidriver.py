#!/usr/bin/env python
'''
Created on 31-May-2013

@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)

TestON is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

TestON is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TestON. If not, see <http://www.gnu.org/licenses/>.


'''
import time
import pexpect
import struct, fcntl, os, sys, signal
import re
import json
import traceback
import urllib2
from urllib2 import URLError, HTTPError
sys.path.append("../")
from drivers.common.clidriver import CLI

class OnosCliDriver(CLI):
    
    def __init__(self):
        super(CLI, self).__init__()
        
    def connect(self,**connectargs):
        '''
        Creates ssh handle for ONOS.
        '''
        try:
            for key in connectargs:
                vars(self)[key] = connectargs[key]
            self.home = "~/ONOS"
            for key in self.options:
                if key == "home":
                    self.home = self.options['home']
                    break

            
            self.name = self.options['name']
            self.handle = super(OnosCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd, home = self.home)

            if self.handle:
                return self.handle
            else :
                main.log.info("NO ONOS HANDLE")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
        
    def start(self, env = ''):
        '''
        Starts ONOS on remote machine.
        Returns false if any errors were encountered.
        '''
        try:
            self.handle.sendline("")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("cd "+self.home)
            self.handle.sendline(env + "./onos.sh core start")
            i=self.handle.expect(["STARTED","FAILED",pexpect.EOF,pexpect.TIMEOUT])
            response = self.handle.before + str(self.handle.after)
            if i==0:
                j = self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT], timeout=60)
                if re.search("Killed",response):
                    main.log.warn(self.name + ": Killed existing process")
                if j==0:
                    main.log.info(self.name + ": ONOS Started ")
                    return main.TRUE
                elif j==1:
                    main.log.error(self.name + ": EOF exception found")
                    main.log.error(self.name + ":     " + self.handle.before)
                    main.cleanup()
                    main.exit()
                elif j==2:
                    main.log.info(self.name + ": ONOS NOT Started, stuck while waiting for it to start ")
                    return main.FALSE
                else:
                    main.log.warn(self.name +": Unexpected response in start")
                    return main.TRUE
            elif i==1:
                main.log.error(self.name + ": ONOS Failed to start")
                return main.FALSE
            elif i==2:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
            elif i==3:
                main.log.error(self.name + ": ONOS timedout while starting")
                return main.FALSE
            else:
                main.log.error(self.name + ": ONOS start  expect script missed something... ")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def start_all(self):
        '''
        starts ZK, RC, and ONOS
        '''
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh start")
        self.handle.expect("./onos.sh start")
        self.handle.expect(["\$",pexpect.TIMEOUT])



    def start_rest(self):
        '''
        Starts the rest server on ONOS.
        '''
        try:
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd= "./start-rest.sh start",prompt="\$",timeout=10)
            if re.search("admin",response):
                main.log.info(self.name + ": Rest Server Started Successfully")
                time.sleep(5)
                return main.TRUE
            else :
                main.log.warn(self.name + ": Failed to start Rest Server")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
    
    def status(self):
        '''
        Called onos.sh core status and returns TRUE/FALSE accordingly
        '''
        try:
            self.execute(cmd="\n",prompt="\$",timeout=10)
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd="./onos.sh core status ",prompt="\d+\sinstance\sof\sonos\srunning",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            if re.search("1\sinstance\sof\sonos\srunning",response):
                return main.TRUE
            elif re.search("0\sinstance\sof\sonos\srunning",response):
                return main.FALSE
            else :
                main.log.warn(self.name + " WARNING: status recieved unknown response")
                main.log.warn(response)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


    def isup(self):
        '''
        A more complete check to see if ONOS is up and running properly.
        First, it checks if the process is up.
        Second, it reads the logs for "Exception: Connection refused"
        Third, it makes sure the logs are actually moving.
        returns TRUE/FALSE accordingly.
        '''
        try:
            self.execute(cmd="\n",prompt="\$",timeout=10)
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd= "./onos.sh core status ",prompt="running",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            tail1 = self.execute(cmd="tail " + self.home + "/onos-logs/onos.*.log",prompt="\$",timeout=10)
            time.sleep(10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            tail2 = self.execute(cmd="tail " + self.home + "/onos-logs/onos.*.log",prompt="\$",timeout=10)
            pattern = '(.*)1 instance(.*)'
            pattern2 = '(.*)Exception: Connection refused(.*)'
           # if utilities.assert_matches(expect=pattern,actual=response,onpass="ONOS process is running...",onfail="ONOS process not running..."):
            running = self.execute(cmd="cat "+self.home+"/onos-logs/onos.*.log | grep 'Sending LLDP out on all ports'",prompt="\$",timeout=10) 
            if re.search(pattern, response):
                if running != "":
                    main.log.info(self.name + ": ONOS process is running...")
                    if tail1 == tail2:
                        main.log.error(self.name + ": ONOS is frozen...")#logs aren't moving
                        return main.FALSE
                    elif re.search( pattern2,tail1 ):
                        main.log.info(self.name + ": Connection Refused found in onos log")
                        return main.FALSE
                    elif re.search( pattern2,tail2 ):
                        main.log.info(self.name + ": Connection Refused found in onos log")
                        return main.FALSE
                    else:
                        main.log.info(self.name + ": Onos log is moving! It's looking good!")
                        return main.TRUE
                else:
                    main.log.info(self.name + ": ONOS not yet sending out LLDP messages")
                    return main.FALSE
            else:
                main.log.error(self.name + ": ONOS process not running...")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


        
    def rest_status(self):
        '''
        Checks if the rest server is running.
        '''
        try:
            response = self.execute(cmd= self.home + "/start-rest.sh status ",prompt="running",timeout=10)
            if re.search("rest\sserver\sis\srunning",response):
                main.log.info(self.name + ": Rest Server is running")
                return main.TRUE
            elif re.search("rest\sserver\sis\snot\srunning",response):
                main.log.warn(self.name + ": Rest Server is not Running")
                return main.FALSE
            else :
                main.log.error(self.name + ": No response" +response)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def stop_all(self):
        '''
        Runs ./onos.sh stop
        '''
        try:
            self.handle.sendline("")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("cd "+self.home)
            self.handle.sendline("./onos.sh stop")
            i=self.handle.expect(["Stop",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT], 60)
            result = self.handle.before
            if re.search("Killed", result):
                main.log.info(self.name + ": ONOS Killed Successfully")
                return main.TRUE
            else :
                main.log.warn(self.name + ": ONOS wasn't running")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
       

    def stop(self):
        '''
        Runs ./onos.sh core stop to stop ONOS
        '''
        try:
            self.handle.sendline("")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("cd "+self.home)
            self.handle.sendline("./onos.sh core stop")
            i=self.handle.expect(["Stop",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT], 60)
            result = self.handle.before
            if re.search("Killed", result):
                main.log.info(self.name + ": ONOS Killed Successfully")
                return main.TRUE
            else :
                main.log.warn(self.name + ": ONOS wasn't running")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
    
    
    def rest_stop(self):
        '''
        Runs ./start-rest.sh stop to stop ONOS rest server
        '''
        try:
            response = self.execute(cmd= self.home + "/start-rest.sh stop ",prompt="killing",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            if re.search("killing", response):
                main.log.info(self.name + ": Rest Server Stopped")
                return main.TRUE
            else :
                main.log.error(self.name + ": Failed to Stop, Rest Server is not Running")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


    def disconnect(self):
        '''
        Called when Test is complete to disconnect the ONOS handle.
        '''
        response = ''
        try:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
        except:
            main.log.error(self.name + ": Connection failed to the host")
            response = main.FALSE
        return response
 
    def print_version(self):
        '''
        Writes the COMMIT number to the report to be parsed by Jenkins data collecter.
        '''
        try:
            self.handle.sendline("export TERM=xterm-256color")
            self.handle.expect("xterm-256color")
            self.handle.expect("\$")
            self.handle.sendline("cd " + self.home + "; git log -1 --pretty=fuller | grep -A 5 \"commit\"; cd \.\.")
            self.handle.expect("cd ..")
            self.handle.expect("\$")
            response=(self.name +": \n"+ str(self.handle.before + self.handle.after))
            main.log.report(response)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
    def get_version(self):
        '''
        Writes the COMMIT number to the report to be parsed by Jenkins data collecter.
        '''
        try:
            self.handle.sendline("export TERM=xterm-256color")
            self.handle.expect("xterm-256color")
            self.handle.expect("\$")
            self.handle.sendline("cd " + self.home + "; git log -1 --pretty=fuller | grep -A 5 \"commit\"; cd \.\.")
            self.handle.expect("cd ..")
            self.handle.expect("\$")
            response=(self.name +": \n"+ str(self.handle.before + self.handle.after))
            lines=response.splitlines()
            for line in lines:
                print line
            return lines[2]
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


    def add_intent(self, intent_id,src_dpid,dst_dpid,src_mac,dst_mac,intentIP,intentPort=8080,intentURL="wm/onos/intent/high" , intent_type = 'SHORTEST_PATH', static_path=False, src_port=1,dst_port=1):
        "CLI command callback: set intent"

        intents = []
        oper = {}
        # Create the POST payload
        oper['intentId'] = intent_id
        oper['intentType'] = intent_type    # XXX: Hardcoded
        oper['staticPath'] = static_path              # XXX: Hardcoded
        oper['srcSwitchDpid'] = src_dpid
        oper['srcSwitchPort'] = src_port
        oper['dstSwitchDpid'] = dst_dpid
        oper['dstSwitchPort'] = dst_port
        oper['matchSrcMac'] = src_mac
        oper['matchDstMac'] = dst_mac
        intents.append(oper)
        url = "http://%s:%s/%s"%(intentIP,intentPort,intentURL)
        parsed_result = []
        data_json = json.dumps(intents)
        try:
            request = urllib2.Request(url,data_json)
            request.add_header("Content-Type", "application/json")
            response=urllib2.urlopen(request)
            result = response.read()
            response.close()
            if len(result) != 0:
                parsed_result = json.loads(result)
        except HTTPError as exc:
            print "ERROR:"
            print "  REST GET URL: %s" % url
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
        except URLError as exc:
            print "ERROR:"
            print "  REST GET URL: %s" % url
            print "  URL Error Reason: %s" % exc.reason
        return parsed_result

        


    def add_intents(self):
        main.log.info("Sending new intents to ONOS")
        self.handle.sendline("cd "+self.home+ "/scripts")
        self.handle.expect("scripts")
        main.log.info("Adding intents")
        self.handle.sendline("./pyintents.py")
        self.handle.expect(["$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before
        self.handle.sendline("cd "+self.home)
        return main.TRUE

    def rm_intents(self):
        main.log.info("Deleteing Intents from ONOS")
        self.handle.sendline("cd "+self.home+ "/scripts")
        self.handle.expect("scripts")
        main.log.info("Deleting Intnents")
        self.handle.sendline("./rmpyintents.py")
        self.handle.expect(["$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before
        self.handle.sendline("cd "+self.home)
        return main.TRUE
        
    def purge_intents(self):
        main.log.info("Purging dead intents")
        self.handle.sendline("cd "+self.home+ "/scripts")
        self.handle.expect("scripts")
        main.log.info("Sending Purge Intent Rest call to ONOS")
        self.handle.sendline("./purgeintents.py")
        self.handle.sendline("cd "+self.home)
        return main.TRUE



    def add_flow(self, testONip, user = "admin", password = "", flowDef = "/flowdef.txt"):
        '''
        Copies the flowdef file from TestStation -> ONOS machine
        Then runs ./add_flow.py to add the flows to ONOS
        '''
        try:
            main.log.info("Adding Flows...")
            self.handle.sendline("scp %s@%s:%s /tmp/flowtmp" %(user,testONip,flowDef))
            i=self.handle.expect(['[pP]assword:', '100%', pexpect.TIMEOUT],30)
            if(i==0):
                    self.handle.sendline("%s" %(password))
                    self.handle.sendline("")
                    self.handle.expect("100%")
                    self.handle.expect("\$", 30)
                    self.handle.sendline(self.home + "/web/add_flow.py -m onos -f /tmp/flowtmp")
                    self.handle.expect("\$", 1000)
                    main.log.info("Flows added")
                    return main.TRUE

            elif(i==1):
                    self.handle.sendline("")
                    self.handle.expect("\$", 10)
                    self.handle.sendline( self.home + "/web/add_flow.py -m onos -f /tmp/flowtmp")
                    self.handle.expect("\$", 1000)
                    main.log.info("Flows added")
                    return main.TRUE

            elif(i==2):
                    main.log.error("Flow Def file SCP Timed out...")
                    return main.FALSE

            else:
                    main.log.error("Failed to add flows...")
                    return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


    def delete_flow(self, *delParams):
        '''
        Deletes a specific flow, a range of flows, or all flows.
        '''
        try:
            if len(delParams)==1:
                if str(delParams[0])=="all":
                    main.log.info(self.name + ": Deleting ALL flows...")
                    #self.execute(cmd="~/ONOS/scripts/TestON_delete_flow.sh all",prompt="done",timeout=150)
                    self.handle.sendline(self.home + "/web/delete_flow.py all")
                    self.handle.expect("delete_flow")
                    self.handle.expect("\$",1000)
                    main.log.info(self.name + ": Flows deleted")
                else:
                    main.log.info(self.name + ": Deleting flow "+str(delParams[0])+"...")
                    #self.execute(cmd="~/ONOS/scripts/TestON_delete_flow.sh "+str(delParams[0]),prompt="done",timeout=150)
                    #self.execute(cmd="\n",prompt="\$",timeout=60)
                    self.handle.sendline(self.home +"/web/delete_flow.py %d" % int(delParams[0]))
                    self.handle.expect("delete_flow")
                    self.handle.expect("\$",60)
                    main.log.info(self.name + ": Flow deleted")
            elif len(delParams)==2:
                 main.log.info(self.name + ": Deleting flows "+str(delParams[0])+" through "+str(delParams[1])+"...")
                 #self.execute(cmd="~/ONOS/scripts/TestON_delete_flow.sh "+str(delParams[0])+" "+str(delParams[1]),prompt="done",timeout=150)
                 #self.execute(cmd="\n",prompt="\$",timeout=60)
                 self.handle.sendline(self.home + "/web/delete_flow.py %d %d" % (int(delParams[0]), int(delParams[1])))
                 self.handle.expect("delete_flow")
                 self.handle.expect("\$",600)
                 main.log.info(self.name + ": Flows deleted")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_flow(self):
        '''
        Calls the ./get_flow.py all and checks:
        - If each FlowPath has at least one FlowEntry
        - That there are no "NOT"s found
        returns TRUE/FALSE
        '''
        try:
            flowEntryDetect = 1
            count = 0
            self.handle.sendline("clear")
            time.sleep(1)
            self.handle.sendline(self.home + "/web/get_flow.py all")
            self.handle.expect("get_flow")
            for x in range(15):
                i=self.handle.expect(['FlowPath','FlowEntry','NOT','\$',pexpect.TIMEOUT],timeout=180)
                if i==0:
                    count = count + 1
                    if flowEntryDetect == 0:
                        main.log.info(self.name + ": FlowPath without FlowEntry")
                        return main.FALSE
                    else:
                        flowEntryDetect = 0
                elif i==1:
                    flowEntryDetect = 1
                elif i==2:
                    main.log.error(self.name + ": Found a NOT")
                    return main.FALSE
                elif i==3:
                    if count == 0:
                        main.log.info(self.name + ": There don't seem to be any flows here...")
                        return main.FALSE
                    else:
                        main.log.info(self.name + ": All flows pass")
                        main.log.info(self.name + ": Number of FlowPaths: "+str(count))
                        return main.TRUE
                elif i==4:
                    main.log.error(self.name + ":Check_flow() - Command Timeout!")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def get_flow(self, *flowParams):
        '''
        Returns verbose output of ./get_flow.py
        '''
        try:
            if len(flowParams)==1:
                if str(flowParams[0])=="all":
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    main.log.info(self.name + ": Getting all flow data...")
                    data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh all",prompt="done",timeout=150)
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    return data
                else:
                    main.log.info(self.name + ": Retrieving flow "+str(flowParams[0])+" data...")
                    data = self.execute(cmd=self.home +"/scripts/TestON_get_flow.sh "+str(flowParams[0]),prompt="done",timeout=150)
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    return data
            elif len(flowParams)==5:
                main.log.info(self.name + ": Retrieving flow installer data...")
                data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh "+str(flowParams[0])+" "+str(flowParams[1])+" "+str(flowParams[2])+" "+str(flowParams[3])+" "+str(flowParams[4]),prompt="done",timeout=150)
                self.execute(cmd="\n",prompt="\$",timeout=60)
                return data
            elif len(flowParams)==4:
                main.log.info(self.name + ": Retrieving flow endpoints...")
                data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh "+str(flowParams[0])+" "+str(flowParams[1])+" "+str(flowParams[2])+" "+str(flowParams[3]),prompt="done",timeout=150)
                self.execute(cmd="\n",prompt="\$",timeout=60)
                return data
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


# http://localhost:8080/wm/onos/topology/switches
# http://localhost:8080/wm/onos/topology/links
# http://localhost:8080/wm/onos/registry/controllers/json
# http://localhost:8080/wm/onos/registry/switches/json"

    def get_json(self, url):
        '''
        Helper functions used to parse the json output of a rest call
        '''
        try:
            try:
                command = "curl -s %s" % (url)
                result = os.popen(command).read()
                parsedResult = json.loads(result)
            except:
                print "REST IF %s has issue" % command
                parsedResult = ""
        
            if type(parsedResult) == 'dict' and parsedResult.has_key('code'):
                print "REST %s returned code %s" % (command, parsedResult['code'])
                parsedResult = ""
            return parsedResult
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_switch(self,RestIP,correct_nr_switch, RestPort ="8080" ):
        '''
        Used by check_status
        '''
        try:
            buf = ""
            retcode = 0
            url="http://%s:%s/wm/onos/topology/switches" % (RestIP, RestPort)
            parsedResult = self.get_json(url)
            if parsedResult == "":
                retcode = 1
                return (retcode, "Rest API has an issue")
            url = "http://%s:%s/wm/onos/registry/switches/json" % (RestIP, RestPort)
            registry = self.get_json(url)
        
            if registry == "":
                retcode = 1
                return (retcode, "Rest API has an issue")
        
            cnt = 0
            active = 0

            for s in parsedResult:
                cnt += 1
                if s['state'] == "ACTIVE":
                   active += 1

            buf += "switch: network %d : %d switches %d active\n" % (0+1, cnt, active)
            if correct_nr_switch != cnt:
                buf += "switch fail: network %d should have %d switches but has %d\n" % (1, correct_nr_switch, cnt)
                retcode = 1

            if correct_nr_switch != active:
                buf += "switch fail: network %d should have %d active switches but has %d\n" % (1, correct_nr_switch, active)
                retcode = 1
        
            return (retcode, buf)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_link(self,RestIP, nr_links, RestPort = "8080"):
        '''
        Used by check_status
        '''
        try:
            buf = ""
            retcode = 0
        
            url = "http://%s:%s/wm/onos/topology/links" % (RestIP, RestPort)
            parsedResult = self.get_json(url)
        
            if parsedResult == "":
                retcode = 1
                return (retcode, "Rest API has an issue")
        
            buf += "link: total %d links (correct : %d)\n" % (len(parsedResult), nr_links)
            intra = 0
            interlink=0
        
            for s in parsedResult:
                intra = intra + 1
        
            if intra != nr_links:
                buf += "link fail\n"
                retcode = 1
        
            return (retcode, buf)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_status_report(self, ip, numoswitch, numolink, port="8080"):
        '''
        Checks the number of swithes & links that ONOS sees against the supplied values.
        Writes to the report log.
        '''
        try:
            main.log.info(self.name + ": Making some rest calls...")
            switch = self.check_switch(ip, int(numoswitch), port)
            link = self.check_link(ip, int(numolink), port)
            value = switch[0]
            value += link[0]
            main.log.report( self.name + ": \n-----\n%s%s-----\n" % ( switch[1], link[1]) )
            if value != 0:
                return main.FALSE
            else:
                # "PASS"
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_status(self, ip, numoswitch, numolink, port = "8080"):
        '''
        Checks the number of swithes & links that ONOS sees against the supplied values.
        Writes to the main log.
        '''
        try:
            main.log.info(self.name + ": Making some rest calls...")
            switch = self.check_switch(ip, int(numoswitch), port)
            link = self.check_link(ip, int(numolink), port)
            value = switch[0]
            value += link[0]
            main.log.info(self.name + ": \n-----\n%s%s-----\n" % ( switch[1], link[1]) )
            if value != 0:
                return main.FALSE
            else:
                # "PASS"
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
 
    def check_for_no_exceptions(self):
        '''
        TODO: Rewrite
        Used by CassndraCheck.py to scan ONOS logs for Exceptions
        '''
        try:
            self.handle.sendline("dsh 'grep Exception ~/ONOS/onos-logs/onos.*.log'")
            self.handle.expect("\$ dsh")
            self.handle.expect("\$")
            output = self.handle.before
            main.log.info(self.name + ": " + output )
            if re.search("Exception",output):
                return main.FALSE
            else :
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


    def git_pull(self, comp1=""):
        '''
        Assumes that "git pull" works without login
        
        This function will perform a git pull on the ONOS instance.
        If used as git_pull("NODE") it will do git pull + NODE. This is
        for the purpose of pulling from other nodes if necessary.

        Otherwise, this function will perform a git pull in the 
        ONOS repository. If it has any problems, it will return main.ERROR
        If it successfully does a git_pull, it will return a 1.
        If it has no updates, it will return a 0.

        '''
        try:
            # main.log.info(self.name + ": Stopping ONOS")
            #self.stop()
            self.handle.sendline("cd " + self.home)
            self.handle.expect("ONOS\$")
            if comp1=="":
                self.handle.sendline("git pull")
            else:
                self.handle.sendline("git pull " + comp1)
           
            uptodate = 0
            i=self.handle.expect(['fatal','Username\sfor\s(.*):\s','Unpacking\sobjects',pexpect.TIMEOUT,'Already up-to-date','Aborting','You\sare\snot\scurrently\son\sa\sbranch'],timeout=1700)
            #debug
           #main.log.report(self.name +": \n"+"git pull response: " + str(self.handle.before) + str(self.handle.after))
            if i==0:
                main.log.error(self.name + ": Git pull had some issue...")
                return main.ERROR
            elif i==1:
                main.log.error(self.name + ": Git Pull Asking for username!!! BADD!")
                return main.ERROR
            elif i==2:
                main.log.info(self.name + ": Git Pull - pulling repository now")
                self.handle.expect("ONOS\$", 120)
                return 0
            elif i==3:
                main.log.error(self.name + ": Git Pull - TIMEOUT")
                return main.ERROR
            elif i==4:
                main.log.info(self.name + ": Git Pull - Already up to date")
                return 1
            elif i==5:
                main.log.info(self.name + ": Git Pull - Aborting... Are there conflicting git files?")
                return main.ERROR
            elif i==6:
                main.log.info(self.name + ": Git Pull - You are not currently on a branch so git pull failed!")
                return main.ERROR
            else:
                main.log.error(self.name + ": Git Pull - Unexpected response, check for pull errors")
                return main.ERROR
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
#********************************************************           


    def git_compile(self):
        '''
        Compiles ONOS
        First runs mvn clean then mvn compile
        '''
        try:
            main.log.info(self.name + ": mvn clean")
            self.handle.sendline("cd " + self.home)
            self.handle.sendline("mvn clean")
            while 1:
                i=self.handle.expect(['There\sis\sinsufficient\smemory\sfor\sthe\sJava\sRuntime\sEnvironment\sto\scontinue','BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=30)
                if i == 0:
                    main.log.error(self.name + ":There is insufficient memory for the Java Runtime Environment to continue.")
                    return main.FALSE
                elif i == 1:
                    main.log.error(self.name + ": Clean failure!")
                    return main.FALSE
                elif i == 2:
                    main.log.info(self.name + ": Clean success!")
                elif i == 3:
                    main.log.info(self.name + ": Clean complete")
                    break;
                elif i == 4:
                    main.log.error(self.name + ": mvn clean TIMEOUT!")
                    return main.FALSE
                else:
                    main.log.error(self.name + ": unexpected response from mvn clean")
                    return main.FALSE
        
            main.log.info(self.name + ": mvn compile")
            self.handle.sendline("mvn compile")
            while 1:
                i=self.handle.expect(['There\sis\sinsufficient\smemory\sfor\sthe\sJava\sRuntime\sEnvironment\sto\scontinue','BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=60)
                if i == 0:
                    main.log.error(self.name + ":There is insufficient memory for the Java Runtime Environment to continue.")
                    return main.FALSE
                if i == 1:
                    main.log.error(self.name + ": Build failure!")
                    return main.FALSE
                elif i == 2:
                    main.log.info(self.name + ": Build success!")
                elif i == 3:
                    main.log.info(self.name + ": Build complete")
                    self.handle.expect("\$", timeout=60)
                    return main.TRUE
                elif i == 4:
                    main.log.error(self.name + ": mvn compile TIMEOUT!")
                    return main.FALSE
                else:
                    main.log.error(self.name + ": unexpected response from mvn compile")
                    return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def tcpdump(self, intf = "eth0"):
        '''
        Runs tpdump on an intferface and saves in onos-logs under the ONOS home directory
        intf can be specified, or the default eth0 is used
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("sudo tcpdump -n -i "+ intf + " -s0 -w " + self.home +"/onos-logs/tcpdump &")
            i=self.handle.expect(['No\ssuch\device','listening\son',pexpect.TIMEOUT],timeout=10)
            if i == 0:
                main.log.error(self.name + ": tcpdump - No such device exists. tcpdump attempted on: " + intf)
                return main.FALSE
            elif i == 1:
                main.log.info(self.name + ": tcpdump started on " + intf)
                return main.TRUE
            elif i == 2:
                main.log.error(self.name + ": tcpdump command timed out! Check interface name, given interface was: " + intf)
                return main.FALSE
            else:
                main.log.error(self.name + ": tcpdump - unexpected response")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def kill_tcpdump(self):
        '''
        Kills any tcpdump processes running
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("sudo kill -9 `ps -ef | grep \"tcpdump -n\" | grep -v grep | awk '{print $2}'`")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def find_host(self,RestIP,RestPort,RestAPI,hostMAC):
        retcode = 0 # number of hosts found with given MAC
        retswitch = [] # Switch DPID's of hosts found with MAC
        retport = [] # Switch port connected to to hosts found with MAC
        foundHost = []
        try:
            ##### device rest API is: 'host:8080/wm/onos/topology/switches' ###
            url ="http://%s:%s%s" %(RestIP,RestPort,RestAPI)

            try:
                command = "curl -s %s" % (url)
                result = os.popen(command).read()
                parsedResult = json.loads(result)
                # print parsedResult
            except:
                print "REST IF %s has issue" % command
                parsedResult = ""

            if parsedResult == "":
                return (retcode, "Rest API has an error", retport)
            else:
                for host in enumerate(parsedResult):
                    print host
                    if (host[1] != []):
                        try:
                            foundHost = host[1]['mac']
                        except:
                            print "Error in detecting MAC address."
                        print foundHost
                        print hostMAC
                        if foundHost == hostMAC:
                            for switch in enumerate(host[1]['attachmentPoints']):
                                retswitch.append(switch[1]['dpid'])
                                retport.append(switch[1]['port'])
                            retcode = retcode +1
                            foundHost ='' 
                '''
                for switch in enumerate(parsedResult):
                    for port in enumerate(switch[1]['ports']):
                        if ( port[1]['hosts'] != [] ):
                            try:
                                foundHost = port[1]['hosts'][0]['ipv4addresses'][0]['ipv4']
                            except:
                                print "Error in detecting MAC address."
                            if foundHost == hostMAC:
                                retswitch.append(switch[1]['dpid'])
                                retport.append(port[1]['desc'])
                                retmac.append(port[1]['hosts'][0]['mac'])
                                retcode = retcode +1
                                foundHost =''
                '''
            return(retcode, retswitch, retport)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_exceptions(self):
        '''
        Greps the logs for "xception"
        '''
        try:
            output = ''
            self.handle.sendline("")
            i = self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            #main.log.warn("first expect response: " +str(i))
            self.handle.sendline("cd "+self.home+"/onos-logs")
            self.handle.sendline("grep \"xception\" *")
            i = self.handle.expect(["\*",pexpect.EOF,pexpect.TIMEOUT])
            #main.log.warn("second expect response: " +str(i))
            i = self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            #main.log.warn("third expect response: " +str(i))
            response = self.handle.before
            count = 0
            for line in response.splitlines():
                if re.search("log:", line):
                    output +="Exceptions found in " + line + "\n"
                    count +=1
                elif re.search("std...:",line):
                    output+="Exceptions found in " + line + "\n"
                    count +=1
                else:
                    pass
                    #these should be the old logs
            main.log.report(str(count) + " Exceptions were found on "+self.name)
            return output
        except pexpect.TIMEOUT:
            main.log.error(self.name + ": Timeout exception found in check_exceptions function")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
