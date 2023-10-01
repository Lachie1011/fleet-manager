"""
    server.py
    Runs the flask server for the application and outlines the routes
"""

from flask import Flask, Response, jsonify, request

# flask app
APP = Flask(__name__)

# mission in use
MISSION = None


class Server:
    """
        creates a flask server and manages routing
    """

    def __init__(self, _mission) -> None:
        global MISSION  # pylint: disable=W0603
        MISSION = _mission
        self.__port = 8500  # TODO: port should be read from the MISSION yaml

    @APP.route('/', methods=['GET'])
    def index() -> Response:  # pylint: disable=E0211
        """ index endpoint """
        data = {'data': ''}
        return jsonify(data), 200

    @APP.route('/update/location', methods=['POST'])
    def update_location() -> Response:  # pylint: disable=E0211
        """ endpoint to update the location of a vehicle """
        data = {'data': ''}

        # getting args from url
        callsign = request.form.get("callsign")
        lat = request.form.get("lat")
        long = request.form.get("long")

        if callsign is None or lat is None or long is None:
            return jsonify(data), 400

        if MISSION.update_location(callsign, lat, long):
            data = {'data': 'updated successfully'}
            return jsonify(data), 200
        return jsonify(data), 400

    def run(self):
        """ runs the server """
        # TODO: debug should be read through a manager yaml
        APP.run(port=self.__port, debug=False)
