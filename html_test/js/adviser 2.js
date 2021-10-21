//어드바이저

$(function(){
    $('.p_num_submit').on('click', function(){
        $('.a_num_input').show();
    });
    //인증번호
    

    $('.pNumCheck').on('click', function(){
        var thisBtn = $(this);

        $('#subscribe').modal('hide');
        $('#subscribe').on('hidden.bs.modal', function(e){
            var nextModal = $(thisBtn).attr('data-target');
            $(nextModal).modal('show');
            $(this).off('hidden.bs.modal');
        });
    });
    // 팝업내 팝업
});