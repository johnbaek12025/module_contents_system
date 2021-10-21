$(function(){
    //이슈홈 슬라이더
    
    let issueNavList = $('.issue-nav-list .list-w .list').length;
    let issueListIndex = $('.issue-nav-list .list-w .active').index();

    
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
    
});