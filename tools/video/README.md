# Video clips (rebuilt 18 Nov 2026)
Pipeline: Playwright records the demo persona (`?demo=<id>`, sample data only) at 540x960 with green tap rings; Piper voice `en_GB-alba-medium` narrates each line; ffmpeg delays each line to the moment its action starts, scales to 1080x1920 and mixes (loudnorm -16 LUFS).
Setup after a workspace reset: `pip install --break-system-packages piper-tts`; Pete re-attaches `en_GB-alba-medium.onnx` (Hugging Face is blocked here; do not commit the 63 MB file). Paths in the scripts point at /home/claude/voice.
Clips: `c_pep_logging.py` (type "pep", pick from library, tap a portion, Log). Male voice for voice-entry clips: quieter, about 65-70% of Alba (not needed here).
`c_voice_logging.py` (voice entry, Alan voice at 0.68), `c_when_you_eat.py` (Reports > When you eat card; builds the mp4 itself)., `c_carer_view.py` (Settings > Carer & Clinician).
Media is never committed; it goes to YouTube via Pete.
