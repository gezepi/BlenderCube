"""
	Uses the MCP2210 library from https://github.com/ondra/mcp2210
"""
import time
import os
import sys
import mathutils
import math

includeSPI = False
try:
	from mcp2210 import MCP2210
	ignoreSPI = True
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
		for z in range(cubeSize):
			for i in range(cubeSize):
				dev.transfer([chr(z)] + data[i])

if includeBlender:
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
	
	def updateCube(scene):
		#Get LED Cubes
		cur_cube = scene.objects['LED Cube']
		#Cube vertices
		verts = [cur_cube.matrix_world * vert.co for vert in cur_cube.data.vertices]
		plain_verts = [Vector(v.to_tuple()) for v in verts]
		#print(plain_verts)
			
		#Get intersecting bodies
		bodies = []
		for ob in scene.objects:
			if ob.type == 'MESH' and ob.name != "LED Cube":
				bodies.append(ob)
		#print("Colliding bodies:{0}".format(len(bodies)))
		
		lit = []
		#print("{0} bodies to check".format(len(bodies)))
		for b in bodies:
			#print("Checking collision for {0}".format(b.name))
			newVerts = [b.matrix_world * v.co for v in b.data.vertices]
			newBmesh = bpy.data.meshes.new(b.name + "_globalVertsMesh")
			#[print(e) for e in b.data.edges]
			newBmesh.from_pydata(newVerts, [], [(3,2,0,1),(1,0,4,5),(5,7,3,1),(2,3,7,6),(5,4,6,7),(0,2,6,4)])
			newB = bpy.data.objects.new(b.name + "_globalVerts", newBmesh)
			#print(dir(newB.data))
			
			#print("b:{0}\tnewB:{1}".format(type(b), type(newB)))
			#[print(b.matrix_world * v.co) for v in newB.data.vertices]
			#[print(v) for v in plain_verts]
			scene.objects.link(newB)
			scene.update()
			
			lit = lit + [is_inside(x, 1e+19, newB) for x in plain_verts]
		print("{0} intersecting LEDs".format(sum(lit)))
	
		#Remove old ghost boxes
		for ob in scene.objects:
			ob.select = (ob.type == 'MESH' and '_global' in ob.name)
		bpy.ops.object.delete()
		
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