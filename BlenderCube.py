"""
	Uses the MCP2210 library from https://github.com/ondra/mcp2210
"""
from mcp2210 import MCP2210
import time

vid = 0x4D8
pid = 0xDE

dev = MCP2210(vid, pid)

print(dev.product_name)
print(dev.manufacturer_name)

settings = dev.boot_chip_settings
settings.pin_designations[0] = 0x01	#GPIO 3(??) as CS
dev.boot_chip_settings = settings

spisettings = dev.boot_transfer_settings
spisettings.idle_cs = 0x01
spisettings.active_cs = 0x00
dev.boot_transfer_settings = spisettings

i = 0

while(1):
	print("Transferring {0}...".format(i))
	dev.transfer([chr(0x7F), chr(0x77), chr(0xDD), chr(i)])
	i += 1
	time.sleep(1)	#seconds
	#dev.cancel_transfer()