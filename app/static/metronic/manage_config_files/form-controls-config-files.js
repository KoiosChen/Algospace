//== Class definition

var FormControls = function () {
    //== Private functions
    var update = function () {
        $("#m_form_config").validate({
            submitHandler: function (form) {
                let value = editor.getValue()
                let key_id = $("#modal_key_id").text()
                let configs_select = $("#modal_config_id").text()
                $.ajax({
                    type: "POST",          //提交方式          
                    url: "update_config",  //提交的页面/方法名      
                    contentType: "application/json;charset=utf-8",
                    dataType: "json",
                    data: JSON.stringify({
                        "content": value,
                        "key_id": key_id,
                        "configs_select": configs_select
                    }, null, '\t'),          //参数（如果没有参数：null）          
                    success: function (msg) {
                        if (msg.status === 'OK') {
                            $("#sendmail2").modal('hide');
                            toastr.info(msg.content);
                            console.log(configs_select)
                            params = {'configs_select': configs_select.split(": ")[1]}
                            config_file_table.settings()[0].ajax.data = params;
                            config_file_table.ajax.reload();

                        } else {
                            $("#sendmail2").modal('hide');
                            toastr.warning(msg.content);
                        }
                    },
                    error: function (xhr, msg, e) {
                        toastr.warning("提交配置失败");
                        $("#sendmail2").modal('hide');
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
