var transfer_confirm_table;

var DatatableConfirmTransferOrders = function () {
    console.log("making transfer orders");
    let table = $('#transfer_confirm_orders_id').DataTable({
        dom: "Bfrtip",
        scrollY: '100vh',
        scrollCollapse: true,
        // paging: false,
        serverSide: true,
        language: mylang,
        searching: false,
        destroy: true,
        "processing": true,
        ajax: {
            url: "/transfer_confirm_orders",
            type: "POST"
        },
        "scrollX": true,
        "columnDefs": [
            {
                // targets用于指定操作的列，从第0列开始，-1为最后一列
                // return后边是我们希望在指定列填入的按钮代码
                "targets": 7,
                "data": "id",
                "render": function (data, type, full, meta) {
                    return '<a ' + 'onClick="return HTMerConfirm(\'' + data + '\', ' + 0 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
                                <i class="fa fa-remove"></i>\
                            </a>\
                            <a ' + 'onClick="return HTMerConfirm(\'' + data + '\', ' + 1 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
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
            {data: "apply_user"},
            {data: "apply_reason"},
            {data: "apply_type"},
            {data: "apply_at"},
            {data: "share_to"}
        ],
        select: {},
        buttons: []
    });
    return table;
};

$(document).ready(function () {
    // let socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    // socket.on('ws_flush_transfer_confirm_order', function (msg) {
    //     if (msg.content === 1) {
    //         console.log("flush table");
    //         if (transfer_confirm_table) {
    //             transfer_confirm_table.ajax.reload();
    //         }
    //     }
    // });

    $("#search_submit").click(function () {
        let search_field = $('#search_field').val();
        console.log(search_field);
        let search_content = $('#search_content').val();
        let search_field_date = $('#search_field_date').val();
        console.log(search_field_date)
        let search_date_range = $('#search_m_daterange .form-control').val();
        console.log(search_date_range)
        let myajax = {
            'search_field': JSON.stringify(search_field),
            'search_content': search_content,
            'search_field_date': search_field_date,
            'search_date_range': search_date_range
        };
        if (transfer_confirm_table) {
            transfer_confirm_table.settings()[0].ajax.data = myajax;
            transfer_confirm_table.ajax.reload();
        }
    });
    $("#clear_all_data").click(function () {
        $("#search_content").val("");
        $("#search_field").selectpicker('val', ['noneSelectedText']);
        $("#select_date_field").selectpicker('val', ['noneSelectedText']);
        $("#search_daterange").val("");
    });
    transfer_confirm_table = DatatableConfirmTransferOrders();
});