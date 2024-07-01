$(document).ready(function() {
    var table = $('#thingmennTable').DataTable({
        "paging": false,
        "searching": true,
        "ordering": true,
        "info": false,
        "order": [[2, 'asc']], // Order by "Nafn" column
        "columnDefs": [
            { "orderable": false, "targets": 0 }, // Disable sorting on the first column (details-control)
            { "orderable": false, "targets": 1 }  // Disable sorting on the image column
        ]
    });

    $('#thingmennTable tbody').on('click', 'td.details-control', function() {
        var tr = $(this).closest('tr');
        var row = table.row(tr);
        var thingmadurId = tr.data('id');
        var childRowsData = thingmennData[thingmadurId];

        if (row.child.isShown()) {
            row.child.hide();
            tr.removeClass('shown');
            $(this).text('➕'); // Change to plus sign when rows are hidden
        } else {
            if (childRowsData.length > 0) {
                var childTable = '<table class="thingskjol-table"><thead><tr><th>Malsnumer</th><th>Malsheiti</th><th>Skjalategund</th><th>Útbyting</th></tr></thead><tbody>';
                childRowsData.forEach(function(child) {
                    childTable += '<tr class="child-row"><td>' + child[1] + '</td><td><a href="' + child[4] + '" target="_blank">' + child[5] + '</a></td><td>' + child[3] + '</td><td>' + child[2] + '</td></tr>';
                });
                childTable += '</tbody></table>';

                row.child(childTable).show();
                tr.addClass('shown');
                $(this).text('➖'); // Change to minus sign when rows are shown
            }
        }
    });

    // Add odd and even classes to thingmadur-row elements
    $('#thingmennTable tbody tr.thingmadur-row').each(function(index) {
        $(this).removeClass('odd even').addClass(index % 2 === 0 ? 'even' : 'odd');
    });
});
