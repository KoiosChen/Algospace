var namespace_table;
var editor;

var DatatableNamespace = function () {
    console.log("making namespace orders");
    let table = $('#table_namespaces').DataTable({
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
            url: "/load_namespace_table",
            type: "POST"
        },
        "scrollX": true,
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 3,
                "data": "DT_RowId",
                "render": function (data, type, full, meta) {
                    return '<a ' + 'onClick="return EditNamespace(\'' + data + '\', ' + 1 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-info m-btn--icon m-btn--icon-only m-btn--pill" title="Accept">\
                                <i class="fa fa-pencil"></i>\
                            </a>\
                            ';
                }
            },
            {"visible": false, "targets": []}
        ],
        columns: [
            {data: "namespace"},
            {data: "owner"},
            {data: "related_strategies"}
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

    namespace_table = DatatableNamespace();
    FormControlsStrategyGroup.update_info();
});