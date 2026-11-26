"""Render the 3D lifts reel frame by frame (Cycles CPU) and export muscle anchor points per frame."""
import sys, math, json, os, time, bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0, "/home/claude/b3d")
import scene, poses as PZ

FPS = 30; TOTAL = 36.4; RW, RH = 1080, 1350
OUT = "/home/claude/b3d/frames"; os.makedirs(OUT, exist_ok=True)
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
F0 = int(a[0]) if a else 0; F1 = int(a[1]) if len(a) > 1 else int(TOTAL * FPS); STEP = int(a[2]) if len(a) > 2 else 1
SAMPLES = int(a[3]) if len(a) > 3 else 6

S = scene.build(); sc = bpy.context.scene; scene.setup_render(sc, RW, RH, SAMPLES)
mats = [S["body"], S["joints"]]

def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def cyc(keys, u):
    for (u0, p0), (u1, p1) in zip(keys, keys[1:]):
        if u0 <= u <= u1: return PZ.lerp_pose(p0, p1, ease((u - u0) / max(1e-6, u1 - u0)))
    return dict(keys[-1][1])

CLEAN = [(0, PZ.C_HANG), (0.13, PZ.C_PULL), (0.25, PZ.C_RACK), (0.34, PZ.C_RACK_UP), (0.52, PZ.C_PRESS), (0.62, PZ.C_PRESS),
         (0.78, PZ.C_RACK_UP), (0.88, PZ.C_RACK), (1.0, PZ.C_HANG)]
DEAD = [(0, PZ.DEAD_BOTTOM), (0.42, PZ.DEAD_TOP), (0.58, PZ.DEAD_TOP), (1.0, PZ.DEAD_BOTTOM)]
SQUAT = [(0, PZ.SQ_TOP), (0.42, PZ.SQ_BOT), (0.55, PZ.SQ_BOT), (1.0, PZ.SQ_TOP)]
PUSH = [(0, PZ.PU_UP), (0.45, PZ.PU_DOWN), (0.55, PZ.PU_DOWN), (1.0, PZ.PU_UP)]

# scene: (start, end, mode, cycle keys, cycle seconds, camera (yaw0, yaw1, dist, height, target))
SCENES = [
 (0.00, 3.45, "intro", None, 0, (8, 30, 5.6, 1.25, (0, 0, 0.98))),
 (3.45, 7.24, "sweep", None, 0, (35, -25, 4.7, 1.2, (0, 0, 0.92))),
 (7.24, 17.21, "clean", CLEAN, 3.3, (24, 34, 6.3, 1.3, (0, 0, 1.13))),
 (17.21, 24.07, "dead", DEAD, 2.8, (28, 36, 5.1, 1.1, (0, 0, 0.72))),
 (24.07, 30.95, "squat", SQUAT, 2.8, (30, 38, 5.4, 1.2, (0, 0, 0.86))),
 (30.95, 34.30, "push", PUSH, 1.7, (60, 68, 5.6, 1.3, (0, -0.72, 0.25))),
 (34.30, 36.40, "cta", None, 0, (20, 40, 5.2, 1.2, (0, 0, 0.92))),
]
HL = {
 "clean": [("forearms", 10.85), ("traps", 11.6), ("shoulders", 12.2), ("triceps", 13.0), ("upperback", 13.6), ("glutes", 15.2),
           ("quads", 15.7), ("hamstrings", 15.75), ("calves", 15.8)],
 "dead": [("hamstrings", 19.6), ("glutes", 20.3), ("lowerback", 21.0), ("lats", 21.8), ("traps", 22.5), ("grip", 23.1)],
 "squat": [("quads", 27.1), ("glutes", 27.7), ("innerthigh", 28.45), ("hamstrings", 29.3), ("core", 30.0)],
 "push": [("chest", 33.2), ("triceps", 33.45), ("shoulders", 33.6), ("core", 33.75)],
}
SWEEP = ["calves", "hamstrings", "quads", "innerthigh", "glutes", "core", "lowerback", "lats", "chest", "upperback",
         "traps", "shoulders", "triceps", "biceps", "forearms", "grip"]

# anchor vertices per muscle: masked vertices on the figure's left side (faces the camera)
surf = bpy.data.objects["Beta_Surface"]; me = surf.data
ANCH = {}
for k in scene.MUSCLES:
    at = me.attributes["m_" + k]
    idx = [i for i, d in enumerate(at.data) if d.value > 0.5 and me.vertices[i].co.x > 2.0]
    ANCH[k] = idx[::max(1, len(idx) // 40)]

def scene_at(t):
    for s in SCENES:
        if s[0] <= t < s[1]: return s
    return SCENES[-1]

def highlights(t, s):
    mode = s[2]; hl = {}
    if mode == "sweep":
        for n, k in enumerate(SWEEP): hl[k] = ease((t - s[0] - 0.25 - n * 0.17) / 0.3)
    elif mode in HL:
        for k, ton in HL[mode]: hl[k] = max(hl.get(k, 0), ease((t - ton) / 0.25))
    elif mode == "cta":
        for k in SWEEP: hl[k] = 0.35
    return hl

def pose_at(t, s):
    mode = s[2]
    if mode in ("intro",): return PZ.C_HANG
    if mode in ("sweep", "cta"): return PZ.STAND
    u = ((t - s[0]) / s[4]) % 1.0
    return cyc(s[3], u)

meta = {}
mpath = f"{OUT}/meta_{F0}_{F1}.json"
t_start = time.time()
for f in range(F0, F1, STEP):
    t = f / FPS; s = scene_at(t)
    pose = pose_at(t, s); PZ.apply(S, pose)
    vis = pose.get("bar_vis", True) and s[2] not in ("sweep", "push", "cta")
    for o in S["bar_objs"]: o.hide_render = not vis
    hl = highlights(t, s)
    for mat in mats:
        for k in scene.MUSCLES: mat.node_tree.nodes["V_" + k].outputs[0].default_value = hl.get(k, 0.0)
    y0, y1, dist, h, tz = s[5]; u = (t - s[0]) / (s[1] - s[0]); yaw = math.radians(y0 + (y1 - y0) * u)
    S["cam"].location = (tz[0] + dist * math.sin(yaw), tz[1] - dist * math.cos(yaw), h); S["ctgt"].location = tz
    bpy.context.view_layer.update()
    # anchors
    dg = bpy.context.evaluated_depsgraph_get(); ev = surf.evaluated_get(dg); m2 = ev.to_mesh()
    anc = {}
    for k, v in hl.items():
        if v <= 0.01 or not ANCH.get(k): continue
        pts = [ev.matrix_world @ m2.vertices[i].co for i in ANCH[k]]
        c = sum(pts, Vector()) / len(pts)
        p = world_to_camera_view(sc, S["cam"], c)
        anc[k] = [round(p.x * RW, 1), round((1 - p.y) * RH, 1), round(v, 3)]
    ev.to_mesh_clear()
    meta[f] = dict(t=t, mode=s[2], anchors=anc)
    sc.render.filepath = f"{OUT}/f_{f:04d}.png"
    bpy.ops.render.render(write_still=True)
    if f % 30 == 0:
        print(f"frame {f} t={t:.2f} elapsed {time.time() - t_start:.0f}s", flush=True)
        json.dump(meta, open(mpath, "w"))
json.dump(meta, open(mpath, "w"))
print("DONE", F0, F1, round(time.time() - t_start))
