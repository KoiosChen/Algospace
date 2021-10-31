function delete_target(rows, btn_id) {
    $.ajax({
        type: "POST",          //提交方式          
        url: btn_id,  //提交的页面/方法名      
        data: JSON.stringify(rows, null, '\t'),//     
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            if (msg.status === 'OK') {
                toastr.info(msg.content)
                if (btn_id === 'delete_strategy') {
                    strategy_table.ajax.reload()
                }
                else if(btn_id === "delete_instance") {
                    childTable.ajax.reload()
                }
                else if(btn_id === "delete_file") {
                    grandChildTable.ajax.reload()
                }

            } else {
                toastr.warning(msg.content);
            }
        },
        error: function (xhr, msg, e) {
            toastr.warning("error");
        }
    });
}