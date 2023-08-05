"""
    server.py
    Runs the flask server for the application and outlines the routes
"""

from flask import Flask, Response, jsonify, request
 
# flask app
app = Flask(__name__)

# mission in use
mission = None

class Server:
    """
        creates a flask server and manages routing
    """
    def __init__(self, _mission) -> None:
        global mission  # global mission 
        mission = _mission
        self.__port = 8500  # TODO: port should be read from mission file and passed into this server

    @app.route('/', methods=['GET'])
    def index() -> Response:
        """ index endpoint """
        data = {'data': ''}
        return jsonify(data), 200

    @app.route('/update/location', methods=['POST'])
    def update_location() -> Response: 
        """ endpoint to update the location of a vehicle """
        data = {'data': ''}

        # getting args from url
        callsign = request.form.get("callsign")
        lat = request.form.get("lat")
        long = request.form.get("long")

        if callsign is None or lat is None or long is None:
            return jsonify(data), 400
        
        if mission.update_location(callsign, lat, long):
            data = {'data': 'updated successfully'}
            return jsonify(data), 200
        return jsonify(data), 400

    def run(self):
        app.run(port=self.__port)
