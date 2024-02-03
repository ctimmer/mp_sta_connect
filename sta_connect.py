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

## connection timeout
CONNECT_TIMEOUT_SECONDS = 10
## country code for access point (unused at this time)
WIFI_COUNTRY = "US"
## Valid SSID/PASSWORD table
SSID_LIST = {
    "Crema guest" : {
        "password" : "Happy2024!" ,
        "priority" : 0
        } ,
    "myrouter" : {
        "password" : "mypassword" ,
        "ifconfig" : ('192.168.19.100', '255.255.0.0', '192.168.1.1', '8.8.8.8') ,
        "priority" : 10
        } ,
    "myotherrouter" : {
        "password" : "myotherpassword" ,
        "ifconfig" : ('192.168.19.100', '255.255.0.0', '192.168.1.1', '8.8.8.8') ,
        "priority" : 0
        } ,
    "OpenRouter" : {       # AP with no password
        "password" : None ,
        "priority" : 0
        }
    }

def do_disconnect (wlan) :
    #---- Clear existing connection
    if wlan.active() :
        print ("Deactivate")
        if wlan.isconnected () :
            print ("Disconnecting")
            wlan.disconnect ()
            for retry_count in range (20) : # wait for dicconnect
            #while wlan.isconnected () : # wait for dicconnect
                if not wlan.isconnected () :
                    break
                print ("waiting disconnect")
                time.sleep_ms (50)
        wlan.active(False)
        for retry_count in range (20) : # wait for inactive
            if not wlan.active () :          # is this needed?
                break
            print ("waiting inactive")
            time.sleep_ms (50)

def do_wifi_scan (wlan) :
    ap_return = None
    #do_disconnect (wlan)

    print ("Scanning...")
    wlan.active(True)
    #---- Do multiple scans because scans do not always return the same set of AP's
    for retry_count in range (10) :
        access_points = wlan.scan()
        #print (access_points)
        for access_point in access_points :
            #print (access_point)
            ssid = access_point[0].decode ()
            #print ("ssid:", ssid)
            if ssid not in SSID_LIST :
                continue
            if ap_return is not None :
                if ssid == ap_return ["ssid"] :
                    continue               # Already in AP return
                if SSID_LIST[ssid]["priority"] <= ap_return["priority"] :
                    print ("skipping:", ssid)
                    continue
            ap_return = {"ssid" : ssid}    # update AP return
            ap_return.update (SSID_LIST[ssid]) # add parameters
        if ap_return is not None \
        and retry_count >= 3 :
            break

    if ap_return is None :
        wlan.active(False)
    return ap_return

def do_connect(disconnect_only = False):
    #import network
    access_point = None
    wlan = network.WLAN(network.STA_IF)
    do_disconnect (wlan)
    if disconnect_only :
        return None

    #---- get access point
    access_point = do_wifi_scan (wlan)
    if access_point is None :
        print ("No known access points found")
        return None

    #access_point["password"] = "Error" # for testing
    #access_point["ssid"] = "Error"     # for testing
    print('connecting to WIFI:', access_point["ssid"])
    if "ifconfig" in access_point :
        wlan.ifconfig (access_point["ifconfig"])
    print ("SSID:" + access_point["ssid"], "PW:" + access_point["password"])
    wlan.connect (access_point["ssid"], access_point["password"])
    connect_max_ms = time.ticks_add (time.ticks_ms (), (CONNECT_TIMEOUT_SECONDS * 1000))
    connect_fail_message = "Connect TIME OUT"
    while time.ticks_diff (connect_max_ms, time.ticks_ms ()) > 0 :
        time.sleep_ms (100)
        status = wlan.status ()
        print ("status:", status)
        if status == network.STAT_CONNECTING :
            #print ("Connecting...")
            continue
        if status == network.STAT_GOT_IP :
            print('Connected:', wlan.ifconfig())
            return
        if status == network.STAT_WRONG_PASSWORD :
            connect_fail_message = "Invalid PASSWORD"
            break
        if status == network.STAT_NO_AP_FOUND :
            connect_fail_message = "Invalid SSID"
            break
        # Some versions (pico w) don't have this return value
        #if True :
        if hasattr (network, 'STAT_WRONG_CONNECT_FAIL') :
            if status == network.STAT_WRONG_CONNECT_FAIL :
                connect_fail_message = "Wrong connect FAIL"
                break
        if status == network.STAT_IDLE :
            #print ("Idle")
            continue
        # Shouldn't be here???
        connect_fail_message = "Unknown status:" + str (status)
        break

    print (connect_fail_message)
    wlan.active(False)

def show_network () :
    import network
    stat_list = ['STAT_CONNECTING',
                 'STAT_CONNECT_FAIL',
                 'STAT_WRONG_CONNECT_FAIL' ,
                 'STAT_GOT_IP',
                 'STAT_IDLE',
                 'STAT_WRONG_PASSWORD' ,
                 'STAT_NO_AP_FOUND']
    for stat_var in stat_list :
        stat_val = "Not implemented"
        if hasattr (network, stat_var) :
            stat_val = getattr (network, stat_var)
        print (stat_var, "=", stat_val)

show_network ()            
do_connect ()
