$(document).ready(function() {
    getPrintQueue();

});


// From https://stackoverflow.com/questions/18405736/is-there-a-c-sharp-string-format-equivalent-in-javascript
// I like Pythons string.format() method.
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

function getPrintQueue() {
    $.ajax({
        type: "POST",
        url: "/get_print_queue_ajax",
        success: function (result) {
            updatePrintQueueTable(JSON.parse(result));
        },
        error: function (result) {
            alert(result.toString())

        }
    });
}


function updatePrintQueueTable(printQueueData){
    var tableHTML = "";
    for (queue_id in printQueueData){
        print_queue_item = printQueueData[queue_id];
        var bgcolour = "";
        if (print_queue_item.printed === true){
            bgcolour = "#c4fc9f";
        }
        tableHTML = tableHTML + "<tr bgcolor='{4}' id='queue{0}' data-target='.queue{0}'> <td>{0}</td> <td> {1} </td> <td> {2} </td> <td> {3}</td></tr>".toString().format(print_queue_item.queue_id, print_queue_item.name, print_queue_item.purchase_id, print_queue_item.printed, bgcolour);

    }
    $('#print_queue_tbody').html(tableHTML);

}


function printBadge(attendee_id) {
    $.ajax({
        type: "POST",
        url: "/add_badge_to_queue",
        data: {
            attendee_id: attendee_id,
        },
        success: function (result) {
            var cell = document.getElementById("badges-printed-" + attendee_id);
            cell.textContent = (parseInt(cell.innerText) + 1).toString()
        },
        error: function (result) {
            alert(result.toString())

        }
    });
}

function completeOrder(attendee_id) {
    $.ajax({
        type: "POST",
        url: "/complete_order",
        data: {
            attendee_id: attendee_id,
        },
        success: function (result) {
            var loc = $("#complete_button-" + attendee_id);
            loc.text("Undo order done")
            loc.removeClass("btn-info")
            loc.addClass("btn-danger")
        },
        error: function (result) {
            alert(result.toString())

        }
    });
}