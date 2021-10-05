$("#namespace_select").on("select2:select", function (e) {
    let namespace = $("#namespace_select option:checked").val();//获取select的值
    update_app_group_by_namespace_select(namespace, "#app_groups_select")
});

$("#app_groups_select").on("select2:select", function (e) {
    let app_groups = $("#app_groups_select option:checked").val();//获取select的值
    update_apps_by_app_group_select2(app_groups, "#apps_select")
});

$("#apps_select").on("select2:select", function (e) {
    let apps = $("#apps_select option:checked").val();//获取select的值
    update_config_by_app_file(apps, "#configs_select")
});

$("#namespace_select_in_modal").on("select2:select", function (e) {
    let namespace = $("#namespace_select_in_modal option:checked").val();//获取select的值
    update_app_group_by_namespace_select(namespace, "#app_groups_select_in_modal")
});

$("#app_groups_select_in_modal").on("select2:select", function (e) {
    let app_groups = $("#app_groups_select_in_modal option:checked").val();//获取select的值
    update_apps_by_app_group_select2(app_groups, "#apps_select_in_modal")
});

$("#apps_select_in_modal").on("select2:select", function (e) {
    let ns = $("#namespace_select_in_modal option:checked").text();//获取select的值
    let ag = $("#app_groups_select_in_modal option:checked").text()
    let a = $("#apps_select_in_modal option:checked").val()
    let a_text = $("#apps_select_in_modal option:checked").text()
    $("#uncompress_to").val(ns + '/' + ag + '/' + a_text)
    $.ajax({
        type: "GET",          //提交方式          
        url: "get_app_info",  //提交的页面/方法名          
        data: {"app_id": a},   //参数（如果没有参数：null）          
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            if (msg.status === 'OK') {
                if (msg.content.version) {
                    $("#deployed_version").val("v" + msg.content.version + "@" + msg.content.deploy_at)
                }

            } else {
                toastr.warning(msg.content);
            }
        },
        error: function (xhr, msg, e) {
            toastr.warning("error");
        }
    });
});


function update_app_group_by_namespace_select(namespace, select_id) {
    $.ajax({
        type: "GET",          //提交方式          
        url: "config_related",  //提交的页面/方法名          
        data: {"content": namespace, "table_name": "NameSpaces", "foreign_obj": "app_groups"},   //参数（如果没有参数：null）          
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            if (msg.status === 'OK') {
                if (msg.content.length > 0) {
                    $(select_id).empty()
                    $(select_id).select2({
                        data: msg.content
                    });
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

function update_apps_by_app_group_select2(app_groups, select_id) {
    $.ajax({
        type: "GET",          //提交方式          
        url: "config_related",  //提交的页面/方法名          
        data: {"content": app_groups, "table_name": "AppGroups", "foreign_obj": "apps"},   //参数（如果没有参数：null）          
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            if (msg.status === 'OK') {
                if (msg.content.length > 0) {
                    $(select_id).empty()
                    $(select_id).select2({
                        data: msg.content
                    });
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

function update_config_by_app_file(apps, select_id) {
    $.ajax({
        type: "GET",          //提交方式          
        url: "config_related",  //提交的页面/方法名          
        data: {"content": apps, "table_name": "Apps", "foreign_obj": "configurations"},   //参数（如果没有参数：null）          
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            if (msg.status === 'OK') {
                if (msg.content.length > 0) {
                    $(select_id).empty()
                    $(select_id).select2({
                        data: msg.content
                    });
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