//font-size

$(function(){
    var lcvText = $('.listContentView .cont'),
        lcvLink = $('.listContentView .cont .txt a');
    

    $('.btn-font').bind('click', function(){
        var fsize = parseInt($('.listContentView .cont .txt').css('font-size'));

        if(fsize < 20){
            lcvText.css({
                "font-size" : fsize + 2 + "px",
                "line-height" : fsize + 10 + "px"
            });
            lcvLink.css('font-size', fsize + 2 + "px");

        }else if(fsize >= 20){
            lcvText.css({
                "font-size" : "15px",
                "line-height" : "25px"
            });
            lcvLink.css('font-size',  "15px");
        }
    });
})