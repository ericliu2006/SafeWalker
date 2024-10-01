from flask import Flask, request
import pyttsx3  # For text-to-speech
import requests  # To call Google Maps API
import json

app = Flask(__name__)

# Initialize the text-to-speech engine
engine = pyttsx3.init()
destination = input("Please enter your destination: ")

def get_directions():

    # Your Google Maps API key
    google_maps_api_key = 'YOUR_API'

    # User's current location (you can hard-code it or use a method to get it dynamically)
    origin = "Current Location"  # Replace with actual location if needed

    # Call Google Maps Directions API
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={google_maps_api_key}"
    response = requests.get(directions_url)
    
    if response.status_code == 200:
        directions = response.json()
        # Check if the response contains valid routes
        if directions['status'] == 'OK':
            steps = directions['routes'][0]['legs'][0]['steps']
            directions_text = []
            for step in steps:
                directions_text.append(step['html_instructions'])  # Get HTML formatted instructions
            # Join instructions for speech
            final_directions = " ".join(directions_text)
            speak(final_directions)
            return f"Directions to {destination} have been spoken out loud."
        else:
            return "No valid routes found."

    return "Error fetching directions."

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

if __name__ == '__main__':
    app.run(debug=True)
