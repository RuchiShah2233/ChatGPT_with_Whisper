from os import system
import speech_recognition as sr
import sys, whisper, time, openai
import re
import pydub
from openai import OpenAI
from pydub import playback

s = sr.Microphone()
r = sr.Recognizer()

api_key = "Enter API-key"

tiny_model = whisper.load_model('tiny')
base_model = whisper.load_model('base')

if sys.platform != 'darwin':
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id) # 0 for male, 1 for female

def speak(text):
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    else:
        engine.say(text)
        engine.runAndWait()

def prompt_gpt(audio):
    print("Asking GPT...")

    try:
        with open("prompt.wav", "wb+") as f:
            f.write(audio.get_wav_data())
        result = base_model.transcribe('prompt.wav')
        prompt_text = result['text']
        if len(prompt_text.strip()) == 0:
            print("Empty prompt. Please speak again.")
            speak("Empty prompt. Please speak again.")
        else:
            client = OpenAI(api_key)
            messages = [{"role": "user", "content":"You're a helpful assistant."},
                        {"role": "user", "content": {prompt_text}}]
            response = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=messages)
            bot_response = response["choices"][0]["message"]["content"]
            print(f"GPT: {bot_response}")
            speak(bot_response)
    
    except Exception as e:
        print("Prompt error: ", e)

def listen_and_reply():

    while True:
        with s as source:
            print("Say something:")
            speak("Say something")    
            r.adjust_for_ambient_noise(source, duration=5)
            audio = r.listen(source)
        
        try:
            print("Processing...")
            text = r.recognize_google(audio)
            print("You said:", text)
            prompt_gpt(audio)

        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            speak("Sorry, I couldn't understand that.")
        except sr.RequestError as e:
            print(f"Error making the request; {e}")


if __name__ == '__main__':
    listen_and_reply()
