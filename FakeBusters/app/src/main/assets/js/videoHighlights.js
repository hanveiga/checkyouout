function videoHighlights(highlights) {

}

var player, timer, timeSpent = [];
//display = document.getElementById('display');

function onYouTubeIframeAPIReady() {
    Android.debugCallback("onYouTubeIframeAPIReady");
	player = new YT.Player( 'player', {
		events: { 'onStateChange': function(event) {
                                     Android.debugCallback("onPlayerStateChange");
                                   } }
	});
	console.log(player);
	Android.debugCallback(player);
}

function onPlayerStateChange(event) {
    Android.debugCallback("onPlayerStateChange");
	if(event.data === 1) { // Started playing
        if(!timeSpent.length){
            for(var i=0, l=parseInt(player.getDuration()); i<l; i++) timeSpent.push(false);
        }
	    timer = setInterval(record,100);
    }
    if(event.data === 1) { }
    if(event.data === 1) { }
}


function showPercentage(){
    var percent = 0;
    for(var i=0, l=timeSpent.length; i<l; i++){
        if(timeSpent[i]) percent++;
    }
    percent = Math.round(percent / timeSpent.length * 100);
    display.innerHTML = percent + "%";
}