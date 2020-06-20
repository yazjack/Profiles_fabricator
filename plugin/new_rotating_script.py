bl_info = {
	"name": "Organize Parts",
	"category": "Object",
	}

import bpy, bmesh
from math import pi
from bpy.types import (
	Panel, 
	Operator,
	AddonPreferences,
	PropertyGroup
	)
class OrganizeParts(Operator):
	bl_idname = "organize.parts"
	bl_label = "Organize Parts"
	bl_options = {'REGISTER', 'UNDO'}
		
	def execute(self, context):
		def cleaner():
			bpy.ops.object.select_all(action='DESELECT')
			bpy.ops.object.select_by_type(type='FONT')
			bpy.ops.object.select_pattern(pattern="Frame*")
			bpy.ops.object.delete()
			bpy.ops.object.select_all(action='SELECT')
			bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
			bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
			bpy.ops.object.select_all(action='DESELECT')
			open('rotator_output.txt', 'w').close()
			print("", file=open("rotator_output.txt", "a"))
			print("BILL OF PARTS", file=open("rotator_output.txt", "a"))
			print("", file=open("rotator_output.txt", "a"))
			
		def rotate_along_x():      
			for o in bpy.context.visible_objects:
				bpy.context.scene.objects.active = o
				o.select = True
				bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
				x, y, z = o.dimensions
				while x<z or x<y:
					if z>x:
						o.rotation_euler = (0, (pi*90/180), 0)
						bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
					if y>x:
						o.rotation_euler = (0, 0, (pi*90/180))
						bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
					if z>y:
						o.rotation_euler = ((pi*90/180), 0, 0)
						bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
					x, y, z = o.dimensions
				if x>y and x>z and y>z:
					x, y, z = o.dimensions
					o.name = str(round(o.dimensions[0]*100, 1))
				o.select = False

		def placer(sorted_list):
			previous_y_location = 0
			previous_y_size = 0
			for o in sorted_list:
				bpy.context.scene.objects.active = o
				o.location.x = -o.dimensions[0]/2
				o.location.y = previous_y_location + previous_y_size/2 + o.dimensions[1]/2+ 0.02
				o.location.z = 0
				previous_y_location = o.location.y
				previous_y_size = o.dimensions[1]
				
		def sorted_objects():
			sorted_objects_list = [obj for obj in bpy.context.visible_objects]
			sorted_objects_list.sort(key=lambda srt: (srt.dimensions[0], srt.dimensions[1]))
			return sorted_objects_list

		def add_text_obj(obj, prev_l, prev_w, prev_h, counter, tot_len, is_it_last, y_loc):
			global tex
			curr_l = round(obj.dimensions[0]*100, 2)
			curr_w = round(obj.dimensions[1]*100, 2)
			curr_h = round(obj.dimensions[2]*100, 2)
			bpy.ops.object.text_add()
			tex = bpy.context.object
			tex.scale = 2*obj.dimensions[1], 2*obj.dimensions[1], 2*obj.dimensions[1]
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			tex.location.x = 0.1
			
			def castrate(n):
				nint = int(n)
				nfloat = round(n, 2)
				if nint/n == 1:
					n = int(n)
				else:
					n = nfloat
				return n
			
			curr_l = castrate(curr_l)
			curr_w = castrate(curr_w)
			curr_h = castrate(curr_h)
			prev_l = castrate(prev_l)
			prev_w = castrate(prev_w)
			prev_h = castrate(prev_h)
				
			if is_it_last == 0:
				tex.location.y = y_loc - 0.5*obj.dimensions[1]
				tex.data.body = str(counter) + " pcs of " + str(prev_l) + "x" + str(prev_w) + "x" + str(prev_h) + "cm"
				print(str(counter) + " pcs of " + str(prev_l) + "x" + str(prev_w) + "x" + str(prev_h) + " cm", file=open("rotator_output.txt", "a"))
			else:
				tex.location.y = y_loc - 0.5*obj.dimensions[1]
				tex.data.body = str(counter) + " pcs of " + str(curr_l) + "x" + str(curr_w) + "x"+ str(curr_h) + "cm"
				print(str(counter) + " pcs of " + str(curr_l) + "x" + str(curr_w) + "x"+ str(curr_h) + " cm", file=open("rotator_output.txt", "a"))
				print("", file=open("rotator_output.txt", "a"))
				print(str(round(tot_len)/100) + " running meters of material", file=open("rotator_output.txt", "a"))
				
			bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

		def add_tags(sorted_list):
			running_length = 0
			parts_counter = 0
			offset_counter = 0
			for i, o in enumerate(sorted_list):
				bpy.context.scene.objects.active = o
				o.select = True
				
				current_length = round(o.dimensions[0]*100, 1)
				currnet_width = round(o.dimensions[1]*100, 1)
				current_height = round(o.dimensions[2]*100, 1)
				running_length = running_length + current_length
				
				if i == 0:
					previous_length = round(o.dimensions[0]*100, 2)
					previous_width = round(o.dimensions[1]*100, 2)
					previous_height = round(o.dimensions[2]*100, 2)
					frame_from = o.location[1]
				
				if currnet_width > previous_width and current_length == previous_length:
					last = 0
					frame_to = o.location[1] - previous_width/100*2.5
					draw_frame(frame_from, frame_to)
					add_text_obj(o, previous_length, previous_width, previous_height, parts_counter, running_length,last, frame_y)
					parts_counter = 0
					frame_from = frame_to + currnet_width/100  
				   
				if current_length > previous_length:
					last = 0
					frame_to = o.location[1] - currnet_width/100*2
					draw_frame(frame_from, frame_to)
					add_text_obj(o, previous_length, previous_width, previous_height, parts_counter, running_length,last, frame_y)
					parts_counter = 0
					frame_from = frame_to + o.dimensions[1]*2

				parts_counter += 1
				previous_length = current_length
				previous_width = currnet_width
				previous_height = current_height
				
				if i == len(sorted_list) - 1:
					last = 1
					frame_to = o.location[1] + o.dimensions[1]*0.25
					draw_frame(frame_from, frame_to)		 
					add_text_obj(o, previous_length, previous_width, previous_height, parts_counter, running_length, last, frame_y)

				offset_counter += 1
				o.select = False
				
		def draw_frame(from_vetex, to_vetex):
			global frame_y
			mesh = bpy.data.meshes.new("mesh")
			obj = bpy.data.objects.new("Frame", mesh)
			scene = bpy.context.scene
			scene.objects.link(obj)
			scene.objects.active = obj
			obj.select = True 

			mesh = bpy.context.object.data
			bm = bmesh.new()

			vert_1 = bm.verts.new((0.01, from_vetex, 0))
			vert_2 = bm.verts.new((0.08, from_vetex, 0))
			vert_3 = bm.verts.new((0.08, to_vetex, 0))
			vert_4 = bm.verts.new((0.01, to_vetex, 0))
			
			bm.edges.new((vert_1, vert_2))
			bm.edges.new((vert_2, vert_3))
			bm.edges.new((vert_3, vert_4))

			bm.to_mesh(mesh)  
			bm.free()
			bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
			frame_y = obj.location[1]
			return frame_y

		def run_all():
			cleaner()
			rotate_along_x()
			cleaner()
			placer(sorted_objects())
			add_tags(sorted_objects())
			
		run_all()
		return {'FINISHED'}
	
def menu_func(self, context):
	self.layout.operator('OrganizeParts.bl_idname')
	
def register():
	bpy.utils.register_class(OrganizeParts)
	bpy.types.VIEW3D_MT_object.append(menu_func)
	
def unregister():
	bpy.utils.unregister_class(OrganizeParts)
	bpy.types.VIEW3D_MT_object.remove(menu_func)
	
if __name__ == '__main__':
	register()