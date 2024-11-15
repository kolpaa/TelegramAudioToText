import telebot
from telebot import apihelper
import subprocess
import os
import speech_recognition as sr 
from pydub import AudioSegment
from pydub.silence import split_on_silence

bot = telebot.TeleBot('7679976524:AAFQ5DSF9r5IOMsda1BSgD-LOCww8oZG258')
apihelper.API_URL = "http://localhost:8081/bot{0}/{1}"


r = sr.Recognizer()


def transcribe_audio(path):
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        text = r.recognize_google(audio_listened, language="ru-RU")
    return text

def get_large_audio_transcription_on_silence(path):
    sound = AudioSegment.from_file(path)  
    chunks = split_on_silence(sound,
        min_silence_len = 500,
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            print(chunk_filename, ":", text)
            whole_text += text
    return whole_text


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Я принмаю голосовые сообщения или аудиофайлы")


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):  
    bot.send_message(message.chat.id, "Обработка")
    a = bot.get_file(message.voice.file_id)
    print(a.file_path)
    process = subprocess.run(['ffmpeg', '-i', a.file_path, str(a.file_id) + ".wav"])
    bot.send_message(message.chat.id, get_large_audio_transcription_on_silence(str(a.file_id) + ".wav"))

@bot.message_handler(content_types=['audio'])
def get_audio_messages(message):  
    bot.send_message(message.chat.id, "Обработка")
    a = bot.get_file(message.audio.file_id)
    print(a.file_path)
    process = subprocess.run(['ffmpeg', '-i', a.file_path, str(a.file_id) + ".wav"])
    bot.send_message(message.chat.id, get_large_audio_transcription_on_silence(str(a.file_id) + ".wav"))


bot.polling(none_stop=True)
