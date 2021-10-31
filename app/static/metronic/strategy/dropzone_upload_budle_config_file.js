//== Class definition

var DropzoneUploadBundleConfigFile = function () {
    //== Private functions
    let upload_bundle_config_file = function () {
        // file type validation
        Dropzone.options.mDropzone = {
            paramName: "file", // The name that will be used to transfer the file
            maxFiles: 1,
            maxFilesize: 2000, // MB
            addRemoveLinks: true,
            autoProcessQueue: false,
            parallelUploads: 100,
            timeout: 300000,
            acceptedFiles: ".tar, .tgz, .tar.gz, .zip",
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
                console.log('bundle config file has been upload to fdfs');

                let deploy_reason = $('#apply_reason').val();
                let app_id = $("#app_id").val();

                let params = {
                    "deploy_reason": deploy_reason,
                    "app_id": app_id
                };

                console.log(params);

                $.ajax({
                    type: "POST",
                    url: "submit_bundle_deploy",
                    data: JSON.stringify(params),
                    dataType: 'json',
                    contentType: 'application/json; charset=UTF-8',
                    success: function (result) {
                        if (result.status === 'true') {
                            mApp.unblock('#modal_transfer .modal-content');
                            $("#modal_new_bundle_config").modal('hide');
                            bundle_config_file_table.draw(false);
                            toastr.info(result.content);
                            //setTimeout("location.reload()", 1000);
                        } else {

                            mApp.unblock('#modal_transfer .modal-content');
                            $('#modal_new_bundle_config').modal('hide');
                            toastr.warning(result.content);
                        }

                    },
                    error: function (xhr, msg, e) {
                        mApp.unblock('#modal_transfer .modal-content');
                        $('#modal_new_bundle_config').modal('hide');
                        toastr.warning("系统繁忙");
                    }
                });
            }
        };
    };

    return {
        // public functions
        init: function () {
            upload_bundle_config_file();
        }
    };
}();

DropzoneUploadBundleConfigFile.init();