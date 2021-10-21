////////////////////////////////
//////////페이지사용js//////////
////////////////////////////////

$(function () {

    $('[data-toggle="modal"]').removeAttr('href');

    //메인 슬라이더
    $('.text-banner_w').bxSlider({
        auto:true,
        mode: 'vertical',
        control: false,
        infiniteLoop: false,
        minSlides: 1,
        maxSlides: 1,
        moveSlides: 1,
        nextText: '',
        prevText: '',
        hideControlOnEnd: true
    });

    //이슈홈 슬라이더
    var issueNavList = $('.issue-nav-list .list-w .list').length;
    var issueListIndex = $('.issue-nav-list .list-w .active').index();

    $('.issue-nav-list .list-w .list').on('click', function(){
        $('.issue-nav-list .list-w .list').removeClass('active');
        $(this).addClass('active');
    });

    
    if(issueNavList > 6){
        $('.issue-nav-list .list-w').bxSlider({
            mode: 'horizontal',
            pager: false,
            minSlides: 1,
            maxSlides: 6,
            moveSlides: 1,
            slideMargin: 0,
            slideWidth: 958 / 6,
            startSlide : issueListIndex,
            //infiniteLoop:false,
            nextText: '>',
            prevText: '<',
            preventDefaultSwipeX: false,
            touchEnabled: false,
            hideControlOnEnd: true
        });
    }
    

    //상단배너 가리기
    $('.top_close').on('click', function () {
        $('.top_w').slideUp();
    });


    //전체메뉴보기
    $('.allmenu').on('click', function () {
        $('#allmenu').modal('toggle');
    });

    //우측메뉴 높이값
    let sideTop = $('#content').offset();
    let headerH = $('#header_w').height();

    $('#c_side').css({
        top: sideTop.top - headerH  + 'px'
    });

    //우측메뉴 종목리스트 오버
    $(".s_list a[data-toggle='popover']").popover({
        trigger: 'manual',
        html: true,
        placement: 'left'
    }).on('mouseenter', function () {
        var _this = this;

        $(this).popover('show');
        $('.popover').on('mouseleave', function () {
            $(_this).popover('hide');
        });
    }).on('mouseleave', function () {
        var _this = this;

        setTimeout(function () {
            if (!$('.popover:hover').length) {
                $(_this).popover('hide');
            }
        });
    });

    //우측메뉴 종목리스트 슬라이드
    var s_menuLenth = $('.s_m01 li').length;

    if (s_menuLenth > 8) {
        $('.s_menu_control').removeClass('disabled')

        var slider = $('.s_m01 .s_list').bxSlider({
            mode: 'vertical',
            control: false,
            pager: false,
            infiniteLoop: false,
            minSlides: 8,
            maxSlides: 8,
            moveSlides: 1,
            nextText: '',
            prevText: '',
            hideControlOnEnd: true
        });

        $('.s_menu_control .next').on('click', function(){
            slider.goToNextSlide();
            return false;
        });
        $('.s_menu_control .prev').on('click', function () {
            slider.goToPrevSlide();
            return false;
        });
    }

    //우측메뉴 탭스크립트
    $('#myTab a').on('click', function (e) {
        e.preventDefault()
        $(this).tab('show')
    })

    //종목홈 top 관심종목 on/off
    $('.ins').on('click', function(){
        $(this).toggleClass('act');
    });

    //게시판 blind 링크 삭제
    let tblBlind = $('.board_tbl table tbody tr.blind td a');
    tblBlind.removeAttr("href");
    $('.board .latest_list li.active a').removeAttr('href');

    //게시판 검색 안내버튼
    $('.board_sch').find('.guide').on('click', function(){
        $('.layer_guide').fadeIn();

        $('button.close span').on('click', function () {
            $('.layer_guide').fadeOut();
        });
    });


    //게시판 댓글
    $('.recmmt').on('click', function(){
        $(this).parents('.cmmtBox').find('.re_cmmt_input').toggle();
    });

    //공유하기
    $('.btn-share').on('click', function(){
        $('.share_pop').fadeIn();
        $('.share_pop').find('.ly_close').children('button').on('click', function(){
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

    $(opjrbtn).on('click', function(){
        $(this).toggleClass('active');
    });


    //글쓰기 파일업로드

    var fileTarget = $('.filebox .upload-hidden');

    fileTarget.on('change', function () {
        if (window.FileReader) {
            var filename = $(this)[0].files[0].name;
        } else {
            var filename = $(this).val().split('/').pop().split('\\').pop();
        }

        $(this).siblings('.upload-name').val(filename);
    });


    //추천종목 아이템리스트

    var rmdItemList = $('.left_item li').length;
    if (rmdItemList > 9) {

        var slider2 = $('.left_item').bxSlider({
            mode: 'vertical',
            pager: false,
            infiniteLoop: false,
            minSlides: 8,
            maxSlides: 8,
            moveSlides: 1,
            hideControlOnEnd: true,
            touchEnabled: false,
            nextText: '<span class="glyphicon glyphicon-triangle-bottom" aria-hidden="true"></span>',
            prevText: '<span class="glyphicon glyphicon-triangle-top" aria-hidden="true"></span>'
        });
        slider2.reloadSlider();
    }



    //프린트버튼

    // 폰트사이즈조절

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


    //signal

    $('.rb_info').popover({
        trigger: 'manual',
        html: true,
        placement : 'bottom',
        container : '.aisignal_w .info'
    }).on('mouseenter', function () {
        var _this = this;

        $(this).popover('show');
        $('.popover').on('mouseleave', function () {
            $(_this).popover('hide');
        });
    }).on('mouseleave', function () {
        var _this = this;

        setTimeout(function () {
            if (!$('.popover:hover').length) {
                $(_this).popover('hide');
            }
        });
    });

    //report

    $(".table a[data-toggle='popover']").popover({
        trigger: 'manual',
        placement: 'bottom'
    }).on('mouseenter', function () {
        var _this = this;

        $(this).popover('show');
        $('.popover').on('mouseleave', function () {
            $(_this).popover('hide');
        });
    }).on('mouseleave', function () {
        var _this = this;

        setTimeout(function () {
            if (!$('.popover:hover').length) {
                $(_this).popover('hide');
            }
        });
    });

    //adviser
    $('.p_num_submit').on('click', function(){
        $('.a_num_input').show();
    });
    

    $('.pNumCheck').on('click', function(){
        var thisBtn = $(this);

        $('#subscribe').modal('hide');
        $('#subscribe').on('hidden.bs.modal', function(e){
            var nextModal = $(thisBtn).attr('data-target');
            $(nextModal).modal('show');
            $(this).off('hidden.bs.modal');
        });
        
    });

    //module

    var moduleLeft = $('.modulebox').find('.left');

    $('.modulebox .left').each(function (index, item){
        var moduleLeftHeight = $(item).next('.right').height();

        $(item).height(moduleLeftHeight + 'px');
    })


});