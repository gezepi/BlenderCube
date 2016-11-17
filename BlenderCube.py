"""
	Uses the MCP2210 library from https://github.com/ondra/mcp2210
"""
import time
import os
import sys
includeSPI = False
try:
	from mcp2210 import MCP2210
	ignoreSPI = True
except:
	pass

includeBlender = any("Blender Foundation" in path for path in sys.path)
print("Include Blender pieces of code? {0}".format(includeBlender))

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
		# max_dist = 1.84467e+19
		# From http://blender.stackexchange.com/questions/31693/how-do-find-in-a-point-is-inside-a-mesh
		#[print(x) for x in dir(obj)]
		ret = obj.closest_point_on_mesh(p, max_dist)
		#print(ret[1:4])
		point, normal, face = ret[1:4]
		p2 = point-p
		v = p2.dot(normal)
		#print(v)
		return not(v < 0.0)
		
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
	
	location = bpy.context.scene.cursor_location
	
	if bpy.context.active_object.mode != 'OBJECT':
		bpy.ops.object.editmode_toggle()
	
	leds = getVertices(cubeCenter, cubeWidth, cubeSize)
	newPoint("Cube", leds)
	
	#[print(x) for x in dir(bpy.context.active_object)]
	lit = [is_inside(x, 1.84e+19, bpy.context.active_object) for x in leds]
	print(len(lit))
	print(lit)
