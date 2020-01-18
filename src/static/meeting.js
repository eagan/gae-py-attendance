'use strict';

function text_attendance(b) {
    if (b) {
        return "ご出席";
    } else {
        return "ご欠席";
    }
}

function getOptionsGroup1() {
}

$( function() {
    $( "#tabs" ).tabs();
    
    //setupGroup1();
    
    // 参加申込
    $( "#form-entry" ).submit(function(event) {
        // デフォルト動作は抑止
        event.preventDefault();
        
        var form = $(this);
        var button = $("#button-entry");
        $.ajax({
            url: form.attr("action"),
            type: form.attr("method"),
            data: form.serialize(),
            success: function(result, textStatus, jqXHR) {
                alert('ご登録ありがとうございました');
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (jqXHR.responseJSON != null) {
                    if ('input_errors' in jqXHR.responseJSON) {
                        jqXHR.responseJSON.input_errors.forEach( function(e) {
                            $('input[name="' + e[0] + '"]').addClass('error');
                            $('#' + e[0] + '-error').text(e[1]);
                        });
                        alert('入力エラーが発生しました');
                    }
                } else {
                    alert(jqXHR.responseText);
                }
            },
            beforeSend: function(jqXHR, settings) {
                button.attr('disabled', true);
                $('input').removeClass('error');
                $('.errorMessage').empty();
            },
            complete: function(jqXHR, textStatus) {
                button.attr('disabled', false);
            }
        });
    });
    
    // 参加者検索
    $( "#form-search" ).submit(function(event) {
        // デフォルト動作は抑止
        event.preventDefault();
        
        var form = $(this);
        var table = $("#table-search-result");
        var template = $("#table-search-result-template").children();
        var button = $("#button-search");
        $.ajax({
            url: form.attr("action"),
            type: form.attr("method"),
            data: form.serialize(),
            success: function(result, textStatus, jqXHR) {
                table.empty();
                result.forEach(function(attendance) {
                    var row = template.clone();
                    var name = attendance['name1']
                    if (attendance['name2']) {
                        name = name + '（旧姓：' + attendance['name2'] + '）';
                    }
                    row.find('.name').text(name + ' 様');
                    row.find('.group1').text(attendance['group1'] + '回生');
                    if (attendance['group2']) {
                        row.find('.group2').text('部活動：' + attendance['group2']);
                    }
                    row.find('.attendance1').text('総会：' + text_attendance(attendance['attendance1']))
                    row.find('.attendance2').text('二次会：' + text_attendance(attendance['attendance2']))
                    table.append(row);
                });
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
