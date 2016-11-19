#
# CoDEmanX, pi
# 19.1.2014
#
# Generate random points within the volume of a mesh
#
# Point testing is done by projecting the point in the positive X direction;
#    if the first collision is with the inside of the mesh, the point is considered to be inside
#
# To load:
#   To load, Either:
#        paste into blender's inbuilt text editor, which has a menu option for "run script", which you need to do.
#   Or type into blender python prompt:
#        f='/Users/pi/Dev/blenderAddons/pointcloud.py'; exec(   compile( open(f).read(), f, 'exec' )   )
#
# To use:
#    * With target object selected
#    * in edit mode
#    * with the mouse over the 3-D view
#   Hit SpaceBar
#
#   ...and search for "PointCloud"
#
#   Adjust the number of points in the panel

bl_info = {
    "name": "PointCloud Generator",
    "author": "CoDEmanX, pi",
    "version": (1, 0),
    "blender": (2, 67, 0),
    "location": "View3D > T-panel > Object Tools",
    "description": "Generate random points within the volume of a mesh",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}


import bpy
from mathutils import Vector
from random import uniform
from math import pi

def pt_in_box(O,P):
    return Vector( (
                uniform( O.x, P.x ),
                uniform( O.y, P.y ),
                uniform( O.z, P.z )
            ) )

def main(context, num):
    max_attempts = 999

    context.scene.update()

    ob = context.object

    mat = ob.matrix_world.copy()
    mat.col[3][:3] = [0] * 3 # reset translation

    bbox = [Vector(b) for b in ob.bound_box]

    O = bbox[0]
    W = bbox[6]

    X = Vector( ( W.x - O.x, 0.0, 0.0 ) )
    #Y = Vector( ( 0.0, W.y - O.y, 0.0 ) )
    #Z = Vector( ( 0.0, 0.0, W.z - O.z ) )

    me = bpy.data.meshes.new("pointcloud")
    me.vertices.add(num)

    for v in me.vertices:
        got = False

        for i in range(1,max_attempts):
            A = pt_in_box( O, W )
            #print(type(A))
            my_x = ob.ray_cast(A, A+X)
            print("obj: {0}\tLen: {1}".format(my_x, len(my_x)))
            my_x = my_x[1:4]
            print("obj: {0}\tLen: {1}".format(my_x, len(my_x)))
            (location, normal, index) = ob.ray_cast(A, A+X)[1:4]

            # don't need X.angle(hit.normal), woot!
            if index > -1  and  normal.x > 0.0 :
                got = True
                break

        if not got:
            print( "PtCloud Failed" )
            return

        v.co = A

    me.transform(mat)

    ob_new = bpy.data.objects.new("pointcloud", me)
    ob_new.location = ob.matrix_world.translation
    ob_new.show_x_ray = True
    bpy.context.scene.objects.link(ob_new)
    bpy.context.scene.update()

class PointCloudGenerator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.pointcloud"
    bl_label = "PointCloud"
    bl_options = {'REGISTER', 'UNDO'}

    amount = bpy.props.IntProperty(name="Points",
        description="Number of random points to generate",
        default=100,
        min=1, max=25000
        )

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        main(context, self.amount)
        return {'FINISHED'}


def draw_func(self, context):
    layout = self.layout
    layout.operator(PointCloudGenerator.bl_idname)

def register():
    bpy.utils.register_class(PointCloudGenerator)
    bpy.types.VIEW3D_PT_tools_object.prepend(draw_func)
    print("Registered")

def unregister():
    bpy.utils.unregister_class(PointCloudGenerator)
    bpy.types.VIEW3D_PT_tools_objectmode.remove(draw_func)


if __name__ == "__main__":
    register()