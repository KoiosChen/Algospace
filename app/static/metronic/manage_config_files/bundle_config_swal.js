// toastr options
function Deploy(id, action) {
    let confirmButtonText;
    if (action === 0) {
        confirmButtonText = 'Yes, deny it!'
    } else if (action === 1) {
        confirmButtonText = 'Yes, issue it!'
    } else if (action === 3) {
        confirmButtonText = 'Yes, dryrun it!'
    }
    swal({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: confirmButtonText,
        cancelButtonText: 'No, cancel!',
        reverseButtons: true
    }).then(function (result) {
        let actionText;
        let actionDetail;
        if (action === 0) {
            actionText = 'Denied';
            actionDetail = 'The config is denied!'
            ConfigIssue(id, action);
        } else if (action === 1) {
            actionText = 'Accepted';
            actionDetail = 'Please wait for the callback message!'
            ConfigIssue(id, action);
        } else if (action === 3) {
            actionText = 'Dry run'
            ConfigIssue(id, action);
        }
        if (result.value) {
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

function ConfigIssue(id, action) {
    $.ajax({
        type: "POST",          //提交方式          
        url: "config_issue",  //提交的页面/方法名          
        data: JSON.stringify({"id": id, "action": action}),   //参数（如果没有参数：null）          
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            if (msg.status === 'OK') {
                $("#modal_new_namespace").modal('hide');
                bundle_config_file_table.draw(false);
                toastr.info(result.content);
            } else {
                toastr.warning(msg.content);
            }
        },
        error: function (xhr, msg, e) {
            toastr.warning("error");
        }
    });
}