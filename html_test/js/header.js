$(function(){

    $('[data-toggle="modal"]').removeAttr('href');

    
    //상단배너 가리기
    $('.top_close').on('click', function () {
        $('.top_w').slideUp();
    });


    //전체메뉴보기
    $('.allmenu').on('click', function () {
        $('#allmenu').modal('toggle');
    });
});