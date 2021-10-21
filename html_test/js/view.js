$(function(){

    //게시판 댓글
    $('.recmmt').on('click', function () {
        $(this).parents('.cmmtBox').find('.re_cmmt_input').toggle();
    });

    //공유하기
    $('.btn-share').on('click', function () {
        $('.share_pop').fadeIn();
        $('.share_pop').find('.ly_close').children('button').on('click', function () {
            $('.share_pop').fadeOut();
        });
    });

    //운영배심원
    $('.btn-operjr').on('click', function () {
        $('.operjr_guide').fadeIn();
        $('.operjr_guide').find('.ly_close').children('button').on('click', function () {
            $('.operjr_guide').fadeOut();
        });
    });

    let opjrbtn = $('.operationjuror ul li a');

    $(opjrbtn).on('click', function () {
        $(this).toggleClass('active');
    });

});