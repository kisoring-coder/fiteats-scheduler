"""Pose keyframes for the 4 movements and a helper that applies a pose (and keys it)."""
import bpy, math
from mathutils import Euler, Vector, Matrix

P = "mixamorig:"

def _ik2(R, T, a, b, pole):
    D = T - R; d = D.length
    u = D.normalized()
    d = max(abs(a - b) + 1e-4, min(d, a + b - 1e-4))
    v = (pole - R); v = (v - u * v.dot(u))
    v = v.normalized() if v.length > 1e-6 else Vector((0, -1, 0))
    cosA = (a * a + d * d - b * b) / (2 * a * d); sinA = math.sqrt(max(0, 1 - cosA * cosA))
    mid = R + u * (a * cosA) + v * (a * sinA)
    end = R + u * d
    return mid, end

def _aim(arm, pb, target_world):
    """Swing a pose bone (no twist) so its head->tail points at target_world."""
    bpy.context.view_layer.update()
    mw = arm.matrix_world; sc = mw.to_scale()[0]
    M = mw @ pb.matrix
    head = M.to_translation(); cur = (mw @ pb.tail) - head
    q = cur.normalized().rotation_difference((target_world - head).normalized())
    R = (mw.to_quaternion().normalized().inverted() @ q @ M.to_quaternion()).to_matrix().to_4x4()
    pb.matrix = Matrix.Translation(pb.matrix.to_translation()) @ R

def _set_world_rot(arm, pb, quat):
    bpy.context.view_layer.update()
    qa = arm.matrix_world.to_quaternion().normalized().inverted()
    pb.matrix = Matrix.Translation(pb.matrix.to_translation()) @ (qa @ quat).to_matrix().to_4x4()

LIMB = ["LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase", "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
        "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand"]

def apply(S, pose, frame=None):
    arm = S["arm"]; pb = arm.pose.bones; mw = arm.matrix_world
    for n in LIMB: pb[P + n].matrix_basis = Matrix.Identity(4)
    arm.location = pose.get("root", (0, 0, 0))
    arm.rotation_mode = 'XYZ'; arm.rotation_euler = Euler((math.radians(pose.get("pitch", 0)), 0, 0))
    pb[P + "Hips"].rotation_euler = Euler((math.radians(pose.get("hinge", 0)), 0, 0))
    for n in ("Spine", "Spine1", "Spine2"):
        pb[P + n].rotation_euler = Euler((math.radians(pose.get("spine", 0)), 0, 0))
    pb[P + "Neck"].rotation_euler = Euler((math.radians(pose.get("neck", 0)), 0, 0))
    pb[P + "Head"].rotation_euler = Euler((math.radians(pose.get("head", 0)), 0, 0))
    for s, sx in (("Left", 1), ("Right", -1)):
        pb[P + s + "Shoulder"].rotation_euler = Euler((0, 0, math.radians(pose.get("shrug", 0) * (-sx))))
        pb[P + s + "Arm"].rotation_euler = Euler((0, 0, 0))
    S["bar"].location = pose.get("bar", (0, -0.09, 0.225))
    bpy.context.view_layer.update()
    g = pose.get("grip", 0.24); bar = Vector(S["bar"].location)
    fx, fy, fz = pose.get("feet", (0.19, -0.06, 0.09))
    for s, sx in (("Left", 1), ("Right", -1)):
        # legs
        hip = mw @ pb[P + s + "UpLeg"].head
        a = pb[P + s + "UpLeg"].length * mw.to_scale()[0]; b = pb[P + s + "Leg"].length * mw.to_scale()[0]
        ank = Vector((sx * fx, fy, fz))
        kx, ky, kz = pose.get("knee", (0.35, -0.9, 0.5))
        knee, ank2 = _ik2(hip, ank, a, b, Vector((sx * kx, ky, kz)))
        _aim(arm, pb[P + s + "UpLeg"], knee); _aim(arm, pb[P + s + "Leg"], ank2)
        qa = mw.to_quaternion().normalized()
        _set_world_rot(arm, pb[P + s + "Foot"], qa @ S["tg"][s + "Foot"])
        _set_world_rot(arm, pb[P + s + "ToeBase"], qa @ S["tg"][s + "ToeBase"])
        # arms
        sh = mw @ pb[P + s + "Arm"].head
        a = pb[P + s + "Arm"].length * mw.to_scale()[0]; b = pb[P + s + "ForeArm"].length * mw.to_scale()[0]
        wr = bar + Vector((sx * g, pose.get("hand_y", 0), pose.get("hand_z", 0.07)))
        if "hands" in pose: wr = Vector((sx * pose["hands"][0], pose["hands"][1], pose["hands"][2]))
        ex, ey, ez = pose.get("elbow", (0.6, 0.6, 0.9))
        elb, wr2 = _ik2(sh, wr, a, b, Vector((sx * ex, ey, ez)))
        _aim(arm, pb[P + s + "Arm"], elb); _aim(arm, pb[P + s + "ForeArm"], wr2)
        hp = pose.get("hand_aim")
        if hp: _aim(arm, pb[P + s + "Hand"], wr2 + Vector((sx * hp[0], hp[1], hp[2])))
    bpy.context.view_layer.update()
    S["bar_vis"] = pose.get("bar_vis", True)

def lerp_pose(p0, p1, t):
    out = {}
    for k in set(p0) | set(p1):
        a = p0.get(k, p1.get(k)); b = p1.get(k, a)
        if isinstance(a, (int, float)) and not isinstance(a, bool): out[k] = a + (b - a) * t
        elif isinstance(a, tuple): out[k] = tuple(x + (y - x) * t for x, y in zip(a, b))
        else: out[k] = a if t < 0.5 else b
    return out

# --------------------------------------------------------------------------- keyframes
# Units: metres, world. Feet rest at ~ (±0.17, -0.07, 0.09). Body faces -Y.
FEET = (0.19, -0.06, 0.09)

DEAD_BOTTOM = dict(root=(0, 0.18, -0.42), hinge=64, spine=-4, neck=-22, head=-10, bar=(0, -0.11, 0.225), grip=0.27,
                   elbow=(0.6, 0.6, 0.5), knee=(0.4, -0.9, 0.5), feet=FEET)
DEAD_TOP = dict(root=(0, 0.0, 0.0), hinge=0, spine=0, neck=0, head=0, bar=(0, -0.11, 0.80), grip=0.27,
                elbow=(0.6, 0.6, 0.9), knee=(0.35, -0.9, 0.5), feet=FEET)

SQ_TOP = dict(root=(0, 0.0, -0.02), hinge=8, spine=0, neck=-6, head=0, bar=(0, 0.1, 1.40), grip=0.42, hand_z=-0.02,
              elbow=(0.5, 0.6, 0.9), knee=(0.45, -0.9, 0.5), feet=(0.23, -0.05, 0.09))
SQ_BOT = dict(root=(0, 0.22, -0.44), hinge=40, spine=0, neck=-26, head=-6, bar=(0, 0.05, 0.98), grip=0.42, hand_z=-0.02,
              elbow=(0.5, 0.6, 0.5), knee=(0.55, -1.0, 0.5), feet=(0.23, -0.05, 0.09))

C_HANG = dict(root=(0, 0.05, -0.04), hinge=18, spine=0, neck=-10, head=0, bar=(0, -0.14, 0.66), grip=0.26,
              elbow=(0.6, 0.6, 0.9), knee=(0.35, -0.9, 0.5), feet=FEET)
C_PULL = dict(root=(0, 0.0, 0.03), hinge=-4, spine=-2, neck=0, head=0, shrug=12, bar=(0, -0.12, 1.08), grip=0.26,
              elbow=(0.7, 0.3, 1.6), knee=(0.35, -0.9, 0.5), feet=FEET)
C_RACK = dict(root=(0, 0.03, -0.1), hinge=4, spine=0, neck=0, head=0, bar=(0, -0.17, 1.38), grip=0.26, hand_z=-0.02, hand_y=0.05,
              elbow=(0.45, -0.9, 1.2), knee=(0.4, -0.9, 0.5), feet=FEET)
C_RACK_UP = dict(C_RACK, root=(0, 0.0, 0.0), bar=(0, -0.16, 1.46))
C_PRESS = dict(root=(0, 0.0, 0.0), hinge=0, spine=0, neck=4, head=0, shrug=10, bar=(0, 0.0, 2.08), grip=0.26, hand_z=-0.06,
               elbow=(0.9, 0.2, 1.6), knee=(0.35, -0.9, 0.5), feet=FEET)

STAND = dict(root=(0, 0, 0), hinge=0, bar=(0, -0.11, 0.80), grip=0.27, hands=(0.26, 0.0, 0.86), elbow=(0.7, 0.5, 1.0), feet=FEET, bar_vis=False)

PU_UP = dict(root=(0, 0.0, 0.0), pitch=67, hinge=0, neck=-28, head=-10, hands=(0.27, -1.30, 0.07), elbow=(0.9, -0.5, 1.0),
             feet=(0.11, -0.04, 0.07), knee=(0.2, -0.5, -0.4), bar_vis=False)
PU_DOWN = dict(PU_UP, pitch=78, neck=-30)
