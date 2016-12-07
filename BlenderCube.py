"""
	Uses the MCP2210 library from https://github.com/ondra/mcp2210
"""
import time
import os
import sys
import math

includeSPI = False
try:
	from mcp2210 import MCP2210
	includeSPI = True
except:
	pass

includeBlender = any("Blender Foundation" in path for path in sys.path)
print("Include Blender pieces of code? {0}".format(includeBlender))
print("Include SPI pieces of code? {0}".format(includeSPI))
print("Running {0} from {1}".format(__file__, os.path.dirname(os.path.realpath(__file__))))

vid = 0x4D8
pid = 0xDE

spiDev = None

cubeCenter = (0, 0, 0)
cubeWidth = 4	#Length of one side in Blender
cubeSize = 8	#Number of points on a side

if includeSPI:
	def setupSPI():
		global spiDev
		spiDev = MCP2210(vid, pid)
		print(spiDev.product_name)
		print(spiDev.manufacturer_name)
		
		settings = spiDev.boot_chip_settings
		settings.pin_designations[0] = 0x01	#GPIO 3(??) as CS
		spiDev.boot_chip_settings = settings

		spisettings = spiDev.boot_transfer_settings
		spisettings.idle_cs = 0x01
		spisettings.active_cs = 0x00
		spisettings.spi_tx_size = cubeSize * 2
		spiDev.boot_transfer_settings = spisettings

	def sendDebug():
		i = 0
		while(1):
			print("Transferring {0}...".format(i))
			spiDev.transfer([chr(0x7F), chr(0x77), chr(0xDD), chr(i)])
			i += 1
			time.sleep(1)	#seconds
			
	def outputCube(data):
		for z in range(cubeSize):
			for i in range(cubeSize):
				spiDev.transfer([chr(z)] + data[i])
	
	def maxTransferAll(address, value):
		print("Sending {0} to {1}".format(value, address))
		sendVal = (address + value) * cubeSize
		spiDev.transfer(sendVal)
		
	def cubeTest():
		for i in range(cubeSize):
			maxTransferAll('\{0}'.format(i+1), '\0xFF')
			time.sleep(.5)
		for i in range(cubeSize):
			maxTransferAll('\{0}'.format(i+1), '\0x00')
			time.sleep(.5)

	setupSPI()
	while(1):
		cubeTest()
		time.sleep(1)

if includeBlender:
	import mathutils
	from mathutils import Vector
	
	def newPoints(name, verts, context):
		me = bpy.data.meshes.new(name+'Mesh')
		ob = bpy.data.objects.new(name, me)
		ob.show_name = True
		
		me.update()
		me.from_pydata(verts, [], [])
		context.scene.objects.link(ob)
		return ob
		
	def is_inside(p, max_dist, obj):
		ret = obj.closest_point_on_mesh(p, max_dist)
		point, normal, face = ret[1:4]
		p2 = point-p
		v = p2.dot(normal)
		return 1 if not(v < 0.0) else 0
		
	def getVertices(center, width, size):
		verts = []
		for x in range(cubeSize):
			nx = (center[0] - width/2) + x * width/(size - 1)
			for y in range(cubeSize):
				ny = (center[1] - width/2) + y * width/(size - 1)
				for z in range(cubeSize):
					nz = (center[2] - width/2) + z * width/(size - 1)
					verts.append(Vector((nx, ny, nz)))
		return verts
	
	def setObjectMode(mode):
		if bpy.context.active_object.mode != mode:
			bpy.ops.object.editmode_toggle()
	
	def runTestCode():
		setObjectMode('OBJECT')
		leds = getVertices(cubeCenter, cubeWidth, cubeSize)
		newPoints("LED_Cube", leds)
		
		lit = [is_inside(x, 1.84e+19, bpy.context.active_object) for x in leds]
		newlit = [lit[i:i+cubeSize] for i in range(cubeSize**2)]
		chrList = [chr(int(''.join(map(str,x)),2)) for x in newlit]
		print(type(chrList))
		print(chrList)
		print(type(lit))
		print(len(chrList))
		
	def displayCube(litVerts):
		i = 0
		for ob in bpy.context.scene.objects:
			ob.select = (ob.type == 'MESH' and 'led_' in ob.name)
			i += 1
		print("Deleting {0} items".format(i))
		bpy.ops.object.delete()
		
		s = .1
		
		for v in litVerts:
			bpy.ops.mesh.primitive_cube_add(radius=s)
			led = bpy.context.object
			led.name = 'led_{0}'.format(v)
			bpy.ops.object.select_all(action='DESELECT')
			
			
			
	
	def updateCube(scene):
		#Get LED Cubes
		cur_cube = scene.objects['LED Cube']
		#Cube vertices
		verts = [cur_cube.matrix_world * vert.co for vert in cur_cube.data.vertices]
		plain_verts = [Vector(v.to_tuple()) for v in verts]
			
		#Get intersecting bodies
		bodies = []
		for ob in scene.objects:
			if ob.type == 'MESH' and ob.name != "LED Cube":
				bodies.append(ob)
		
		lit = []
		litVertices = []
		
		from mathutils import Matrix
		
		for b in bodies:
			moveX = b.location[0]
			moveY = b.location[1]
			moveZ = b.location[2]
			matrixFwd = Matrix.Translation((moveX, moveY, moveZ))
			matrixRev = Matrix.Translation((-moveX, -moveY, -moveZ))
			b.data.transform(matrixFwd)
			b.data.update()
			
			#for v in plain_verts:
			#	i = is_inside(v, 1e+19, b)
			#	lit.append(i)
			#	if i == 1:
			#		litVertices.append(v)
					
			lit = lit + [is_inside(x, 1e+19, b) for x in plain_verts]
			b.data.transform(matrixRev)
			b.data.update()
		#displayCube(litVertices)
		print("{0} intersecting LEDs".format(sum(lit)))
		
	class MakeLedCube(bpy.types.Operator):
		"""Makes a cube of LEDs that can be interacted with"""
		bl_idname = "mesh.make_ledcube"
		bl_label = "Add LED Cube"
		
		def invoke(self, context, event):
			#setObjectMode('OBJECT')
			points = newPoints("LED Cube", getVertices(cubeCenter, cubeWidth, cubeSize), context)
			#print("points.data has {0}".format(dir(points.data)))
						
			return {"FINISHED"}
	
	def register():
		bpy.app.handlers.frame_change_pre.append(updateCube)
		bpy.utils.register_class(MakeLedCube)
		print("Registered")
	
	def unregister():
		bpy.util.unregister_class(MaeLedCube)
		
	if __name__ == "__main__":
		register()