import base64
import io
import json
import logging
import os

import audioop
from pydub import AudioSegment

from flask import Flask
from flask_sockets import Sockets
import azure.cognitiveservices.speech as speechsdk

AZURE_SPEECH_SUBSCRIPTION_KEY = os.environ.get("AZURE_SPEECH_SUBSCRIPTION_KEY")
AZURE_SERVICE_REGION = os.environ.get("AZURE_SERVICE_REGION")

speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_SUBSCRIPTION_KEY, region=AZURE_SERVICE_REGION, speech_recognition_language='en-US')
wave_format = speechsdk.audio.AudioStreamFormat(samples_per_second=16000, bits_per_sample=16, channels=1)
audio_stream = speechsdk.audio.PushAudioInputStream(stream_format=wave_format)
audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
speech_recognizer.canceled.connect(lambda evt: on_canceled(evt))


def on_canceled(evt):
    print('CANCELED')
    print(evt)
    print(evt.result)
    print(evt.result.cancellation_details)

app = Flask(__name__)
sockets = Sockets(app)

HTTP_SERVER_PORT = 5000


def on_transcription_response(result):
    if not result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return

    transcription = result.text
    print("Transcription: " + transcription)

@sockets.route('/media')
def echo(ws):
    app.logger.info("Connection accepted")
    speech_recognizer.start_continuous_recognition()
    # A lot of messages will be sent rapidly. We'll stop showing after the first one.
    has_seen_media = False
    message_count = 0
    while not ws.closed:
        message = ws.receive()
        if message is None:
            app.logger.info("No message received...")
            continue

        # Messages are a JSON encoded string
        data = json.loads(message)

        # Using the event type you can determine what type of message you are receiving
        if data['event'] == "connected":
            app.logger.info("Connected Message received: {}".format(message))
        if data['event'] == "start":
            app.logger.info("Start Message received: {}".format(message))
        if data['event'] == "media":
            if not has_seen_media:
                # app.logger.info("Media message: {}".format(message))
                payload = data['media']['payload']
                # app.logger.info("Payload is: {}".format(payload))
                chunk = base64.b64decode(payload)
                # app.logger.info("That's {} bytes".format(len(chunk)))
                # app.logger.info("Additional media messages from WebSocket are being suppressed....")
                wav_data = AudioSegment.from_file(io.BytesIO(chunk), format='mulaw').set_frame_rate(16000).set_sample_width(2).set_channels(1).raw_data
                audio_stream.write(wav_data)
                # has_seen_media = True
        if data['event'] == "stop":
            app.logger.info("Stop Message received: {}".format(message))
            speech_recognizer.stop_continuous_recognition()
            break
        message_count += 1

    app.logger.info("Connection closed. Received a total of {} messages".format(message_count))


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    print("Server listening on: http://localhost:" + str(HTTP_SERVER_PORT))
    server.serve_forever()
