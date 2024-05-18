#
##
# @mainpage Connecting station to WI-FI
#
# @section description_main Description
# This class connects a micro controller station to a WI-FI network
#
# @section station_documentation External resources
# - [network module](https://docs.micropython.org/en/latest/library/network.html)
#   - [WLAN class](https://docs.micropython.org/en/latest/library/network.WLAN.html)
#
# @section notes_main Notes
# - Testing
#   - Raspberry Pico w
#   - MicroPython v22 or later
#

##
# @file sta_connect.py
#
# @section description_sta_connect Description
# sta_connect is used to connect to know access points (in config).
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
# @section todo_sta_connect TODO
# - None.
#
# @section author_doxygen_example Author(s)
# - Created by Curt Timmerman 01/01/2024

##
# @file sta_connect_config.py
#

#import sys
import network
import time
import binascii

import sta_connect_config as config

## show_all default
SHOW_ALL = False

##
# Defines the base class for WLAN interface.
#
class WlanStation :

    def __init__ (self ,
                  show_all = SHOW_ALL) :
        ##
        # The WlanStation base class initializer.
        #
        # @param show_all Prints activity log.
        #
        # @return  WlanStation instance.
        #

        ## Sets instance show_all
        self.show_all = show_all

        ## status_constants - As defined in the MP documentation
        #
        # @section wlan_documentation External resources
        # [WLAN documentation](https://docs.micropython.org/en/latest/library/network.WLAN.html)
        #
        # @section notes_on_status_constants Notes
        # - Not all implementations include every status constant
        #
        self.ap_config = None
        self.status_constants = {
            'STAT_CONNECTING' : {
                "status_value" : "Not implemented" ,
                "success" : False ,
                "fatal" : False ,
                "message" : "Connecting..."
                } ,
            'STAT_CONNECT_FAIL' : {
                "status_value" : "Not implemented" ,
                "success" : False ,
                "fatal" : True ,
                "message" : "Fail - Could not connect"
                } ,
            'STAT_WRONG_CONNECT_FAIL' : {
                "status_value" : "Not implemented" ,
                'success' : False ,
                "fatal" : True ,
                "message" : "Fail - Wrong connect"
                } ,
            'STAT_GOT_IP' : {
                "status_value" : "Not implemented" ,
                'success' : True ,
                "fatal" : False ,
                "message" : "Connected"
                } ,
            'STAT_IDLE' : {
                "status_value" : "Not implemented" ,
                'success' : False ,
                "fatal" : False ,
                "message" : "Idle"
                } ,
            'STAT_WRONG_PASSWORD' : {
                "status_value" : "Not implemented" ,
                'success' : False ,
                "fatal" : True ,
                "message" : "Fail - Invalid password"
                } ,
            'STAT_NO_AP_FOUND' : {
                "status_value" : "Not implemented" ,
                'success' : False ,
                "fatal" : True ,
                "message" : "Fail - No access point"
                } ,
            "_UNKNOWN_" : {            # This is not a valid network constant
                "status_value" : "Not implemented" ,
                'success' : False ,
                "fatal" : False ,
                "message" : "Unknown status"
                }
            }
        ## implemented by \_\_INIT\_\_ function
        #
        # @section notes_on_status_results
        # - 
        self.status_results = {
            }
        if self.show_all :
            print ("\n__init__: Entry")
        for status_key in self.status_constants :
            if status_key == '_UNKNOWN_' :
                continue
            if hasattr (network, status_key) :
                status_value = getattr (network, status_key)
                self.status_results [status_value] \
                    = self.status_constants [status_key]
                self.status_results [status_value]["constant_id"] \
                    = status_key
                self.status_results [status_value]["status_value"] = status_value
            else :
                if self.show_all :
                    print ("network module missing constant:", status_key)
        #
        self.wlan = network.WLAN (network.STA_IF)
        if self.show_all :
            self.show_network ()

    def connect (self, ap_config = None) :
        if self.show_all :
            print ("\nconnect: Entry")
        connect_result = None
        self.disconnect_from_ap ()
        self.ap_config = ap_config
        ## Multiple tries are required when password changes
        for retry_count in range (3) :
            connect_result = self.connect_to_ap ()
            if connect_result is not None :
                break
        return connect_result

    def disconnect (self) :
        if self.show_all :
            print ("\ndisconnect: Entry")
        self.disconnect_from_ap ()

    def disconnect_from_ap (self) :
        if self.show_all :
            print ("\ndisconnect_from_ap: Entry")
        ## Clear existing connection, this doesn't work
        if self.wlan.active() :
            if self.show_all :
                print ("Deactivate")
            if self.wlan.isconnected () :
                if self.show_all :
                    print ("Disconnecting")
                self.wlan.disconnect ()
                for retry_count in range (20) : # wait for dicconnect
                    if not self.wlan.isconnected () :
                        break
                    if self.show_all :
                        print ("waiting disconnect")
                    time.sleep_ms (50)
            self.wlan.active(False)
            for retry_count in range (20) : # wait for inactive
                if not self.wlan.active () :          # is this needed?
                    break
                if self.show_all :
                    print ("waiting inactive")
                time.sleep_ms (50)

    def wifi_scan (self) :
        if self.show_all :
            print ("\nwifi_scan: Entry")
        self.ap_config = None
        if self.show_all :
            print ("Scanning for access points...")
        self.wlan.active(True)
        ## Do multiple scans because scans do not always return the same list of AP's
        for retry_count in range (10) :
            if self.show_all :
                print ("scan: pass:", (retry_count + 1))
            ## Get available access points
            scan_aps = self.wlan.scan()
            #print (scan_aps)
            for scan_ap in scan_aps :
                if self.show_all :
                    print ("Scanned accesspoint:", scan_ap)
                ssid = scan_ap[0].decode ()
                #print ("ssid:", ssid)
                if ssid not in config.SSID_LIST :
                    continue
                if self.ap_config is not None :
                    if ssid == self.ap_config ["ssid"] :
                        continue               # Already in AP return
                    if config.SSID_LIST[ssid]["priority"] <= self.ap_config["priority"] :
                        if self.show_all :
                            print ("skipping:", ssid)
                        continue
                self.ap_config = {
                    "ssid" : ssid ,
                    "bssid" : binascii.hexlify (scan_ap [1]) ,
                    "channel" : scan_ap [2] ,
                    "RSSI" : scan_ap [3] ,
                    "security" : scan_ap [4] ,
                    "hidden" : scan_ap [5] == 1
                    }    # update AP return
                self.ap_config.update (config.SSID_LIST[ssid]) # add parameters
                if self.show_all :
                    print ("AP selected:", self.ap_config)
            if self.ap_config is not None \
            and retry_count >= 3 :
                break

        if self.ap_config is None :
            self.wlan.active(False)
        return self.ap_config
    # end wifi_scan #

    def connect_to_ap (self) :
        if self.show_all :
            print ("\nconnect_to_ap: Entry")
        #---- get access point
        if self.ap_config is None :
            self.ap_config = self.wifi_scan ()
        if self.ap_config is None :
            print ("No known access points found")
            return None

        #self.ap_config["password"] = "Error" # for testing
        #self.ap_config["ssid"] = "Error"     # for testing
        if self.show_all :
            print('connecting to WIFI:', self.ap_config["ssid"])
            #print (self.ap_config)
        if "ifconfig" in self.ap_config :
            self.wlan.ifconfig (self.ap_config["ifconfig"])
        #print ("SSID:" + self.ap_config["ssid"], "PW:" + self.ap_config["password"])
        self.wlan.connect (self.ap_config["ssid"], self.ap_config["password"])
        connect_max_ms = time.ticks_add (time.ticks_ms (), (config.CONNECT_TIMEOUT_SECONDS * 1000))
        connect_fail_message = "Connect TIME OUT"
        while time.ticks_diff (connect_max_ms, time.ticks_ms ()) > 0 :
            time.sleep_ms (100)
            status = self.wlan.status ()
            if self.show_all :
                print ("wlan status:", status)
            status_data = None
            if status in self.status_results :
                status_data = self.status_results [status]
            else :
                status_data = self.status_constants ["_UNKNOWN_"]
                status_data ["message"] = "Unknown status: " + str (status)
            if self.show_all :
                print ("status info:", status_data)
            if status_data ["success"] :
                if_config = self.wlan.ifconfig()
                if self.show_all :
                    print (status_data ["message"] + ":", if_config)
                return if_config
            if status_data ["fatal"] :
                connect_fail_message = status_data ["message"]
                break
            continue # try again
        print (connect_fail_message)
        self.wlan.active(False)
        return None

    ## Show information about the network class
    #
    # @details
    # - Displays:
    #   - List of WLAN class constants
    #
    # @section TODO
    # - Add more network information
    #
    def show_network (self) :
        print ("network module status constants:")
        for stat_var in self.status_constants :
            if stat_var == "_UNKNOWN_" :
                continue
            stat_val = "Not implemented"
            if hasattr (network, stat_var) :
                stat_val = getattr (network, stat_var)
            print (stat_var, "=", stat_val)

"""
#ifndef DOXYGEN_SHOULD_SKIP_THIS
"""
if __name__ == "__main__" :
    sta = WlanStation (show_all=False)
    #sta.show_network ()
    #print (sta.wifi_scan ())
    conn_result = sta.connect ()
    if conn_result is not None :
        print ("Connected:", conn_result)
    #time.sleep (5)
    #sta.disconnect ()
"""
#endif
"""