# FitEats Reel Studio

Code that renders FitEats Instagram Reels (1080x1920, 30 fps) with Python PIL + ffmpeg.
Voice comes from Creative Claw (ElevenLabs v4, voice_id 2iAXJEMO2o0PqUHzvZwQ "Ranbir", neutral Indian-English male).

| Folder | Reel | Style |
|---|---|---|
| story_reel/ | EP01 Desk Body, EP02 Why eating less backfires, EP03 30g protein quiz | dark charcoal + lime, kinetic captions |
| strength/ | Strong At Any Age (Karthik, Priya, Ravi) | dark + lime, character story |
| e847/ | 8:47 PM (Karthik) | dark + lime, 18 fast scenes |
| hour23/ | 1 Hour vs 23 Hours | cream paper + red/green, music only, no voice |
| eggs/ | 2 Eggs a Day for 14 Days | charcoal + yolk yellow, voice |
| chars/ | draws the flat character sprites | |
| assets/ | sprites/*.png, music_cc.mp3 (ElevenLabs music bed used on all reels) | |

Builders read voice files from ./dl/ (voice_tight.wav, words.json) — those are not in the repo; regenerate the voice per reel.
Typical modes: `python3 build.py timing | stills <t...> | render <scene>`.
The e847 and strength builders share one engine (copied from story_reel); e847/build.py is the assembled file.
