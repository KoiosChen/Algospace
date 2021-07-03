var transfer_table;

var DatatableTransferOrders = function () {
    console.log("making transfer orders");
    let table = $('#transfer_orders_id').DataTable({
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
            url: "/transfer_orders",
            type: "POST"
        },
        "scrollX": true,
        "columnDefs": [],
        columns: [
            {data: "id"},
            {data: "filename"},
            {data: "apply_reason"},
            {data: "apply_type"},
            {data: "apply_at"},
            {data: "share_to"},
            {data: "confirm_user"},
            {data: "confirm_result"},
            {data: "confirm_at"},
        ],
        select: {},
        buttons: []
    });
    return table;
};

$(document).ready(function () {
    transfer_table = DatatableTransferOrders();
});