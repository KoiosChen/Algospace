//== Class definition

var DatatableRemoteAjaxTransferFilesConfirm = function () {
    //== Private functions

    // basic demo
    let demo = function () {

        let datatable = $('#ajax_data').mDatatable({
            // data source definition
            data: {
                type: 'remote',
                source: {
                    read: {
                        // sample GET method
                        method: 'POST',
                        url: '/transfer_confirm_orders',
                        map: function (raw) {
                            // sample data mapping
                            var dataSet = raw;
                            if (typeof raw.data !== 'undefined') {
                                dataSet = raw.data;
                            }
                            return dataSet;
                        },
                    },
                },
                pageSize: 10,
                serverPaging: true,
                serverFiltering: true,
                serverSorting: false,
            },

            // layout definition
            layout: {
                scroll: false,
                footer: false
            },

            // column sorting
            sortable: false,

            pagination: true,

            autoWidth: true,

            toolbar: {
                // toolbar items
                items: {
                    // pagination
                    pagination: {
                        // page size select
                        pageSizeSelect: [10, 20, 30, 50, 100],
                    },
                },
            },

            // columns definition

            columns: [
                {
                    field: 'id',
                    title: '订单号',
                    sortable: false, // disable sort for this column
                    selector: false,
                    textAlign: 'center',
                }, {
                    field: 'filename',
                    title: '文件名称',
                    textAlign: 'center',
                    // sortable: 'asc', // default sort
                    filterable: false, // disable or enable filtering
                    // basic templating support for column rendering,
                    overflow: 'visible',
                    template: function (row) {
                        return '<a href="' + row.file_store_path + '"target="_Blank">' + row.filename + '</a>';
                    }
                }, {
                    field: 'apply_user',
                    title: '申请人',
                    textAlign: 'center',
                }, {
                    field: 'apply_reason',
                    title: '申请理由',
                    textAlign: 'center',
                }, {
                    field: 'apply_at',
                    title: '申请时间',
                    textAlign: 'center',
                    type: 'date',
                    format: 'YYYY/MM/DD',
                }, {
                    field: 'Actions',
                    width: 100,
                    textAlign: 'center',
                    title: '操作',
                    sortable: false,
                    overflow: 'visible',
                    template: function (row) {
                        console.log(row.id);
                        return '<a ' + 'onClick="return HTMerConfirm(\'' + row.id + '\', ' + 0 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
                                <i class="fa fa-remove"></i>\
                            </a>\
                            <a ' + 'onClick="return HTMerConfirm(\'' + row.id + '\', ' + 1 + ')" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\
                                <i class="fa fa-check"></i>\
                            </a>\
                        ';
                    },
                }],
        });
    };


    return {
        // public functions
        init: function () {
            demo();
        },
    };
}();


jQuery(document).ready(function () {
    DatatableRemoteAjaxTransferFilesConfirm.init();
});

