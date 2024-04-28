from enum import Enum
from os import path
import speech_recognition as sr
import logging


class CyLangSpeechRecognizerType(Enum):
    WHISPER=1
    GOOGLE_CLOUD=2

class CyLangSpeechRecognition:
    def __init__(self, speech_type:int):
        self.speech_type=CyLangSpeechRecognizerType(speech_type)
        self.speech_recognizer = sr.Recognizer()
              
    def recognize(self,file_path:str,language:str=None)->str:
        
        logging.info("Recognize:"+file_path)
        
        audio_file = path.join(path.dirname(path.realpath(__file__)), file_path)
        
        with sr.AudioFile(audio_file) as source:
            audio = self.speech_recognizer.record(source) 

        txt_rec=""

        try:
            if self.speech_type==CyLangSpeechRecognizerType.WHISPER:
                if language is None:
                    txt_rec=self.speech_recognizer.recognize_whisper(audio)
                else:
                    txt_rec=self.speech_recognizer.recognize_whisper(audio, language=language) 
            elif self.speech_type==CyLangSpeechRecognizerType.GOOGLE_CLOUD:
                  if language is None:
                    txt_rec=self.speech_recognizer.recognize_google_cloud(audio)
                  else:
                    txt_rec=self.speech_recognizer.recognize_google_cloud(audio, language=language)
            else:
                raise ValueError(self.speech_type)    

            logging.info("Recognized Text:"+txt_rec)                 

        except sr.UnknownValueError:
            logging.warn("Recognizer could not understand audio")
        except sr.RequestError as e:
            logging.error("Request Error")
            raise e

        return txt_rec        
