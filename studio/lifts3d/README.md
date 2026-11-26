3D x-ray lifter pipeline (Blender as a Python module, Cycles CPU, no image credits).
- Model: Xbot.glb from the three.js repo (Mixamo rig). Bones re-aimed at children so limbs can be solved.
- poses.py: analytic 2-bone IK for arms/legs, hip hinge, push-up pitch. Pose dicts per lift.
- scene.py: x-ray emission shader (rim + faint wireframe, semi-transparent), per-muscle masks from bone weights + normals, barbell, floor.
- render_all.py: per-frame pose, muscle highlights, camera, anchor export -> frames/f_XXXX.png + meta json (~1.8 s/frame on 2 CPUs).
- compose.py: background, karaoke captions, kicker, muscle labels, bloom -> video.
Install: pip install --break-system-packages bpy==5.3.0 ; model: raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/Xbot.glb
