//module

$(function(){

    var moduleLeft = $('.modulebox').find('.left');

    $('.modulebox .left').each(function (index, item){
        var moduleLeftHeight = $(item).next('.right').height();

        $(item).height(moduleLeftHeight + 'px');
    })
    
})