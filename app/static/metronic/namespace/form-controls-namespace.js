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


var FormControlsNamespace = function () {
    //== Private functions
    var update = function () {
        $("#m_form_namespace").validate({
            rules: {
                new_namespace_name: {
                    required: true,
                    noSpace: true,
                    illegalCharacter: true
                },
            },

            //display error alert on form submit
            invalidHandler: function (event, validator) {
                var alert = $('#modal_new_namespace_msg');
                alert.removeClass('m--hide').show();
                mApp.scrollTo(alert, -200);
            },

            submitHandler: function (form) {
                let name = $("#new_namespace_name").val()
                let owners = $("#m_select2_owners").val()
                let namespace_id = $("#tmp_namespace_id").val()
                $.ajax({
                    type: "POST",          //提交方式          
                    url: "update_namespace",  //提交的页面/方法名      
                    contentType: "application/json;charset=utf-8",
                    dataType: "json",
                    data: JSON.stringify({"namespace_id": namespace_id, "name": name, "owners": owners}),          //参数（如果没有参数：null）          
                    success: function (msg) {
                        if (msg.status === 'OK') {
                            $("#modal_new_namespace").modal('hide');
                            namespace_table.draw(false);
                            toastr.info(result.content);
                            //setTimeout("location.reload()", 1000);
                        } else {
                            toastr.warning(msg.content);
                        }
                    },
                    error: function (xhr, msg, e) {
                        toastr.warning("提交配置失败");
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