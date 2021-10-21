//리포트 리포트분석 

$(function(){
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
});