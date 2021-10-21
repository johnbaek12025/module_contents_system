$(function(){
    

    //게시판 blind 링크 삭제
    let tblBlind = $('.board_tbl table tbody tr.blind td a');
    tblBlind.removeAttr("href");
    $('.board .latest_list li.active a').removeAttr('href');

    //게시판 검색 안내버튼
    $('.board_sch').find('.guide').on('click', function () {
        $('.layer_guide').fadeIn();

        $('button.close span').on('click', function () {
            $('.layer_guide').fadeOut();
        });
    });
    

});