from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pydub import AudioSegment
import tempfile
import speech_recognition as sr
import os
import requests
import spacy

from chat.isro3 import SpaceBotCLI


@csrf_exempt
def homepage(request):
    if request.method == 'POST':
        try:
            audio_file = request.FILES.get('audio')

            if audio_file:
                # Save the audio file to a temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                temp_file.write(audio_file.read())
                temp_file.close()

                # Convert the audio file to PCM WAV format
                converted_temp_file = convert_audio_to_wav(temp_file.name)

                # Use speech recognition to convert audio to text
                recognized_text = recognize_speech(converted_temp_file)

                # Process the query and get a response
                backend_response = process_query_and_get_response(recognized_text)

                # Delete the temporary files
                os.remove(temp_file.name)
                os.remove(converted_temp_file)

                return JsonResponse({'success': True, 'text': recognized_text, 'response': backend_response}, status=200)
            else:
                return JsonResponse({'error': 'No audio file provided'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'chat.html')

def convert_audio_to_wav(input_file_path):
    # Load the input audio file
    audio_data = AudioSegment.from_file(input_file_path)

    # Save the audio data as PCM WAV format
    output_file_path = input_file_path.replace('.wav', '_converted.wav')
    audio_data.export(output_file_path, format='wav')

    return output_file_path

def recognize_speech(audio_file_path):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {str(e)}"

def process_query_and_get_response(query):
    # Assuming you have a SpaceBotCLI instance
    space_bot = SpaceBotCLI()

    # Load space data from a file (adjust the path as needed)
    space_database = space_bot.load_space_data('chat/space_data.txt')

    # Process the query using spaCy
    nlp = spacy.load("en_core_web_sm")
    doc_query = nlp(query)

    # Initialize variables for best match
    best_match = None
    best_similarity = 0.0

    # Iterate over each key phrase in the space database
    for keyword, value in space_database.items():
        doc_keyword = nlp(keyword)
        similarity = doc_query.similarity(doc_keyword)

        # Update best match if the current similarity is higher
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = value

    if best_similarity > 0.6:  # Adjust the threshold as needed
        return best_match
    else:
        return "No relevant information found."
