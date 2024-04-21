import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Calibrating...")
    r.adjust_for_ambient_noise(source, duration=5)

    print("Okay, go!")
    while 1:
        text = ""
        print("listening now...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=30)
            print("Recognizing...")
            
            # whisper model options are found here: https://github.com/openai/whisper#available-models-and-languages
            # other speech recognition models are also available.
            text = r.recognize_whisper(
                     audio,
                     model="medium.en",
                     show_dict=True,
             )["text"]

            
            
        except Exception as e:
            unrecognized_speech_text = (
                    f"Sorry, I didn't catch that. Exception was: {e}s"
            )
        
        text = unrecognized_speech_text
        print(text)

        