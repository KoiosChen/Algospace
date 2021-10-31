function delete_items(delete_item) {
    $("#" + delete_item).on("click", function () {
        let this_id = this.id
        console.log(this_id)
        if (this_id === "delete_strategy") {
            var the_row = strategy_table.rows(".selected").data()
        }
        else if (this_id === "delete_instance") {
            var the_row = childTable.rows(".selected").data()
        }
        else if (this_id === "delete_file") {
            var the_row = grandChildTable.rows(".selected").data()
        }

        if (the_row.length > 0) {
            swal({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                type: 'warning',
                showCancelButton: true,
                confirmButtonText: "Delete",
                cancelButtonText: 'No, cancel!',
                reverseButtons: true
            }).then(function (result) {
                let actionText;
                let actionDetail;
                actionText = 'Done';
                actionDetail = ''

                if (result.value) {
                    delete_target(the_row.toArray(), this_id)
                    swal(
                        actionText,
                        actionDetail,
                        'success'
                    )
                    // result.dismiss can be 'cancel', 'overlay',
                    // 'close', and 'timer'
                } else if (result.dismiss === 'cancel') {
                    swal(
                        'Cancelled',
                        'Mission dismissed :)',
                        'error'
                    )
                }
            });
        }
    });
}


$("#new_strategy").click(function () {
    $("#new_strategy_name").val("");
    $("#strategy_desc").val("");
    $("#local_path").val("");
    $("#dryrun_path").val("");
    //$("div.form-control-feedback").remove();
    let select_id = "#m_select2_owners"
    let namespace_select_id = "#namespace_select_in_modal"
    get_user_list(select_id)
    get_namespaces(namespace_select_id)
    $("#modal_new_strategy").removeData("bs.modal").modal("show");
});