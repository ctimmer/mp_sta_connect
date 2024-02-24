#

## connection timeout
CONNECT_TIMEOUT_SECONDS = 10
## country code for access point (unused at this time)
WIFI_COUNTRY = "US"
## Valid SSID/PASSWORD table
SSID_LIST = {
    "Crema guest" : {
        "password" : "Comeonspring!" ,
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
