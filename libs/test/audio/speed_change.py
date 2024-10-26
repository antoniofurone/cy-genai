from pydub import AudioSegment

sound = AudioSegment.from_file("sample3.wav")

def speed_change(sound, speed):

    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })

    filename = 'changed_speed.wav'

    sound_with_altered_frame_rate.export(filename, format ="wav")
# To Slow down audio
slow_sound = speed_change(sound, 0.8)
# To Speed up the audio 
#fast_sound = speed_change(sound, 1.2)