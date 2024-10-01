from flask import Flask, request, render_template, jsonify
import pyttsx3  # For text-to-speech
import requests  # To call Google Maps API

app = Flask(__name__)

# Initialize the text-to-speech engine
engine = pyttsx3.init()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/destination', methods=['POST'])
def destination():
    destination = request.form['destination']
    origin_lat = request.form['origin_lat']
    origin_lng = request.form['origin_lng']
    origin = f"{origin_lat},{origin_lng}"

    directions_response = get_directions(origin, destination)
    return jsonify(directions_response)

def get_directions(origin, destination):
    # Your Google Maps API key (ensure it's valid and safe to use)
    google_maps_api_key = ''

    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={google_maps_api_key}"
    response = requests.get(directions_url)

    if response.status_code == 200:
        directions = response.json()
        if directions['status'] == 'OK':
            steps = directions['routes'][0]['legs'][0]['steps']
            directions_text = []
            for step in steps:
                # Parse and strip out HTML instructions for readability
                directions_text.append(step['html_instructions'].replace('<div style="font-size:0.9em">', '').replace('</div>', ''))
            final_directions = " ".join(directions_text)
            speak(final_directions)  # Speak the final directions
            return {"message": f"Directions to {destination} spoken aloud."}
        else:
            return {"error": "No valid routes found."}
    return {"error": "Error fetching directions."}

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

if __name__ == '__main__':
    app.run(debug=True)
