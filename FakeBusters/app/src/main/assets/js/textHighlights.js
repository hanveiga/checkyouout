var aFunction = function(e){
    console.log($(this).data('docid'))
    displayOverlay($(this).data('doctext'), $(this).data('docid'));

}

function displayOverlay(text , id) {
    $("<table id='overlay'><tbody><tr><td>" + text + "</td></tr><tr><td>" + id + "</td></tr></tbody></table>").css({
        "position": "fixed",
        "top": "0px",
        "left": "0px",
        "width": "50%",
        "height": "50%",
        "background-color": "rgba(0,0,0,.5)",
        "z-index": "10000",
        "vertical-align": "middle",
        "text-align": "center",
        "color": "#fff",
        "font-size": "20px",
        "cursor": "wait"
    }).appendTo("body");
}

function textHighlights(highlights) {
    console.log(highlights);
    Android.debugCallback(highlights);
    var index = 0;
        $("p").each(function() {
            data = $.parseJSON(highlights);
            for(var i = 0; i < data.length; i++) {
                var item = data[i];
                if(item.pid == index && item.label == "discuss") {
                    console.log("yellow");
                    $(this).css("background-color", "#F7DC6F")
                    $(this).append(
                                $("<a>")
                                .attr("data-docid", item.did)
                                .attr("data-doctext", item.docText)
                                .attr("href", "javascript:void(0)")
                                .text("click me")
                                .click(aFunction)
                                .wrap("<img src='../images/icon.gif' width='20px' height='20px'/>")
                            );
                }

                if(item.pid == index && item.label == "agree") {
                    console.log("green");
                    $(this).css("background-color", "#82E0AA")
                    $(this).append(
                                $("<a>")
                                .attr("data-docid", item.did)
                                .attr("data-doctext", item.docText)
                                .attr("href", "javascript:void(0)")
                                .text("click me")
                                .click(aFunction)
                                .wrap("<img src='../images/icon.gif' width='20px' height='20px'/>")
                            );
                }

                if(item.pid == index && item.label == "disagree") {
                    console.log("red");
                    $(this).css("background-color", "#F1948A");
                    $(this).append(
                                $("<a>")
                                .attr("data-docid", item.did)
                                .attr("data-doctext", item.docText)
                                .attr("href", "javascript:void(0)")
                                .text("click me")
                                .click(aFunction)
                                .wrap("<img src='../images/icon.gif' width='20px' height='20px'/>")
                            );
                }
            }

            index++;
        });
        Android.TextCallback("finish");
}

