var strategy_table;
var editor;

var DatatableStrategy = function () {
    console.log("making strategy table");
    let table = $('#table_strategy_manage').DataTable({
        Dom: "Blfrtip",
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
                "targets": 7,
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
            {
                "className": 'details-control',
                "orderable": false,
                "data": null,
                "defaultContent": ''
            },
            {data: "strategy_name"},
            {data: "strategy_desc"},
            {data: "namespace"},
            {data: "local_path"},
            {data: "dryrun_path"},
            {data: "owner"}
        ],
        select: {},
        buttons: [],
        initComplete: function () {
            init = false;
        },
        createdRow: function (row, data, index) {
            if (data.extn === '') {
                var td = $(row).find("td:first");
                td.removeClass('details-control');
            }
        },
        rowCallback: function (row, data, index) {
            //console.log('rowCallback');
        }
    });
    return table;
};

$(document).ready(function () {
    strategy_table = DatatableStrategy();
    FormControlsStrategy.update_info();
    // Add event listener for opening and closing first level childdetails
    $('#table_strategy_manage tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = strategy_table.row(tr);
        var rowData = row.data();
        console.log(rowData)

        //get index to use for child table ID
        var index = row.index();
        console.log(index);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        } else {
            // Open this row
            row.child(
                '<table class="child_table" id = "child_details' + index + '" cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;width:100%">' +
                '<thead><tr><th></th><th>Instance Name</th><th>Deployed Version</th><th>Action</th></tr></thead><tbody>' +
                '</tbody></table>').show();


            var childTable = $('#child_details' + index).DataTable({
                Dom: "Bfrtip",
                scrollY: '100vh',
                scrollCollapse: true,
                paging: true,
                serverSide: true,
                searching: false,
                language: mylang,
                "processing": true,

                ajax: {
                    url: "/get_app_info",
                    type: "POST",
                    data: {"strategy_group_id": rowData.DT_RowId}
                },
                "scrollX": true,
                "columnDefs":
                    [
                        {
                            // targets用于指定操作的列，从第0列开始，-1为最后一列
                            // return后边是我们希望在指定列填入的按钮代码
                            "targets": 3,
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
                    {
                        "className": 'details-control1',
                        "orderable": false,
                        "data": null,
                        "defaultContent": ''
                    },
                    {"data": "instance_name"},
                    {"data": "latest_version"},
                ],
                destroy: true,
            });
            tr.addClass('shown');
        }
        // Add event listener for opening and closing second level child details
        $('.child_table tbody').off().on('click', 'td.details-control1', function () {
            var c_tr = $(this).closest('tr');
            var c_row = childTable.row(c_tr);
            var childRowData = c_row.data();

            if (c_row.child.isShown()) {
                // This row is already open - close it
                c_row.child.hide();
                c_tr.removeClass('shown');
            } else {
                // Open this row
                c_row.child(
                    '<table id = "child_details_2" cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;width:100%">' +
                    '<thead><tr><th>Order</th><th>Filename</th><th>Version</th><th>Apply Time</th><th>Auditor</th><th>Audit Result</th><th>Audit Time</th></tr></thead><tbody>' +
                    '</tbody></table>').show();

                $('#child_details_2').DataTable({
                    Dom: "Blfrtip",
                    scrollY: '100vh',
                    scrollCollapse: true,
                    // paging: false,
                    serverSide: true,
                    searching: false,
                    language: mylang,
                    destroy: true,
                    "processing": true,
                    ajax: {
                        url: "/load_bundle_config_table",
                        type: "POST",
                        data: {"strategy_id": childRowData.DT_RowId}
                    },
                    "scrollX": true,
                    columns: [
                        {data: "id"},
                        {data: "filename"},
                        {data: "version"},
                        {data: "apply_at"},
                        {data: "issue_user"},
                        {data: "issue_result"},
                        {data: "issue_at"},
                    ],
                    destroy: true,
                    scrollY: '100px'
                });
                c_tr.addClass('shown');
            }
        });
    });

});