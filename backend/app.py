from flask import Flask, request, jsonify
import requests
from video_detection import VideoProcessor
import pyttsx3

app = Flask(__name__)

# Google Maps Directions API key
API_KEY = 'AIzaSyDgVxHoB_dMB4PVM7tHCZWUqqbLuz68_bQ'

# Initialize video processor (from your earlier code)
video_processor = VideoProcessor()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def get_directions(origin, destination, api_key):
    """Fetch walking directions from Google Maps Directions API."""
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={api_key}"
    response = requests.get(url)
    directions_data = response.json()
    
    if not directions_data['routes']:
        return None
    
    steps = directions_data['routes'][0]['legs'][0]['steps']
    return steps

def speak_instruction(instruction):
    """Speak out the walking direction instruction."""
    engine.say(instruction)
    engine.runAndWait()

@app.route('/directions', methods=['POST'])
def get_directions_and_guide():
    """Receive origin and destination from the frontend and provide directions."""
    data = request.get_json()
    origin = data.get('origin')
    destination = data.get('destination')

    if not origin or not destination:
        return jsonify({'error': 'Origin and destination are required.'}), 400

    # Fetch directions from Google Maps Directions API
    steps = get_directions(origin, destination, API_KEY)
    if steps is None:
        return jsonify({'error': 'No routes found.'}), 404

    instructions = []
    for step in steps:
        # Extract and clean the HTML instructions from Google Maps
        instruction = step['html_instructions']
        instruction = instruction.replace('<b>', '').replace('</b>', '')
        instruction = instruction.replace('<div style="font-size:0.9em">', ' ').replace('</div>', '')
        instructions.append(instruction)
        # Speak each instruction
        speak_instruction(instruction)

    return jsonify({'directions': instructions}), 200

@app.route('/process_video', methods=['POST'])
def process_video():
    """Process a video stream for signal and vehicle detection."""
    # Assuming you will be sending a video feed (not implemented fully here)
    video_processor.process_frame()  # Your existing logic to process video
    
    return jsonify({'message': 'Video processing completed.'})

if __name__ == '__main__':
    app.run(debug=True)
