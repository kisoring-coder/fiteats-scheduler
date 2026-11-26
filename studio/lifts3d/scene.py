"""Build the 3D x-ray lifter scene (Xbot, Mixamo rig) with IK, barbell, muscle masks and a camera."""
import bpy, math, json, sys
from mathutils import Vector, Matrix, Euler

P = "mixamorig:"
MUSCLES = ["quads", "hamstrings", "innerthigh", "glutes", "calves", "core", "chest", "lowerback", "lats", "upperback",
           "traps", "shoulders", "triceps", "biceps", "forearms", "grip"]
LIME = (0.79, 0.93, 0.29, 1)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath="/home/claude/assets3d/Xbot.glb")
    for o in list(bpy.data.objects):
        if o.name == "Icosphere": bpy.data.objects.remove(o)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.animation_data.action = None
    fix_bones(arm)
    for a in list(bpy.data.actions): bpy.data.actions.remove(a)
    for pb in arm.pose.bones: pb.matrix_basis = Matrix.Identity(4); pb.rotation_mode = 'XYZ'
    bpy.context.view_layer.update()
    return arm

CHAIN = {"Hips": "Spine", "Spine": "Spine1", "Spine1": "Spine2", "Spine2": "Neck", "Neck": "Head", "Head": "HeadTop_End"}
for s_ in ("Left", "Right"):
    CHAIN.update({s_ + "UpLeg": s_ + "Leg", s_ + "Leg": s_ + "Foot", s_ + "Foot": s_ + "ToeBase", s_ + "ToeBase": s_ + "Toe_End",
                  s_ + "Shoulder": s_ + "Arm", s_ + "Arm": s_ + "ForeArm", s_ + "ForeArm": s_ + "Hand", s_ + "Hand": s_ + "HandMiddle1"})
    for f in ("Thumb", "Index", "Middle", "Ring", "Pinky"):
        for i in (1, 2, 3): CHAIN[f"{s_}Hand{f}{i}"] = f"{s_}Hand{f}{i+1}"

def fix_bones(arm):
    """glTF import gives bogus bone lengths; point each bone at its child so IK works."""
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    for b in eb:
        n = b.name.replace(P, "")
        if n in CHAIN and (P + CHAIN[n]) in eb:
            b.tail = eb[P + CHAIN[n]].head.copy()
        else:
            d = (b.tail - b.head); 
            if d.length > 0: b.tail = b.head + d.normalized() * 5.0
        if "Hand" in n and n not in ("LeftHand", "RightHand"): continue
        b.align_roll(Vector((0, -1, 0)) if "Foot" not in n and "Toe" not in n else Vector((0, 0, 1)))
    bpy.ops.object.mode_set(mode='OBJECT')

# ------------------------------------------------------------ muscle masks (rest pose, T-pose)
def build_masks(arm):
    sc = bpy.context.scene
    for mname in ("Beta_Surface", "Beta_Joints"):
        m = bpy.data.objects[mname]; me = m.data
        gi = {g.index: g.name.replace(P, "") for g in m.vertex_groups}
        me.calc_loop_triangles()
        attrs = {k: me.attributes.new("m_" + k, 'FLOAT', 'POINT') for k in MUSCLES}
        hip_z = 1.0
        for v in me.vertices:
            w = {}
            for g in v.groups: w[gi[g.group]] = w.get(gi[g.group], 0) + g.weight
            def W(*names): return sum(w.get(n, 0) + w.get("Left" + n, 0) + w.get("Right" + n, 0) for n in names)
            co = v.co * 0.01; n = v.normal; side = 1 if co.x > 0 else -1
            front = -n.y; back = n.y; inward = -n.x * side
            val = {k: 0.0 for k in MUSCLES}
            up = W("UpLeg"); lg = W("Leg"); arm_ = W("Arm"); fa = W("ForeArm"); hd = W("Hand") + sum(v_ for k_, v_ in w.items() if "Hand" in k_ and k_ not in ("LeftHand", "RightHand"))
            sp = W("Spine"); sp1 = W("Spine1"); sp2 = W("Spine2"); hips = W("Hips"); sh = W("Shoulder"); nk = W("Neck")
            if up > 0.4:
                if front > 0.15: val["quads"] = min(1, up)
                if back > 0.2 and co.z < 0.86: val["hamstrings"] = min(1, up)
                if inward > 0.45 and co.z > 0.62: val["innerthigh"] = min(1, up)
            if (hips + up) > 0.4 and back > 0.25 and 0.78 < co.z < 1.02: val["glutes"] = 1.0
            if lg > 0.4 and back > 0.1 and co.z > 0.2: val["calves"] = min(1, lg)
            if (sp + sp1 + hips + sp2) > 0.4 and front > -0.05 and 0.96 < co.z < 1.25 and abs(co.x) < 0.15: val["core"] = 1.0
            if (sp2 + sp1) > 0.4 and front > 0.3 and 1.25 < co.z < 1.42 and abs(co.x) < 0.17: val["chest"] = 1.0
            if (sp + hips + sp1) > 0.4 and back > 0.3 and 1.0 < co.z < 1.2: val["lowerback"] = 1.0
            if (sp1 + sp2) > 0.3 and abs(n.x) > 0.35 and n.y > -0.2 and 1.12 < co.z < 1.36: val["lats"] = 1.0
            if (sp2 + sh) > 0.4 and back > 0.35 and 1.22 < co.z < 1.42: val["upperback"] = 1.0
            if (nk + sh + sp2) > 0.3 and (n.z > 0.45 or (back > 0.4 and co.z > 1.4)) and co.z > 1.36 and abs(co.x) < 0.2: val["traps"] = 1.0
            if (arm_ > 0.3 or sh > 0.4) and 0.12 < abs(co.x) < 0.33 and co.z > 1.3: val["shoulders"] = 1.0
            if arm_ > 0.5 and abs(co.x) >= 0.3:
                if n.y > 0.2 or n.z < -0.55: val["triceps"] = min(1, arm_)
                if n.y < -0.25 or n.z > 0.55: val["biceps"] = min(1, arm_)
            if fa > 0.5: val["forearms"] = min(1, fa)
            if hd > 0.5: val["grip"] = 1.0
            for k in MUSCLES: attrs[k].data[v.index].value = val[k]

# ------------------------------------------------------------ materials
def xray_material(name, strength=1.0, muscles=True):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nt = mat.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.006, 0.007, 0.009, 1)
    ramp.color_ramp.elements[1].position = 1.0; ramp.color_ramp.elements[1].color = (0.82, 0.86, 0.95, 1)
    e = ramp.color_ramp.elements.new(0.72); e.color = (0.03, 0.034, 0.042, 1)
    e2 = ramp.color_ramp.elements.new(0.9); e2.color = (0.28, 0.3, 0.36, 1)
    L.new(lw.outputs["Facing"], ramp.inputs["Fac"])
    wf = N.new("ShaderNodeWireframe"); wf.use_pixel_size = True; wf.inputs["Size"].default_value = 1.0
    wfm = N.new("ShaderNodeMath"); wfm.operation = 'MULTIPLY'; wfm.inputs[1].default_value = 0.035
    L.new(wf.outputs[0], wfm.inputs[0])
    addc = N.new("ShaderNodeMix"); addc.data_type = 'RGBA'; addc.blend_type = 'ADD'; addc.inputs[0].default_value = 1.0
    L.new(ramp.outputs["Color"], addc.inputs[6]); L.new(wfm.outputs[0], addc.inputs[7])
    base = N.new("ShaderNodeEmission"); base.inputs["Strength"].default_value = strength
    L.new(addc.outputs[2], base.inputs["Color"])
    if not muscles:
        L.new(base.outputs[0], out.inputs[0]); return mat
    # muscle mask = max(attr_i * value_i)
    acc = None
    for k in MUSCLES:
        at = N.new("ShaderNodeAttribute"); at.attribute_name = "m_" + k; at.attribute_type = 'GEOMETRY'
        vn = N.new("ShaderNodeValue"); vn.name = "V_" + k; vn.label = "V_" + k; vn.outputs[0].default_value = 0.0
        mu = N.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'
        L.new(at.outputs["Fac"], mu.inputs[0]); L.new(vn.outputs[0], mu.inputs[1])
        if acc is None: acc = mu
        else:
            mx = N.new("ShaderNodeMath"); mx.operation = 'MAXIMUM'
            L.new(acc.outputs[0], mx.inputs[0]); L.new(mu.outputs[0], mx.inputs[1]); acc = mx
    # fibre texture inside lit muscles
    wave = N.new("ShaderNodeTexWave"); wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
    wave.inputs["Scale"].default_value = 26.0; wave.inputs["Distortion"].default_value = 2.0
    tc = N.new("ShaderNodeTexCoord"); L.new(tc.outputs["Object"], wave.inputs["Vector"])
    fib = N.new("ShaderNodeMapRange"); fib.inputs["To Min"].default_value = 0.55; fib.inputs["To Max"].default_value = 1.0
    L.new(wave.outputs["Fac"], fib.inputs["Value"])
    rim = N.new("ShaderNodeMapRange"); rim.inputs["To Min"].default_value = 0.45; rim.inputs["To Max"].default_value = 1.5
    L.new(lw.outputs["Facing"], rim.inputs["Value"])
    s1 = N.new("ShaderNodeMath"); s1.operation = 'MULTIPLY'; L.new(fib.outputs[0], s1.inputs[0]); L.new(rim.outputs[0], s1.inputs[1])
    lime = N.new("ShaderNodeEmission"); lime.inputs["Color"].default_value = LIME
    L.new(s1.outputs[0], lime.inputs["Strength"])
    mix = N.new("ShaderNodeMixShader")
    L.new(acc.outputs[0], mix.inputs[0]); L.new(base.outputs[0], mix.inputs[1]); L.new(lime.outputs[0], mix.inputs[2])
    tr = N.new("ShaderNodeBsdfTransparent")
    al = N.new("ShaderNodeMapRange"); al.inputs["To Min"].default_value = 0.5; al.inputs["To Max"].default_value = 0.92
    L.new(acc.outputs[0], al.inputs["Value"])
    mx2 = N.new("ShaderNodeMixShader"); L.new(al.outputs[0], mx2.inputs[0]); L.new(tr.outputs[0], mx2.inputs[1]); L.new(mix.outputs[0], mx2.inputs[2])
    L.new(mx2.outputs[0], out.inputs[0])
    return mat

def line_material(name, col=(0.82, 0.86, 0.95, 1), dark=(0.01, 0.011, 0.014, 1)):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nt = mat.node_tree; N = nt.nodes; L = nt.links; N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.3
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = dark; ramp.color_ramp.elements[1].color = col
    ramp.color_ramp.elements[0].position = 0.55
    L.new(lw.outputs["Facing"], ramp.inputs["Fac"])
    wf = N.new("ShaderNodeWireframe"); wf.use_pixel_size = True; wf.inputs["Size"].default_value = 1.0
    mx = N.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'ADD'
    wm = N.new("ShaderNodeMath"); wm.operation = 'MULTIPLY'; wm.inputs[1].default_value = 0.25
    L.new(wf.outputs[0], wm.inputs[0]); L.new(wm.outputs[0], mx.inputs[0])
    L.new(ramp.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = col
    em = N.new("ShaderNodeEmission"); L.new(mx.outputs[2], em.inputs["Color"])
    L.new(em.outputs[0], out.inputs[0]); return mat

# ------------------------------------------------------------ props
def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    e.location = loc; e.empty_display_size = 0.05
    if parent: e.parent = parent
    return e

def barbell():
    bar = empty("BAR", (0, -0.09, 0.225))
    mat = line_material("bar_mat")
    objs = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.014, depth=2.2, rotation=(0, math.pi / 2, 0)); objs.append(bpy.context.object)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.225, depth=0.05, location=(sx * 0.82, 0, 0), rotation=(0, math.pi / 2, 0)); objs.append(bpy.context.object)
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.16, depth=0.03, location=(sx * 0.875, 0, 0), rotation=(0, math.pi / 2, 0)); objs.append(bpy.context.object)
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.03, depth=0.05, location=(sx * 0.77, 0, 0), rotation=(0, math.pi / 2, 0)); objs.append(bpy.context.object)
    for o in objs:
        o.data.materials.append(mat); o.parent = bar
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.shade_smooth()
    floor_mat = line_material("floor_mat", col=(0.25, 0.27, 0.32, 1))
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, -0.002)); fl = bpy.context.object
    fl.scale = (3.4, 1.6, 1); fl.data.materials.append(floor_mat)
    bpy.ops.object.modifier_add(type='WIREFRAME'); fl.modifiers[-1].thickness = 0.004
    bpy.ops.object.modifier_add(type='ARRAY')
    return bar, objs, fl

# ------------------------------------------------------------ IK rig
def rig(arm, bar):
    """No Blender IK (its solver folds badly): limbs are solved analytically each frame in poses.py.
    Store rest world rotations for feet and curl the fingers into a grip."""
    pb = arm.pose.bones
    bpy.context.view_layer.update()
    rest = {}
    for s in ("Left", "Right"):
        for n in ("Foot", "ToeBase"):
            rest[s + n] = (arm.matrix_world @ pb[P + s + n].matrix).to_quaternion()
    for b in pb:
        n = b.name.replace(P, "")
        if "Hand" in n and n[-1] in "123" and "Thumb" not in n:
            b.rotation_euler = Euler((math.radians(70), 0, 0))
        if "Thumb" in n and n[-1] in "23":
            b.rotation_euler = Euler((math.radians(25), 0, 0))
    return rest

def camera(sc):
    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.lens = 50; cam.sensor_fit = 'VERTICAL'; cam.sensor_height = 24
    tgt = empty("camtarget", (0, 0, 0.98))
    c = co.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return co, tgt

def setup_render(sc, w=1080, h=1350, samples=6):
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples
    sc.cycles.use_denoising = False; sc.cycles.max_bounces = 0; sc.cycles.diffuse_bounces = 0; sc.cycles.glossy_bounces = 0
    sc.cycles.transmission_bounces = 0; sc.cycles.transparent_max_bounces = 6
    sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.film_transparent = True
    sc.render.fps = 30; sc.render.use_persistent_data = True
    sc.view_settings.view_transform = 'Standard'
    w_ = bpy.data.worlds.new("w"); sc.world = w_; w_.color = (0, 0, 0)

def build():
    arm = reset(); sc = bpy.context.scene
    build_masks(arm)
    body = xray_material("xray_body"); joints = xray_material("xray_joints", 0.8)
    for mname, mat in (("Beta_Surface", body), ("Beta_Joints", joints)):
        o = bpy.data.objects[mname]; o.data.materials.clear(); o.data.materials.append(mat)
    bar, bar_objs, floor = barbell()
    tg = rig(arm, bar)
    cam, ctgt = camera(sc)
    setup_render(sc)
    return dict(arm=arm, bar=bar, bar_objs=bar_objs, tg=tg, cam=cam, ctgt=ctgt, body=body, joints=joints, floor=floor)
