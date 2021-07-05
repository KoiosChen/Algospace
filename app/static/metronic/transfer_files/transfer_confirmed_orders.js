var transfer_confirmed_table;

var DatatableConfirmedTransferOrders = function () {
    console.log("making transfer confirmed orders");
    let table = $('#transfer_confirmed_orders_id').DataTable({
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
            url: "/transfer_confirmed_orders",
            type: "POST"
        },
        "scrollX": true,
        "columnDefs": [],
        columns: [
            {data: "id"},
            {data: "filename"},
            {data: "apply_user"},
            {data: "apply_reason"},
            {data: "apply_type"},
            {data: "apply_at"},
            {data: "share_to"},
            {data: "confirm_result"},
            {data: "confirm_user"},
            {data: "confirm_at"},
        ],
        select: {},
        buttons: []
    });
    return table;
};

$(document).ready(function () {
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
        if (transfer_confirmed_table) {
            transfer_confirmed_table.settings()[0].ajax.data = myajax;
            transfer_confirmed_table.ajax.reload();
        }
    });

    $("#clear_all_data").click(function () {
        $("#search_content").val("");
        $("#search_field").selectpicker('val',['noneSelectedText']);
        $("#select_date_field").selectpicker('val',['noneSelectedText']);
        $("#search_daterange").val("");
    });
    transfer_confirmed_table = DatatableConfirmedTransferOrders();
});