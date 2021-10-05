var bundle_config_file_table;
var editor;

var DatatableBundleConfigFiles = function () {
    console.log("making transfer confirmed orders");
    let table = $('#table_bundle_deploy').DataTable({
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
            url: "/load_bundle_config_table",
            type: "POST"
        },
        "scrollX": true,
        "columnDefs": [],
        columns: [
            {data: "id"},
            {data: "filename"},
            {data: "version"},
            {data: "uncompress_to"},
            {data: "apply_at"},
            {data: "issue_user"},
            {data: "issue_result"},
            {data: "issue_at"},
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

    bundle_config_file_table = DatatableBundleConfigFiles();
    FormNewInstanceControls.update_info();
    FormControlsBundleDeploy.init();
});