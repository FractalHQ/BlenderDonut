from mathutils import Vector
from mathutils.geometry import distance_point_to_plane
import bpy
import bmesh

# Aliases

D = bpy.data
C = bpy.context

# Helper functions


# In- and out- sockets are assumed to be lists of dictionaries, where the key is the parameter
# and the value is the argument. The 'get' function supplies a default if the key is not
# included in the list. See https://docs.blender.org/api/current/bpy.types.NodeSocketShader.html
# for list of available data types that can be represented in nodes.
def append_group_node(data=bpy.data, name='GroupNode', use_fake_user=False, in_sockets=[], out_sockets=[]):

    # Create group.
    group = data.node_groups.new(name, 'ShaderNodeTree')

    # Create input and output nodes within group.
    group.nodes.new('NodeGroupInput')
    group.nodes.new('NodeGroupOutput')

    # If the group has a fake user, then it will be retained in memory after all other
    # instances that use it are removed.
    group.use_fake_user = use_fake_user

    # Inputs
    inputs = group.inputs

    # Loop through list.
    for in_socket in in_sockets:

        # Create new input.
        curr = inputs.new(in_socket.get(
            'data_type', 'NodeSocketFloat'), in_socket.get('name', 'Value'))

        # Assign default value.
        if curr.bl_socket_idname == 'NodeSocketFloat':
            curr.default_value = in_socket.get('default_value', 0.0)

        # Default vector value is 1.0 / sqrt(3.0), where vector has magnitude of 1.0.
        elif curr.bl_socket_idname == 'NodeSocketVector':
            curr.default_value = in_socket.get(
                'default_value', (0.57735, 0.57735, 0.57735))

        # Colors include alpha/transparency as the fourth component.
        elif curr.bl_socket_idname == 'NodeSocketColor':
            curr.default_value = in_socket.get(
                'default_value', (0.0, 0.0, 0.0, 0.0))

        # Assign min and max values to nodes which contain them.
        if curr.bl_socket_idname == 'NodeSocketFloat' or curr.bl_socket_idname == 'NodeSocketVector':
            curr.min_value = in_socket.get('min_value', -10000.0)
            curr.max_value = in_socket.get('max_value', 10000.0)

    # Outputs.
    outputs = group.outputs

    # Loop through list.
    for out_socket in out_sockets:

        # Create new output.
        curr = outputs.new(out_socket.get(
            'data_type', 'NodeSocketFloat'), out_socket.get('name', 'Value'))

        # Assign default value.
        if curr.bl_socket_idname == 'NodeSocketFloat':
            curr.default_value = out_socket.get('default_value', 0.0)
        elif curr.bl_socket_idname == 'NodeSocketVector':
            curr.default_value = out_socket.get(
                'default_value', (0.57735, 0.57735, 0.57735))
        elif curr.bl_socket_idname == 'NodeSocketColor':
            curr.default_value = out_socket.get(
                'default_value', (0.0, 0.0, 0.0, 0.0))

        # Assign min and max values to nodes which contain them.
        if curr.bl_socket_idname == 'NodeSocketFloat' or curr.bl_socket_idname == 'NodeSocketVector':
            curr.min_value = out_socket.get('min_value', -10000.0)
            curr.max_value = out_socket.get('max_value', 10000.0)

    return group


def select(str):
    obj = D.objects[str]
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def delete(str):
    select(str)
    bpy.ops.object.delete(use_global=False)


def popup(message, title='', icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def RIP():
    try:
        select("Cube")
        delete("Cube")
    except:
        print('Default Cube already yeeted')


RIP()

#! Remove all materials
for material in bpy.data.materials:
    material.user_clear()
    bpy.data.materials.remove(material)

#! Remove All Objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ?
# ? Donut
# ?


# * Create Torus

bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(0, 0, 0), rotation=(
    0, 0, 0), major_segments=28, major_radius=0.05, minor_radius=0.026)
bpy.ops.object.shade_smooth()

# Save Torus to variable
Donut = C.object


# * Add Subdivision Modifier

bpy.ops.object.modifier_add(type='SUBSURF')
bpy.context.object.modifiers["Subdivision"].levels = 2
bpy.context.object.modifiers["Subdivision"].render_levels = 2


# * Duplicate mesh

bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'}, TRANSFORM_OT_translate={"value": (0, 0, 0), "orient_axis_ortho": 'X', "orient_type": 'GLOBAL', "orient_matrix": ((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type": 'GLOBAL', "constraint_axis": (False, False, False), "mirror": False, "use_proportional_edit": False, "proportional_edit_falloff": 'SMOOTH', "proportional_size": 1,
                                                                                                                    "use_proportional_connected": False, "use_proportional_projected": False, "snap": False, "snap_target": 'CLOSEST', "snap_point": (0, 0, 0), "snap_align": False, "snap_normal": (0, 0, 0), "gpencil_strokes": False, "cursor_transform": False, "texture_space": False, "remove_on_cancel": False, "view2d_edge_pan": False, "release_confirm": False, "use_accurate": False, "use_automerge_and_split": False})


# * store new mesh as icing

Icing = C.object


# * Delete bottom half of icing

def deleteBottomHalf():
    bpy.ops.object.editmode_toggle()

    context = bpy.context

    def bbox(ob):
        return (Vector(b) for b in ob.bound_box)

    def bbox_center(ob):
        return sum(bbox(ob), Vector()) / 8

    def bbox_axes(ob):
        bb = list(bbox(ob))
        return tuple(bb[i] - bb[0] for i in (4, 3, 1))

    o = bbox_center(Icing)
    x, y, z = bbox_axes(Icing)

    bm = bmesh.from_edit_mesh(Icing.data)
    for v in bm.verts:
        v.select = distance_point_to_plane(v.co, o, z) >= 0.01

    bmesh.update_edit_mesh(Icing.data)

    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.object.editmode_toggle()
deleteBottomHalf()

# ?
# ?	Modifiers
# ?

# * Multires

bpy.ops.object.modifier_add(type='MULTIRES')
bpy.ops.object.multires_subdivide(modifier="Multires", mode='CATMULL_CLARK')


# * Screw
def icingScrew():
    bpy.ops.object.modifier_add(type='SCREW')
    bpy.ops.object.modifier_move_to_index(modifier="Screw", index=1)
    bpy.context.object.modifiers["Screw"].steps = 1
    bpy.context.object.modifiers["Screw"].axis = 'Y'
    bpy.context.object.modifiers["Screw"].screw_offset = 0.01
    bpy.context.object.modifiers["Screw"].use_smooth_shade = True
    bpy.context.object.modifiers["Screw"].use_normal_calculate = False
    # bpy.context.object.modifiers["Screw"].use_normal_flip = True
    bpy.context.object.modifiers["Screw"].use_merge_vertices = True
    bpy.context.object.modifiers["Screw"].render_steps = 1
icingScrew()

# * Solidify


def icingSolidify():
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    bpy.context.object.modifiers["Solidify"].thickness = -0.001
    bpy.context.object.modifiers["Solidify"].use_rim = False
    bpy.context.object.modifiers["Solidify"].use_even_offset = True
    bpy.context.object.modifiers["Solidify"].offset = -0.904306
icingSolidify()


# * Remesh

def icingRemesh():
    bpy.ops.object.modifier_add(type='REMESH')
    bpy.context.object.modifiers["Remesh"].mode = 'SMOOTH'
    bpy.context.object.modifiers["Remesh"].octree_depth = 5
    bpy.context.object.modifiers["Remesh"].scale = 0.887
    bpy.context.object.modifiers["Remesh"].use_smooth_shade = True
icingRemesh()


# * Move Subdivision to index
bpy.ops.object.modifier_move_to_index(modifier="Subdivision", index=4)


# * Shrinkwrap

def icingShrinkwrap():
    bpy.ops.object.modifier_add(type='SHRINKWRAP')
    bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'ABOVE_SURFACE'
    bpy.context.object.modifiers["Shrinkwrap"].offset = 0.0005
    bpy.context.object.modifiers["Shrinkwrap"].target = Donut
icingShrinkwrap()

# * Wave


def icingWave():
    bpy.ops.object.modifier_add(type='WAVE')
    bpy.context.object.modifiers["Wave"].use_normal = True
    bpy.context.object.modifiers["Wave"].height = 0.1
    bpy.context.object.modifiers["Wave"].width = 0.56
    bpy.context.object.modifiers["Wave"].narrowness = 0.2
icingWave()

# * Smooth


def icingSmooth():
    bpy.ops.object.modifier_add(type='SMOOTH')
    bpy.context.object.modifiers["Smooth"].factor = 1.756
    bpy.context.object.modifiers["Smooth"].iterations = 3
icingSmooth()

# ?
# ? Look and Feel
# ?

# * Icing Material


def icingMaterial():
    # Create new material
    icingMaterial = bpy.data.materials.new(name="IcingMaterial")
    # Add to Icing
    Icing.data.materials.append(icingMaterial)
    # Use Nodes
    icingMaterial.use_nodes = True
    # Store Principled BSDF node
    icingShader = bpy.data.materials["IcingMaterial"].node_tree.nodes["Principled BSDF"]
    # Base Color
    icingShader.inputs[0].default_value = (0.8, 0.013, 0.707, 1)
    # Subsurface
    icingShader.inputs[1].default_value = 0.15
    # Subsurface Radius
    icingShader.inputs[2].default_value[0] = 0.2
    icingShader.inputs[2].default_value[1] = 0.5
    icingShader.inputs[2].default_value[2] = 0.1
    # Subsurface Color
    icingShader.inputs[3].default_value = (0.66, 0.50, 0.8, 1)
    # Clearcoat
    icingShader.inputs[14].default_value = 0.2
    # Clearcoat Rougness
    icingShader.inputs[15].default_value = 0.13
    # Transmission
    icingShader.inputs[18].default_value = 0.38
    # Transmission Roughness
    icingShader.inputs[17].default_value = 0.17
icingMaterial()


# * Camera
# bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(1.63363, 4.13058e-07, -1.38929), scale=(1, 1, 1))
