function get_user_list(select_id,checked_options) {
    $.ajax({
        type: "GET",          //提交方式          
        url: "get_user_list",  //提交的页面/方法名          
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            if (msg.status === 'OK') {
                if (msg.content.length > 0) {
                    $(select_id).empty()
                    $(select_id).select2({
                        data: msg.content
                    });
                    if (checked_options) {
                        $(select_id).select2().val(checked_options).trigger("change")
                    }
                } else {
                    $(select_id).empty()
                    $(select_id).select2({
                        data: [{"id": 0, "text": "请选择"}]
                    });
                }
            } else {
                toastr.warning(msg.content);
            }
        },
        error: function (xhr, msg, e) {
            toastr.warning("error");
        }
    });
}