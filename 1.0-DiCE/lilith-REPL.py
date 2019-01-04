# -*- coding: utf-8 -*-

import lilith

lilith.main()
while(True):
    inp = raw_input("(Start)MaintenanceMode (Stop)MaintenanceMode (E)xit : ")
    if(inp=="Start"):
        print("StartMaintenanceMode")
        lilith.maintenance_mode(True)
    elif(inp=="Stop"):
        print("StopMaintenanceMode")
        lilith.maintenance_mode(False)
    elif(inp=="E"):
        print("StoppingServer...")
        lilith.SERVER_RUN = False
