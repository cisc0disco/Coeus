from wit import Wit
import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk
import wikipedia
import json
from playsound import playsound
import geocoder
import configparser
import requests
import signal
from datetime import datetime, timedelta
import snowboydecoder
from hue_api import HueApi
from bs4 import BeautifulSoup

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

def Temp_classify(tmp):

    if(tmp == 1 or tmp == -1):
        return "bude {} stupeň".format(tmp)

    elif(tmp < 5 and tmp > -5):
        return "budou {} stupně".format(tmp)

    else:
        return "bude {} stupňů".format(tmp)

def Temp_classifyNow(tmp):

    if(tmp == 1 or tmp == -1):
        return "je {} stupeň".format(tmp)
    
    elif(tmp < 5 and tmp > -5):
        return "jsou {} stupně".format(tmp)

    else:
        return "je {} stupňů".format(tmp)
    
#deklarace proměnných

interrupted = False
azure_key = ""
azure_end = ""
wit_key = ""
weather_key = ""
bridge_ip = ""
voice = ""


#načtení konfigurace
config = configparser.ConfigParser()
config.read("login.ini")

def _config():

    global azure_key
    global azure_end
    global wit_key
    global weather_key
    global bridge_ip
    global voice

    headers = {"username":config["login"]["Username"], "password":config["login"]["Password"]}
    r = requests.post("http://127.0.0.1:8000/api/", data=headers)

    azure_key = r.json()["azure_key"]
    azure_end = r.json()["azure_end"]
    wit_key = r.json()["wit_key"]
    weather_key = r.json()["weather_key"]
    bridge_ip = r.json()["bridge_ip"]
    voice = r.json()["voice"]

_config()

#získání lokace pro počasí atd.
g = geocoder.ip("me")

#nastavení hue
api = HueApi()
try:
    api.create_new_user(bridge_ip)
    api.save_api_key(cache_file = "hue_token")
except:
    api.load_existing(cache_file = "hue_token")

api.fetch_lights()

#inicializace regnozicačních objektů
r = sr.Recognizer()
m = sr.Microphone()

#nastavení azure
speech_config = speechsdk.SpeechConfig(endpoint=azure_end, subscription=azure_key)
if(voice == "M"):
    speech_config.speech_synthesis_voice_name = "cs-CZ-AntoninNeural"
else:
    speech_config.speech_synthesis_voice_name = "cs-CZ-VlastaNeural"
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat(21))

synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

#oprava mikrofonů se šumem
with m as source: r.adjust_for_ambient_noise(source)

client = Wit(str(wit_key))

signal.signal(signal.SIGINT, signal_handler)

def main():
    _config()
    playsound("./audio/activated.mp3")
    while(not interrupted):
        try:    
            resp = client.message(Listen())
            intent = resp.get("intents")[0].get("name")
        except:
            playsound("./audio/disabled.mp3")
            break

        if(intent == "stop"):
            playsound("./audio/disabled.mp3")
            break

        elif (intent == "wikipedia"):
            try:
                body = resp.get("entities").get("wit$wikipedia_search_query:wikipedia_search_query")[0].get("body")
                Speak(Wikipedia(body))
            except Exception as e:
                if("may refer to:" in str(e)):
                    _e = str(e)
                    Speak("Možná jste měli na mysli " + _e[_e.find("may refer to:") + len("may refer to:")+1:_e.rfind(body)])
                else:
                    Speak("Omlouvám se, ale termín nebyl nalezen")

            playsound("./audio/disabled.mp3")
            break
            #TODO: přidat možnosti

        elif (intent == "weather"):
            try:
                body = resp.get("entities").get("day:day")[0].get("body")
                url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (g.lat, g.lng, weather_key)    
                response = requests.get(url)
                data = json.loads(response.text)
            except Exception as e:
                break

            if("dnes" in body): 
                expression = data.get("daily")[0].get("weather")[0].get("main").lower()
            elif(body == "zítra"):
                expression = data.get("daily")[1].get("weather")[0].get("main").lower()
            elif("teď" in body):
                expression = data.get("current").get("weather")[0].get("main").lower()

            tSaid_expression = ""
            nSaid_expression = ""
            print(expression)

            #teď
            if(expression == "thunderstorm"):
                nSaid_expression = "je bouřka"
            elif(expression == "drizzle"):
                nSaid_expression = "mrholí"
            elif(expression == "rain"):
                nSaid_expression = "prší"
            elif(expression == "snow"):
                nSaid_expression = "sněží"
            elif(expression == "clear"):
                nSaid_expression = "je slunečno"
            elif(expression == "clouds"):
                nSaid_expression = "je zataženo"
            elif(expression == "mist"):
                nSaid_expression = "je mhla"
            elif(expression == "clouds"):
                nSaid_expression = "je zataženo"
            elif(expression == "clouds"):
                nSaid_expression = "je zataženo"

            #dnes
            if(expression == "thunderstorm"):
                tSaid_expression = "bouřka"
            elif(expression == "drizzle"):
                tSaid_expression = "mrholit"
            elif(expression == "rain"):
                tSaid_expression = "pršet"
            elif(expression == "snow"):
                tSaid_expression = "sněžit"
            elif(expression == "clear"):
                tSaid_expression = "slunečno"
            elif(expression == "clouds"):
                tSaid_expression = "zataženo"
            elif(expression == "mist" or expression == "haze" or expression == "smoke"):
                tSaid_expression = "mlha"

            if("dnes" in body):
                #print(data.get("current"))
                #print(data.get("current").get("weather")[0].get("main"))
                #print(data)
                Speak("Dnes bude {} a nejnižší teplota dnes {} a nejvyšší teplota {}".format(tSaid_expression, Temp_classify(round(data.get("daily")[0].get("temp").get("min"))), Temp_classify(round(data.get("daily")[0].get("temp").get("max")))))

            elif(body == "zítra"):
                Speak("Zítra bude {} a nejnižší teplota {} a nejvyšší teplota {}".format(tSaid_expression, Temp_classify(round(data.get("daily")[1].get("temp").get("min"))), Temp_classify(round(data.get("daily")[1].get("temp").get("max")))))

            elif(body == "teď"):
                Speak("Momentálně {}, pocitově {} a {}".format(Temp_classifyNow(round(data.get("current").get("temp"))), Temp_classifyNow(round(data.get("current").get("feels_like"))), nSaid_expression))

            break

        elif (intent == "light"):
            body = resp.get("entities").get("state:state")[0].get("body")
            if (body.lower() == "zapni"):
                api.turn_on()
                break
            elif (body.lower() == "vypni"):
                api.turn_off()
                break
            else:
                api.toggle_on()
                break

        elif (intent == "set_light"):
            try:
                body = resp.get("entities").get("percent:percent")[0].get("body")
            except:
                print("error")
            api.set_brightness(body.replace("%", ""))

        elif (intent == "time"):
            Speak("Je "+str(datetime.now().hour)+"hodin a "+str(datetime.now().minute) + "minut")
            break

        elif (intent == "joke"):
            url = "https://vtipy.atropin.cz/1--vtipy--nahodny-vtip"
            page = requests.get(url)
            content = page.content
            soup = BeautifulSoup(content)
            div = soup.findAll("div", {"class": "content"})
            vtip = div[0].findAll("p")
            Speak(vtip[3].getText())
            break

        elif (intent == "news"):
            url = "https://www.novinky.cz/zahranicni/svet"
            page = requests.get(url)
            content = page.content
            soup = BeautifulSoup(content)
            headers = soup.findAll("h3", {'data-dot-data': '{"component":"mol-feed-item-title","action":"mol-feed-item-title-click"}'})
            titulky = ""
            for header in headers:
                if ("ON-LINE: " in header.getText()):
                    titulky += header.getText().replace("ON-LINE: ", "") + "\n"
                else:
                    titulky += header.getText() + "\n"

            Speak(titulky)
            break

        elif (intent == "covid"):
            body = resp.get("entities").get("day:day")[0].get("body")
            url = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakaza.min.json"
            r = requests.get(url)
            data = r.json()["data"]
            today = datetime.today()
            _today = today.strftime("%Y-%m-%d")
            yesterday = datetime.today() - timedelta(days=1)
            _yesterday = yesterday.strftime("%Y-%m-%d")
            
            #print(data[len(data)-1]["prirustkovy_pocet_nakazenych"])

            if ("dnes" in body or "dnešek" in body or "dneska" in body):
                if (data[len(data)-1]["datum"] == _today):
                    Speak("Za dnešní den přibylo" + str(data[len(data)-1]["prirustkovy_pocet_nakazenych"]) + " nakažených")
                else: 
                    Speak("Pro dnešní datum není známý přírustkový počet")
                
            elif ("včera" in body or "včerejšek" in body):
                if (data[len(data)-1]["datum"] == _yesterday):
                    Speak("Za včerejší den přibylo " + str(data[len(data)-1]["prirustkovy_pocet_nakazenych"]) + " nakažených")
                else: 
                    Speak("Pro včerejší datum není známý přírustkový počet")

            break


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
