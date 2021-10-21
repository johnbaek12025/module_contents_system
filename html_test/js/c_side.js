$(function(){
    //우측메뉴 높이값
    let sideTop = $('#content').offset();
    let headerH = $('#header_w').height();

    $('#c_side').css({
        top: sideTop.top - headerH + 'px'
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

        $('.s_menu_control .next').on('click', function () {
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
});