'use strict';

$( function() {
    // パスワード送信
    $( "#form-password" ).submit(function(event) {
        // デフォルト動作は抑止
        event.preventDefault();
        
        var form = $(this);
        var button = $("#button-password");
        $.ajax({
            url: form.attr("action"),
            type: form.attr("method"),
            data: form.serialize(),
            success: function(result, textStatus, jqXHR) {
                alert(jqXHR.responseText);
                window.location.reload(false);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert(jqXHR.responseText);
            },
            beforeSend: function(jqXHR, settings) {
                button.attr('disabled', true);
            },
            complete: function(jqXHR, textStatus) {
                button.attr('disabled', false);
            }
        });
    });
});
