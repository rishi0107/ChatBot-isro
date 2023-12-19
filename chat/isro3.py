import speech_recognition as sr
import requests
import spacy

class SpaceBotCLI:
    def __init__(self):
        print("Space Search Assistant CLI")

    def voice_search(self):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Say something...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)

        try:
            query = recognizer.recognize_google(audio)
            print(f"You said: {query}")

            # Send audio to the backend and get the response
            backend_response = self.send_audio_to_backend(audio)

            if backend_response:
                print("Backend Response:")
                print(backend_response + "\n")
            else:
                print("No relevant information found.")

        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    @staticmethod
    def load_space_data(file_path):
        space_data = {}
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    key, value = line.strip().split('|')
                    space_data[key.lower()] = value
                except ValueError:
                    print(f"Ignoring invalid line: {line}")

        return space_data

    @staticmethod
    def process_query(query, space_database):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(query)

        key_phrases = [token.text.lower() for token in doc if token.is_alpha]
        search_query = ' '.join(key_phrases)

        matching_keywords = [keyword for keyword in space_database.keys() if keyword in search_query]

        if matching_keywords:
            response_key = matching_keywords[0]
            return space_database[response_key]

        return None

    def send_audio_to_backend(self, audio):
        # Convert audio to text
        recognizer = sr.Recognizer()
        text_query = recognizer.recognize_google(audio)

        # Assuming you have a Django server running at http://localhost:8000
        backend_url = 'http://localhost:8000/chat/'

        # Send audio data to the backend
        response = requests.post(backend_url, data={'audio': text_query})

        if response.status_code == 200:
            return response.text
        else:
            print(f"Error sending audio to the backend. Status code: {response.status_code}")
            return None

if __name__ == "__main__":
    space_bot = SpaceBotCLI()
    space_bot.voice_search()
