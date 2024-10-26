from pydub import AudioSegment
sound = AudioSegment.from_mp3("vajont.mp3")
sound.export("vajont.wav", format="wav")