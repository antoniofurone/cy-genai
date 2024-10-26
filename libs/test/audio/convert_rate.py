from pydub import AudioSegment
sound = AudioSegment.from_file("sample3.wav")
print("----------Before Conversion--------")
print("Frame Rate", sound.frame_rate)
print("Channel", sound.channels)
print("Sample Width",sound.sample_width)
# Change Frame Rate
sound = sound.set_frame_rate(16000)
# Change Channel
# 1=mono; 2=stereo
sound = sound.set_channels(1)
# Change Sample Width
# 1=8bit; 2=16 bit; 3=32 bit; 4=64 bit;
sound = sound.set_sample_width(2)
sound.export("convertedrate.wav", format ="wav")