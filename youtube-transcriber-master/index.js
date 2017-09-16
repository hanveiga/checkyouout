const express        = require('express');
const bodyParser     = require('body-parser');
const app            = express();
var watson = require('./watson');
var youtube = require('./youtube');
var path = require('path');

var flags = process.argv.slice(2);

const port = 8001;

app.listen(port, () => {
  console.log('We are live on ' + port);
});

app.get('/videototext', function (req, res) {
	console.log(req.query.id);
	youtube.getYouTubeAudio(req.query.id)
	.then(watson.watsonSpeechToText.bind(this, path.join(__dirname, 'file.flac')))
	.then(function(){
		console.log('Done transcribing video id: ' + flags[1]);
		var transcript = require('./transcript.json');
		res.setHeader('Content-Type', 'application/json');
    		res.json(transcript);
	});
})



