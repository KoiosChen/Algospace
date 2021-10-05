var config_file_table;
var editor;

var DatatableConfigFiles = function () {
    console.log("making transfer confirmed orders");
    let table = $('#config_file_table_id').DataTable({
        dom: "Bfrtip",
        scrollY: '100vh',
        scrollCollapse: true,
        // paging: false,
        serverSide: true,
        searching: false,
        language: mylang,
        destroy: true,
        "processing": true,
        ajax: {
            url: "/config_file_table",
            type: "POST"
        },
        "scrollX": true,
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 4,
                "data": "id",
                "render": function (data, type, full, meta) {
                    return '<a ' + 'onClick="return HTMerConfirm(\'' + data + '\', ' + 0 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
                                <i class="la la-trash-o"></i>\
                            </a>\
                            <a ' + 'onClick="return ConfigFile(\'' + data + '\', ' + 1 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-info m-btn--icon m-btn--icon-only m-btn--pill" title="Update">\
                                <i class="fa fa-gear"></i>\
                            </a>\
                            ';
                }
            },
            {"visible": false, "targets": []}
        ],
        columns: [
            {data: "key"},
            {data: "value"},
            {data: "status"},
            {data: "version"},
        ],
        select: {},
        buttons: []
    });
    return table;
};

$(document).ready(function () {
    $("#search_submit").click(function () {
        if (config_file_table) {
            config_file_table.settings()[0].ajax.data = {'configs_select': $("#configs_select").val()};
            config_file_table.ajax.reload();
        }
    });

    $("#clear_all_data").click(function () {
        $("#namespace_select").selectpicker('val', ['noneSelectedText']);
        $("#app_groups_select").selectpicker('val', ['noneSelectedText']);
        $("#apps_select").selectpicker('val', ['noneSelectedText']);
    });

    $("#clear_all_modal_data").click(function () {
        if (confirm("是否确认清空数据？")) {
            editor.setValue("")
        }
    });

    $("#namespace_select").on("select2:select", function (e) {
        let namespace = $("#namespace_select option:checked").val();//获取select的值
        let select_id = "#app_groups_select"
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
    });

    $("#app_groups_select").on("select2:select", function (e) {
        let app_groups = $("#app_groups_select option:checked").val();//获取select的值
        let select_id = "#apps_select"
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
    });

    $("#apps_select").on("select2:select", function (e) {
        let apps = $("#apps_select option:checked").val();//获取select的值
        let select_id = "#configs_select"
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
    });

    config_file_table = DatatableConfigFiles();
    FormControls.update_info();
});