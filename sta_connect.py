#
##
# @mainpage Example connecting station to WI-FI
#
# @section description_main Description
# This program connects a micro controller station to a WI-FI network
#
# @section notes_main Notes
# - Testing
#   - Raspberry Pico w
#   - MicroPython v22 or later
#

##
# @file sta_connect.py
#
#
# @section description_sta_connect Description
# Source for example station connection code.
#
# @section libraries_main Libraries/Modules
# - sys
#   - Used when debugging
# - network
#   - Used to access WLAN
#   - Used to access status and STAT_* constants
# - time
#   - Access to time_ms, ticks_* functions.
#
# @section notes_doxygen_example Notes
# - Comments are Doxygen compatible.
#
# @section todo_sta_connect TODO
# - None.
#
# @section author_doxygen_example Author(s)
# - Created by Curt Timmerman 01/01/2024

#import sys
import network
import time

import sta_connect_config as config

class wlan_station :
    status_constants = {
        'STAT_CONNECTING' : {
            "success" : False ,
            "fatal" : False ,
            "message" : "Connecting..."
            } ,
        'STAT_CONNECT_FAIL' : {
            "success" : False ,
            "fatal" : True ,
            "message" : "Fail - Could not connect"
            } ,
        'STAT_WRONG_CONNECT_FAIL' : {
            'success' : False ,
            "fatal" : True ,
            "message" : "Fail - Wrong connect"
            } ,
        'STAT_GOT_IP' : {
            'success' : True ,
            "fatal" : False ,
            "message" : "Connected"
            } ,
        'STAT_IDLE' : {
            'success' : False ,
            "fatal" : False ,
            "message" : "Idle"
            } ,
        'STAT_WRONG_PASSWORD' : {
            'success' : False ,
            "fatal" : True ,
            "message" : "Fail - Invalid password"
            } ,
        'STAT_NO_AP_FOUND' : {
            'success' : False ,
            "fatal" : True ,
            "message" : "Fail - No access point"
            } ,
        "UNKNOWN" : {
            'success' : False ,
            "fatal" : True ,
            "message" : "Unknown status"
            }
        }
    ## implemented by __INIT__
    status_results = {
        }
    def __init__ (self ,
                  show_all = False) :
        self.show_all = show_all
        for status_key in wlan_station.status_constants :
            if status_key == 'UNKNOWN' :
                continue
            if hasattr (network, status_key) :
                wlan_station.status_results [getattr (network, status_key)] \
                    = wlan_station.status_constants [status_key]
                wlan_station.status_results [getattr (network, status_key)]["constant_id"] \
                    = status_key
            else :
                pass # do something here?
        #
        self.wlan = network.WLAN (network.STA_IF)
        self.access_point = None

    def connect (self) :
        self.disconnect_from_ap ()
        self.connect_to_ap ()

    def disconnect_from_ap (self) :
        ## Clear existing connection, this doesn't work
        if self.wlan.active() :
            print ("Deactivate")
            if self.wlan.isconnected () :
                print ("Disconnecting")
                self.wlan.disconnect ()
                for retry_count in range (20) : # wait for dicconnect
                #while self.wlan.isconnected () : # wait for dicconnect
                    if not self.wlan.isconnected () :
                        break
                    #print ("waiting disconnect")
                    time.sleep_ms (50)
            self.wlan.active(False)
            for retry_count in range (20) : # wait for inactive
                if not self.wlan.active () :          # is this needed?
                    break
                #print ("waiting inactive")
                time.sleep_ms (50)

    def wifi_scan (self) :
        ap_return = None
        print ("Scanning for access points...")
        self.wlan.active(True)
        ## Do multiple scans because scans do not always return the same set of AP's
        for retry_count in range (10) :
            access_points = self.wlan.scan()
            #print (access_points)
            for access_point in access_points :
                #print (access_point)
                ssid = access_point[0].decode ()
                #print ("ssid:", ssid)
                if ssid not in config.SSID_LIST :
                    continue
                if ap_return is not None :
                    if ssid == ap_return ["ssid"] :
                        continue               # Already in AP return
                    if config.SSID_LIST[ssid]["priority"] <= ap_return["priority"] :
                        print ("skipping:", ssid)
                        continue
                ap_return = {"ssid" : ssid}    # update AP return
                ap_return.update (config.SSID_LIST[ssid]) # add parameters
            if ap_return is not None \
            and retry_count >= 3 :
                break

        if ap_return is None :
            self.wlan.active(False)
        return ap_return

    def connect_to_ap (self, access_point = None) :
        #---- get access point
        if access_point is None :
            access_point = self.wifi_scan ()
        if access_point is None :
            print ("No known access points found")
            return None

        #access_point["password"] = "Error" # for testing
        #access_point["ssid"] = "Error"     # for testing
        print('connecting to WIFI:', access_point["ssid"])
        if "ifconfig" in access_point :
            self.wlan.ifconfig (access_point["ifconfig"])
        #print ("SSID:" + access_point["ssid"], "PW:" + access_point["password"])
        self.wlan.connect (access_point["ssid"], access_point["password"])
        connect_max_ms = time.ticks_add (time.ticks_ms (), (config.CONNECT_TIMEOUT_SECONDS * 1000))
        connect_fail_message = "Connect TIME OUT"
        while time.ticks_diff (connect_max_ms, time.ticks_ms ()) > 0 :
            time.sleep_ms (100)
            status = self.wlan.status ()
            #print ("status:", status)
            status_data = None
            if status in wlan_station.status_results :
                status_data = wlan_station.status_results [status]
            else :
                status_data = wlan_station.status_constants ["UNKNOWN"]
                status_data ["message"] = "Unknown status: " + str (status)
            #print (status_data)
            if status_data ["success"] :
                print (status_data ["message"] + ":", self.wlan.ifconfig())
                return
            if status_data ["fatal"] :
                connect_fail_message = status_data ["message"]
                break
            continue # try again
        print (connect_fail_message)
        self.wlan.active(False)
        return

    def show_network (self) :
        for stat_var in  wlan_station.status_constants :
            if stat_var == "UNKNOWN" :
                continue
            stat_val = "Not implemented"
            if hasattr (network, stat_var) :
                stat_val = getattr (network, stat_var)
            print (stat_var, "=", stat_val)

sta = wlan_station ()
#print (sta.wifi_scan ())
sta.connect ()
#sta.show_network ()            

