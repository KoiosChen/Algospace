var bundle_config_file_table;
var editor;

var DatatableBundleConfigIssue = function () {
    console.log("making transfer confirmed orders");
    let table = $('#table_ready_issue').DataTable({
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
            url: "/load_bundle_config_table_issue",
            type: "POST"
        },
        "scrollX": true,
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 8,
                "data": "id",
                "render": function (data, type, full, meta) {
                    return '<a ' + 'onClick="return Deploy(\'' + data + '\', ' + 3 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Test">\
                                <i class="fa fa-download"></i>\
                            </a>\
                            <a ' + 'onClick="return Deploy(\'' + data + '\', ' + 0 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Deny">\
                                <i class="fa fa-remove"></i>\
                            </a>\
                            <a ' + 'onClick="return Deploy(\'' + data + '\', ' + 1 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-info m-btn--icon m-btn--icon-only m-btn--pill" title="Accept">\
                                <i class="fa fa-check"></i>\
                            </a>\
                            ';
                }
            },
            {"visible": false, "targets": []}
        ],
        columns: [
            {data: "id"},
            {data: "filename"},
            {data: "uncompress_to"},
            {data: "version"},
            {data: "issued_version"},
            {data: "deploy_reason"},
            {data: "apply_user"},
            {data: "apply_at"}
        ],
        select: {},
        buttons: []
    });
    return table;
};

$(document).ready(function () {
    let socket = io.connect('http://' + document.domain + ':' + location.port + '/algospace');
    socket.on('ws_flush_bundle_config_order', function (msg) {
        if (msg.content === 1) {
            console.log("flush table");
            if (bundle_config_file_table) {
                bundle_config_file_table.ajax.reload();
            }
        }
    });

    $("#search_submit").click(function () {
        if (config_file_table) {
            config_file_table.settings()[0].ajax.data = {'configs_select': $("#configs_select").val()};
            config_file_table.ajax.reload();
        }
    });


    $("#clear_all_modal_data").click(function () {
        if (confirm("是否确认清空数据？")) {
            editor.setValue("")
        }
    });

    bundle_config_file_table = DatatableBundleConfigIssue();
});