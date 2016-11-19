"""
	Uses the MCP2210 library from https://github.com/ondra/mcp2210
"""
import time
import os
import sys
from array import array
import numpy

includeSPI = False
try:
	from mcp2210 import MCP2210
	ignoreSPI = True
except:
	pass

includeBlender = any("Blender Foundation" in path for path in sys.path)
print("Include Blender pieces of code? {0}".format(includeBlender))
print("Include SPI pieces of code? {0}".format(includeSPI))
print("Running from {0}".format(os.path.dirname(os.path.realpath(__file__))))

vid = 0x4D8
pid = 0xDE

spiDev = None

cubeCenter = (0, 0, 0)
cubeWidth = 1	#Length of one side in Blender
cubeSize = 8	#Number of points on a side

if includeSPI:
	def setupSPI():
		spiDev = MCP2210(vid, pid)
		print(dev.product_name)
		print(dev.manufacturer_name)
		
		settings = dev.boot_chip_settings
		settings.pin_designations[0] = 0x01	#GPIO 3(??) as CS
		dev.boot_chip_settings = settings

		spisettings = dev.boot_transfer_settings
		spisettings.idle_cs = 0x01
		spisettings.active_cs = 0x00
		dev.boot_transfer_settings = spisettings

	def sendDebug():
		i = 0
		while(1):
			print("Transferring {0}...".format(i))
			dev.transfer([chr(0x7F), chr(0x77), chr(0xDD), chr(i)])
			i += 1
			time.sleep(1)	#seconds
			
	def outputCube(data):
		for z in range(8):
			for i in range(8):
			dev.transfer([chr(z)] + data[i])

if includeBlender:
	from mathutils import Vector
	
	def newPoint(name, verts):
		me = bpy.data.meshes.new(name+'Mesh')
		ob = bpy.data.objects.new(name, me)
		ob.show_name = True
		
		bpy.context.scene.objects.link(ob)
		me.from_pydata(verts, [], [])
		me.update()
		return ob
		
	def is_inside(p, max_dist, obj):
		ret = obj.closest_point_on_mesh(p, max_dist)
		point, normal, face = ret[1:4]
		p2 = point-p
		v = p2.dot(normal)
		return 1 if not(v < 0.0) else 0
		
	def getVertices(center, width, size):
		verts = []
		for x in range(8):
			nx = (center[0] - width/2) + x * width/(size - 1)
			for y in range(8):
				ny = (center[1] - width/2) + y * width/(size - 1)
				for z in range(8):
					nz = (center[2] - width/2) + z * width/(size - 1)
					verts.append(Vector((nx, ny, nz)))
		print("Num points:{0}".format(len(verts)))
		return verts
	
	def setObjectMode(mode):
		if bpy.context.active_object.mode != mode:
			bpy.ops.object.editmode_toggle()
	
	setObjectMode('OBJECT')
	leds = getVertices(cubeCenter, cubeWidth, cubeSize)
	newPoint("LED_Cube", leds)
	
	lit = [is_inside(x, 1.84e+19, bpy.context.active_object) for x in leds]
	newlit = [lit[i:i+8] for i in range(64)]
	chrList = [chr(int(''.join(map(str,x)),2)) for x in newlit]
	print(type(chrList))
	print(chrList)
	print(type(lit))
	print(len(chrList))
	#print(lit)
