//== Class definition
jQuery.validator.addMethod("noSpace", function (value, element) {
    return value == '' || value.trim().length != 0;
}, "不能为空格");


jQuery.validator.addMethod("illegalCharacter", function (value, element) {
    let val_reg = /;|；|^\.|\s+|:|：/;
    return val_reg.test(value) == false;
}, "非法字符");

jQuery.validator.addMethod("select2required", function (value, element) {
    return value != '0';
}, "必选");


var FormControlsStrategy = function () {
    //== Private functions
    var update = function () {
        $("#m_form_new_strategy").validate({
            rules: {
                new_strategy_name: {
                    required: true,
                    noSpace: true,
                    illegalCharacter: true
                },
                namespace_select_in_modal: {
                    required: true
                },
                local_path: {
                    required: true
                },
                dryrun_path: {
                    required: true
                }
            },

            //display error alert on form submit
            invalidHandler: function (event, validator) {
                var alert = $('#modal_new_strategy_msg');
                alert.removeClass('m--hide').show();
                mApp.scrollTo(alert, -200);
            },

            submitHandler: function (form) {
                let name = $("#new_strategy_name").val()
                let owners = $("#m_select2_owners").val()
                let strategy_id = $("#tmp_strategy_id").val()
                let desc = $("#strategy_desc").val()
                let local_path = $("#local_path").val()
                let dryrun_path = $("#dryrun_path").val()
                let namespace_id = $("#namespace_select_in_modal").val()
                $.ajax({
                    type: "POST",          //提交方式          
                    url: "update_strategy",  //提交的页面/方法名      
                    contentType: "application/json;charset=utf-8",
                    dataType: "json",
                    data: JSON.stringify({
                        "strategy_id": strategy_id,
                        "name": name,
                        "owners": owners,
                        "desc": desc,
                        "local_path": local_path,
                        "dryrun_path": dryrun_path,
                        "namespace_id": namespace_id
                    }),          //参数（如果没有参数：null）          
                    success: function (msg) {
                        if (msg.status === 'OK') {
                            $("#modal_new_strategy").modal('hide');
                            strategy_table.draw(false);
                            toastr.info(result.content);
                            //setTimeout("location.reload()", 1000);
                        } else {
                            toastr.warning(msg.content);
                        }
                    },
                    error: function (xhr, msg, e) {
                        toastr.warning("提交策略失败");
                    }
                });
            }
        });
    }

    return {
        // public functions
        update_info: function () {
            update();
        }
    };
}();