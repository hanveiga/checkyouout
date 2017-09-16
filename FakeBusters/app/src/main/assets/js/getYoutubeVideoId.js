function getYoutubeVideoId() {
    var width = 0;
    var src = "";
    $("iframe").each(function() {
        if(width < $(this).width()) {
            width = $(this).width()
            src= $(this).attr('src');
        }
    });
    var reg = /(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com(?:\/embed\/|\/v\/|\/watch\?v=))([\w-]{10,12})/g;
    var id = reg.exec(src)[1];
    console.log("youtube video id : "+id);
    Android.videoCallback(id);
}

getYoutubeVideoId();
