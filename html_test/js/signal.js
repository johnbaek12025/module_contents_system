//AI매매신호 팝오버 스크립트

$(function(){

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

})