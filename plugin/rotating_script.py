#Script developed as an aid to steel profile constuructions manufacturing process
#Script does following to **visible** objects:
#   * rotates them along X axis, no matter the true orientation
#   * changes the names to their X dimmension
#   * sorts them by X dimmension and places along Y axis with defined spacing

import bpy
from math import pi

offset_counter = 0
offset_value = 0.03 #how much the objects are getting spaced

#Clean up some things that might intrfere with script execution
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='FONT')
bpy.ops.object.delete()

for visible in bpy.context.visible_objects:
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')


def main():
    global offset_counter
    parts_counter = 0

    previous_length = 0
    previous_width = 0
    previous_height = 0
    running_length = 0
    
    #Create output file and clear the contents
    open('rotator_output.txt', 'w').close()

    #create new collection from visible objects
    sorted_objects = [obj for obj in bpy.context.visible_objects]
    #sort the contents based on x length
    sorted_objects.sort(key=lambda srt: srt.dimensions[0])
    
    print("====BILL OF PARTS====", file=open("rotator_output.txt", "a"))

    #this is main loop so to speak, this is where the magic happens
    for i, o in enumerate(sorted_objects):
        bpy.context.scene.objects.active = o
        o.select = True
        rotationator()
        current_length = round(o.dimensions[0]*100, 1)
        running_length = running_length + current_length
        pr_y = int(round(o.dimensions[1]*100, 0))
        pr_z = int(round(o.dimensions[2]*100, 0))
        placeinator()

        #get the length of the shortest piece
        if i == 0:
            shortest_piece = o.dimensions[0]
            previous_length = round(shortest_piece*100, 1)
            
        #this will add a name tag in the scene if length changes, also write ammount of pieces of the same length to file
        if current_length > previous_length:
            bpy.ops.object.text_add()
            tex = bpy.context.object
            tex.scale = 0.07, 0.07, 0.07
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            tex.location.x = 0.1
            tex.location.y = o.location.y - tex.dimensions[1]
            tex.data.body = str(parts_counter) + "pcs of " + str(previous_length) + "cm"
            print(str(parts_counter) + "pcs of " + str(pr_y) + "x" + str(pr_z) + "x" + str(previous_length) + " cm", file=open("rotator_output.txt", "a"))
            parts_counter = 0

        parts_counter += 1
        previous_length = current_length
        
        #this will add a tag and file entry for the last object, also write total length of needed material
        if i == len(sorted_objects) - 1:    
            bpy.ops.object.text_add()
            tex = bpy.context.object
            tex.scale = 0.07, 0.07, 0.07
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            tex.location.x = 0.1
            tex.location.y = o.location.y + tex.dimensions[1]
            tex.data.body = str(parts_counter) + "pcs of " + str(current_length) + "cm"
            print(str(parts_counter) + "pcs of " + str(pr_z) + "x" + str(pr_y) + "x" + str(current_length) + " cm", file=open("rotator_output.txt", "a"))
            print("", file=open("rotator_output.txt", "a"))
            print(str(running_length/100) + " running meters of material", file=open("rotator_output.txt", "a"))

        offset_counter += 1
        o.select = False

#function that will apply transforms, fix origins, rotate objects and name them
def rotationator():
    o = bpy.context.active_object
    x, y, z = o.dimensions #write XYZ dimensions to variables

    if z>x:
        x, y, z = o.dimensions
        o.rotation_euler = (0, (pi*90/180), 0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    if y>x:
        x, y, z = o.dimensions
        o.rotation_euler = (0, 0, (pi*90/180))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        
    #now that it's oriented, we can name it
    o.name = str(round(o.dimensions[0]*100, 1)) #name it with previously aquired value

#function to place rotated object along Y axis. It also offsets X location by half length, so the object starts at X zero
def placeinator():
    o = bpy.context.active_object
    x_length = o.dimensions[0] #get length for X offset
    y_length = o.dimensions[1] #get the width for Y offset
    o.location.x = -x_length/2  #move it to the begining of the X axis
    o.location.y = offset_value*offset_counter+y_length #place it in offseted Y location
    o.location.z = 0 #set Z location to zero
    print(str(offset_counter))
    
main()