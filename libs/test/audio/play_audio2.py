# Import packages
from pydub import AudioSegment
from pydub.playback import play


# Play audio
playaudio = AudioSegment.from_file("sample3.wav", format="wav")
play(playaudio)