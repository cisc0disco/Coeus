from wit import Wit
import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk
import wikipedia
import json
from playsound import playsound
import geocoder
import configparser
import requests
import snowboydecoder
import signal
from datetime import datetime

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

def Speak(text):
    synthesizer.speak_text_async(text)

def Listen():
    with sr.Microphone() as source:
        audio = r.listen(source, timeout=10, phrase_time_limit=10)
    return r.recognize_google(audio, language = "cs-CZ")

def Wikipedia(topic):
    wikipedia.set_lang("cs")
    return wikipedia.summary(topic, sentences=1)

#načtení konfigurace
config = configparser.ConfigParser()
config.read("konfigurace.ini")

#získání lokace pro počasí atd.
g = geocoder.ip("me")
print(g.city) #TODO: zpracuj to


#inicializace regnozicačních objektů
r = sr.Recognizer()
m = sr.Microphone()

#nastavení azure
speech_config = speechsdk.SpeechConfig(endpoint=config["azure"]["Endpoint"], subscription=config["azure"]["Subscription"])
speech_config.speech_synthesis_voice_name = "cs-CZ-AntoninNeural"
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat(21))

synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

#oprava mikrofonů se šumem
with m as source: r.adjust_for_ambient_noise(source)

client = Wit(str(config["wit"]["Token"]))

signal.signal(signal.SIGINT, signal_handler)

def main():
    snowboydecoder.play_audio_file
    playsound("./audio/activated.mp3")
    while(not interrupted):
        try:    
            resp = client.message(Listen())
            intent = resp.get("intents")[0].get("name")
        except:
            playsound("./audio/disabled.mp3")
            break

        if(intent == "stop" or intent == "přestaň"):
            playsound("./audio/disabled.mp3")
            break
            #TODO: opravit, přidat intent na wit

        elif (intent == "wikipedia"):
            body = resp.get("entities").get("wit$wikipedia_search_query:wikipedia_search_query")[0].get("body")
            try:
                Speak(Wikipedia(body))
            except:
                Speak("Omlouvám se, ale termín nebyl nalezen")

            playsound("./audio/disabled.mp3")
            break
            #TODO: přidat možnosti

        elif (intent == "weather"):
            body = resp.get("entities").get("day:day")[0].get("body")
            if("dnes" in body):
                url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (g.lat, g.lng, "b8673c1c6075378467103fc57030a52b")    
                response = requests.get(url)
                data = json.loads(response.text)
                print(data)

            elif(body == "zítra"):
                print("co zítra")

        elif (intent == "reminders"):
            Speak("Na dnes je jediný plán, dej si pořádnýho bonga a rozjebej se ty sračko")
            playsound("./audio/bong.mp3")

        elif (intent == "time"):
            Speak("Je "+str(datetime.now().hour)+"hodin a "+str(datetime.now().minute) + "minut")

        elif (intent == "spotify"):
            print("")

        elif (intent == "joke"):
            print("")

        elif (intent == "news"):
            print("")


def detected_callback():
    main()

detector = snowboydecoder.HotwordDetector("hotword.pmdl", sensitivity=0.5, audio_gain=1)
detector.start(detected_callback, interrupt_check=interrupt_callback, sleep_time=0.03)

detector.terminate()


"""
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized to speaker for text [{}]".format(text))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
    print("Did you update the subscription info?")
"""
