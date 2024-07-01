$(document).ready(function() {
    // Toggle filter section
    $('#filter-tab').click(function() {
        $(this).toggleClass('active-tab');
        $('#filter-section').slideToggle();
    });

    var table = $('#malWithThingskjalTable').DataTable({
        "paging": false,
        "searching": true,
        "ordering": true,
        "info": true,
        "pageLength": 50,
        "order": [[1, 'asc']], // Order by malsnumer
        "columnDefs": [
            { "orderable": false, "targets": 0 } // Disable sorting on the first column (details-control)
        ]
    });

    $('#malWithThingskjalTable tbody').on('click', 'td.details-control', function() {
        var tr = $(this).closest('tr');
        var row = table.row(tr);
        var malsnumer = tr.data('id');
        var childRowsData = childRowData[malsnumer];

        if (row.child.isShown()) {
            row.child.hide();
            tr.removeClass('shown');
            $(this).text('➕'); // Change to plus sign when rows are hidden
        } else {
            if (childRowsData.length > 0) {
                var childTable = '<table class="thingskjol-table"><thead><tr><th>Skjalsnumer</th><th>Skjalategund</th><th>Malsheiti</th><th>Flutningsmaður</th><th>Útbyting</th></tr></thead><tbody>';
                childRowsData.forEach(function(child) {
                    childTable += '<tr class="child-row"><td>' + child.skjalsnumer + '</td><td><a href="' + child.html_thingskjal + '" target="_blank">' + child.skjalategund + '</a></td><td>' + child.malsheiti + '</td><td>' + child.flutningsmadur + '</td><td>' + child.utbyting + '</td></tr>';
                });
                childTable += '</tbody></table>';

                row.child(childTable).show();
                tr.addClass('shown');
                $(this).text('➖'); // Change to minus sign when rows are shown
            }
        }
    });

    // Add odd and even classes to mal-row elements
    $('#malWithThingskjalTable tbody tr.mal-row').each(function(index) {
        $(this).removeClass('odd even').addClass(index % 2 === 0 ? 'even' : 'odd');
    });

    // Function to populate filters
    function populateFilters() {
        var nefndSet = new Set();
        var thingflokkurSet = new Set();
        var skjalategundSet = new Set();
        var stadamalSet = new Set();

        table.rows().every(function() {
            var data = this.data();
            nefndSet.add($(this.node()).data('nefnd'));
            thingflokkurSet.add($(this.node()).data('thingflokkur'));
            skjalategundSet.add($(this.node()).data('skjalategund'));
            stadamalSet.add($(this.node()).data('stadamal'));
        });

        function createFilterOptions(set, listId, className) {
            var list = $('#' + listId);
            set.forEach(function(value) {
                if (value) {
                    list.append('<li><label><input type="checkbox" class="' + className + '" value="' + value + '"> ' + value + '</label></li>');
                }
            });
        }

        createFilterOptions(nefndSet, 'nefnd-filter-list', 'nefnd-filter');
        createFilterOptions(thingflokkurSet, 'thingflokkur-filter-list', 'thingflokkur-filter');
        createFilterOptions(skjalategundSet, 'skjalategund-filter-list', 'skjalategund-filter');
        createFilterOptions(stadamalSet, 'stadamal-filter-list', 'stadamal-filter');
    }

    // Populate filters
    populateFilters();

    // Filter function
    function filterTable() {
        table.draw();
    }

    // Event listener for checkboxes
    $(document).on('change', '.nefnd-filter, .thingflokkur-filter, .skjalategund-filter, .stadamal-filter', function() {
        filterTable();
    });

    // Custom search function to filter based on selected checkboxes
    $.fn.dataTable.ext.search.push(
        function(settings, data, dataIndex) {
            var selectedNefndir = [];
            var selectedThingflokkar = [];
            var selectedSkjalategundir = [];
            var selectedStadamal = [];

            $('.nefnd-filter:checked').each(function() {
                selectedNefndir.push($(this).val());
            });

            $('.thingflokkur-filter:checked').each(function() {
                selectedThingflokkar.push($(this).val());
            });

            $('.skjalategund-filter:checked').each(function() {
                selectedSkjalategundir.push($(this).val());
            });

            $('.stadamal-filter:checked').each(function() {
                selectedStadamal.push($(this).val());
            });

            if (selectedNefndir.length === 0 && selectedThingflokkar.length === 0 && selectedSkjalategundir.length === 0 && selectedStadamal.length === 0) {
                return true; // No filter selected, show all rows
            }

            var row = table.row(dataIndex).node();
            var nefnd = $(row).data('nefnd');
            var thingflokkur = $(row).data('thingflokkur');
            var skjalategund = $(row).data('skjalategund');
            var stadamal = $(row).data('stadamal');

            var showRow = (selectedNefndir.length === 0 || selectedNefndir.includes(nefnd)) &&
                          (selectedThingflokkar.length === 0 || selectedThingflokkar.includes(thingflokkur)) &&
                          (selectedSkjalategundir.length === 0 || selectedSkjalategundir.includes(skjalategund)) &&
                          (selectedStadamal.length === 0 || selectedStadamal.includes(stadamal));

            return showRow;
        }
    );

    // Initial filter
    filterTable();
});
