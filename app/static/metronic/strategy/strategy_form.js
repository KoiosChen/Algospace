var strategy_table;
var editor;

var DatatableStrategy = function () {
    console.log("making strategy table");
    let table = $('#table_strategy_manage').DataTable({
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
            url: "/load_strategy_table",
            type: "POST"
        },
        "scrollX": true,
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 6,
                "data": "DT_RowId",
                "render": function (data, type, full, meta) {
                    return '<a ' + 'onClick="return EditStrategy(\'' + data + '\', ' + 1 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-info m-btn--icon m-btn--icon-only m-btn--pill" title="Accept">\
                                <i class="fa fa-pencil"></i>\
                            </a>\
                            ';
                }
            },
            {"visible": false, "targets": []}
        ],
        columns: [
            {data: "strategy_name"},
            {data: "strategy_desc"},
            {data: "namespace"},
            {data: "local_path"},
            {data: "dryrun_path"},
            {data: "owner"}
        ],
        select: {},
        buttons: []
    });
    return table;
};

$(document).ready(function () {
    strategy_table = DatatableStrategy();
    FormControlsStrategy.update_info();
});