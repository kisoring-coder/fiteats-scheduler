# Paid ad series (desk-job weight loss)

adA/ holds everything used to build Ad A "Desk Job Diet" (posted 22 Nov 2026).

- build.py: frame renderer (1080x1920, 30 fps). `python3 build.py render` writes silent.mp4; `python3 build.py stills 1.0 5.0` writes test stills.
  Expects avatar frames in avA/ (hook) and avM/ (shared middle). Make them with:
  `ffmpeg -i hookA.mp4 -vf "fps=30,eq=contrast=1.04:saturation=0.95" -start_number 0 avA/%04d.png` (same for mid.mp4 -> avM/).
  Photo fallback path in build.py points at /home/claude/v2/photo_hq.png; change it if missing.
- words.json: word timings of vo.wav (Creative Claw transcribe output).
- vo.wav: full voiceover (Kisor's Cartesia clone, speed 1.0).
- hookA.mp3 / mid.mp3: the audio sent to HeyGen; hookA.mp4 / mid.mp4: the HeyGen Avatar 6 Turbo clips.
- mid.mp4 is the SHARED middle line reused in ads B and C: "That's why every FitEats meal is low calorie, high protein, and cooked fresh every day."
- music_raw.mp3: ElevenLabs Music track (24 s). mix.py edits it (+0.10 s, loops 4 beats after the 17.15 s drop). SFX in mix.py are NOT used in the final.
- Final mix (no SFX, -13 LUFS): see the source-of-truth doc.
- FitEats_Ad_A_DeskJob_v2.mp4 + cover.jpg: the posted ad.
