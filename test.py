import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()

with m as source: r.adjust_for_ambient_noise(source)

with sr.Microphone() as source:
        audio = r.listen(source)

text = r.recognize_sphinx(audio, keyword_entries="pochitach")

print(text)