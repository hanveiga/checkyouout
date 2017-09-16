var watson = require('watson-developer-cloud');
var fs = require('fs');
var path = require('path');
var Promise = require('bluebird');

var speech_to_text = watson.speech_to_text({
  version: 'v1',
  url: "https://stream.watsonplatform.net/speech-to-text/api",
  username: "a1a457d9-2215-49af-88ed-676baa6905d9",
  password: "SjwQhGGXeoPV"
});

exports.watsonSpeechToText = function(audioFile) {

  return new Promise(function(resolve, reject) {

    var params = {
      content_type: 'audio/flac',
      timestamps: true,
      continuous: true
    };
    var results = {};
    results["final"] = [];
    results["text"] = "";
    var finalTranscript = "";

    // create the stream
    var recognizeStream = speech_to_text.createRecognizeStream(params);

    // pipe in some audio
    fs.createReadStream(audioFile).pipe(recognizeStream);

    // listen for 'data' events for just the final text
    // listen for 'results' events to get the raw JSON with interim results, timings, etc.

    recognizeStream.setEncoding('utf8'); // to get strings instead of Buffers from `data` events

    recognizeStream.on('results', function(e) {
      if (e.results[0].final) {
        results.final.push(e);
      }
    });

    ['results', 'error', 'connection-close', 'close'].forEach(function(eventName) {
      recognizeStream.on(eventName, console.log.bind(console, eventName + ' event: '));
    });

    ['data'].forEach(function(eventName) {
      recognizeStream.on(eventName, makeFinalTranscript);
    });

function makeFinalTranscript(transcript) {
	finalTranscript = finalTranscript + transcript;
}

    recognizeStream.on('error', function(err) {
      util.handleError('Error writing to transcript.json: ' + err);
    });

    recognizeStream.on('close', function() {
	console.log(finalTranscript);
	results.text = finalTranscript;
    	var transcriptFile = path.join(__dirname, 'transcript.json');

      fs.writeFile(transcriptFile, JSON.stringify(results), function(err) {
        if (err) {
          util.handleError(err);
        }
        resolve();
      });
    });
  });
};
