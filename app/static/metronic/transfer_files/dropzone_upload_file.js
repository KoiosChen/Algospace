//== Class definition

var dropzone_cutover;

var DropzoneUploadFile = function () {
    //== Private functions
    let transfer_upload_file = function () {
        // file type validation
        Dropzone.options.mDropzone = {
            paramName: "file", // The name that will be used to transfer the file
            maxFiles: 1,
            maxFilesize: 2000, // MB
            addRemoveLinks: true,
            autoProcessQueue: false,
            timeout: 9000,
            url: 'upload_inside_fdfs',
            init: function () {
                myDropzone = this;
                myDropzone.on("complete", function (file) {
                    myDropzone.removeFile(file);
                });
            },
            accept: function (file, done) {
                done();
            },
            success: function (file, done) {
                console.log('transfer from inside to outside');

                let apply_reason = $('#apply_reason').val();

                let params = {
                    "apply_reason": apply_reason,
                };

                console.log(params);

                $.ajax({
                    type: "POST",
                    url: "apply_transfer",
                    data: JSON.stringify(params),
                    dataType: 'json',
                    contentType: 'application/json; charset=UTF-8',
                    success: function (result) {
                        if (result.status === 'true') {
                            mApp.unblock('#modal_transfer .modal-content');
                            $("#modal_transfer").modal('hide');
                            $('#ajax_data').mDatatable().destroy();
                            DatatableRemoteAjaxTransferFiles.init();
                            toastr.info(result.content);
                            //setTimeout("location.reload()", 1000);
                        } else {

                            mApp.unblock('#modal_transfer .modal-content');
                            $('#modal_transfer').modal('hide');
                            toastr.warning(result.content);
                        }

                    },
                    error: function (xhr, msg, e) {
                        mApp.unblock('#modal_transfer .modal-content');
                        $('#modal_transfer').modal('hide');
                        toastr.warning("系统繁忙");
                    }
                });
            }
        };
    };

    return {
        // public functions
        init: function () {
            transfer_upload_file();
        }
    };
}();

DropzoneUploadFile.init();