from pydub import AudioSegment
import os
import requests
import json
import pprint


if not os.path.isdir("splitaudio"):
    os.mkdir("splitaudio")

audio = AudioSegment.from_file("vajont.wav")
lengthaudio = len(audio)
print("Length of Audio File:", lengthaudio)

start = 0
threshold = 60000
end = 0
counter = 0

url="https://localhost:8000/speech-recognize/1/2?language=it"
headers = {'app-name':'test_app','app-key':'CyLang-9da11944-2fb0-462d-a79d-d586cf2f1625'}
data = {}
data_json = json.dumps(data)

file_out=open("vajont.txt", "w") 
file_to_elab=1
file_count=0

while start < len(audio):
    end += threshold
    print(start , end)
    chunk = audio[start:end]
    filename = f'splitaudio/chunk{counter}.wav'
    chunk.export(filename, format="wav")
    counter +=1
    start += threshold

    #  recognize audio
    files = {'file': open(filename,'rb')}
    response = requests.post(url, headers=headers,data=data,files=files,verify=False)
    pprint.pprint(response.json())
    file_out.write(response.json()['text_rcgn'])
    file_out.write('\n')
    
    file_count=file_count+1
    if file_count>=file_to_elab:
        break

file_out.close()

