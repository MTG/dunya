function loadSocialFollowButtons(){
    
    $('button.followButton').on('click', function(e){
        var csrftoken = $.cookie('csrftoken');
        e.preventDefault();
        $button = $(this);
        if($button.hasClass('following')){
            // Do Unfollow
            $.post("/social/user/unfollow", { username: $button.attr('id') })
            .done(function(data) {
              if(data.status == "OK"){
                $button.removeClass('following');
                $button.removeClass('unfollow');
                $button.text('Follow');
              }
              else{
                window.alert("Oups, there was some error unfollowing this user. Please try again");
              }
            })
            .fail(function() { window.alert("Oups, there was some error unfollowing this user. Please try again"); });
        } else {
            // Do Follow
            $.post("/social/user/follow", { username: $button.attr('id') })
            .done(function(data) {
              if(data.status == "OK"){
                $button.addClass('following');
                $button.text('Following');
              }
              else{
                window.alert("Oups, there was some error following this user. Please try again");
              }
            })
            .fail(function() { window.alert("Oups, there was some error following this user. Please try again"); });
        }
    });
        
    $('button.followButton').hover(function(){
         $button = $(this);
        if($button.hasClass('following')){
            $button.addClass('unfollow');
            $button.text('Unfollow');
        }
    }, function(){
        if($button.hasClass('following')){
            $button.removeClass('unfollow');
            $button.text('Following');
        }
    });

}