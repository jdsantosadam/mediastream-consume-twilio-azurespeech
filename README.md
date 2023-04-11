# Azure Speech-to-Text SDK real-time transcription using a real-time Twilio Media Stream using WebSockets, Python, and Flask

## Requirements

- Python 3.7.x
- [Twilio Account](https://www.twilio.com/try-twilio)
- Tunneling service like [ngrok](https://ngrok.com/)

This project is able to transcribe the audio stream from Twilio using the Azure Speech-to-Text SDK.
The source and the base documentations can be found below:
- [Consume a real-time media stream using WebSockets, Python, and Flask](https://www.twilio.com/docs/voice/tutorials/consume-real-time-media-stream-using-websockets-python-and-flask). 


Follow along the docs to get the project up and running.

## About the project

The Azure Speech-to-Text SDK is used to transcribe the audio stream from Twilio. The documentation of the SDK can be found [here](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/quickstart-python). This project
it's configured to send the stream data from Twilio to the Azure Speech-to-Text directly using the SDK. The SDK is configured to use the [Speech Translation API](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-translation) to translate the audio stream to English. The translation is done in real-time and the transcription is returned in the response for each utterance that is detected in the audio stream.

## How to run

Configure the project according to the documentations above. For the real-time project, you will need to configure the environment variables with the Azure Recognition Service

Run the Flask server for the Twilio Media Stream project, and then tunnel the port using ngrok and copy the URL. Then, configure the url in the TwiML Bin (see the documentation above).

```shell
python app.py

# In another terminal
ngrok http 5000
```

## Transcription

With the project up and running, make a call to the Twilio number configured with the TwiML that will send the audio stream to the Flask server. The transcription will be printed in the console.







