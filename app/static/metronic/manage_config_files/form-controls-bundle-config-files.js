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


var FormNewInstanceControls = function () {
    //== Private functions
    var update = function () {
        $("#m_form_new_instance").validate({
            rules: {
                new_instance_name: {
                    required: true,
                    noSpace: true,
                    illegalCharacter: true
                },
            },

            //display error alert on form submit
            invalidHandler: function (event, validator) {
                var alert = $('#m_form_new_instance_msg');
                alert.removeClass('m--hide').show();
                mApp.scrollTo(alert, -200);
            },

            submitHandler: function (form) {
                let new_app_name = $("#new_instance_name").val()
                let app_group_id = $("#group_id").val()
                $.ajax({
                    type: "POST",          //提交方式          
                    url: "new_app",  //提交的页面/方法名      
                    contentType: "application/json;charset=utf-8",
                    dataType: "json",
                    data: JSON.stringify({"app_group_id": app_group_id, "new_app_name": new_app_name}),          //参数（如果没有参数：null）          
                    success: function (msg) {
                        if (msg.status === 'OK') {
                            $("#modal_new_instance").modal('hide');
                            if ($("#m_form_bundle_config select[id='app_groups_select_in_modal']").val()) {
                                update_apps_by_app_group_select2($("#app_groups_select_in_modal option:checked").val(), "#apps_select_in_modal")
                            }
                            if (strategy_table.row("#" + app_group_id).child.isShown()) {
                                childTable.ajax.data = {"strategy_group_id": app_group_id}
                                childTable.ajax.reload()
                            }
                            toastr.info(msg.content);
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

//== Class definition

var FormControlsBundleDeploy = function () {
    //== Private functions

    var demo1 = function () {
        $("#m_form_bundle_config").validate({
            // define validation rules
            rules: {
                namespace_select_in_modal: {
                    select2required: true
                },
                app_groups_select_in_modal: {
                    select2required: true
                },
                apps_select_in_modal: {
                    select2required: true
                },
            },

            //display error alert on form submit
            invalidHandler: function (event, validator) {
                var alert = $('#m_form_bundle_config_msg');
                alert.removeClass('m--hide').show();
                mApp.scrollTo(alert, -200);
            },

            submitHandler: function (form) {
                let queued_file_length = myDropzone.getQueuedFiles().length;
                console.log(queued_file_length);
                if (queued_file_length > 0) {
                    mApp.block('#modal_transfer .modal-content', {
                        overlayColor: '#000000',
                        type: 'loader',
                        state: 'success',
                        size: 'lg'
                    });
                    myDropzone.processQueue();
                } else {
                    toastr.warning("未上传文件");
                }

            }
        });
    }


    return {
        // public functions
        init: function () {
            demo1();
        }
    };
}();