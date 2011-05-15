$(function(){
	$("input[type='text']").addClass("text");
	$("#id_firstname").focus();
	$("#id_birthdate,#id_gender").addClass("hide");
	$("#id_birthdate").before('<div class="calendar"></div>');
	$("#id_gender").before('\
    <p style="overflow: hidden;">\
      <a class="male" href="{{ request.path_info }}">Male</a>\
      <a class="female" href="{{ request.path_info }}">Female</a>\
    </p>\
	');

	// Gender select
	if ($("#id_gender").val() == "M") {
			$("a.male").css("background-color", "yellow");
	} else if ($("#id_gender").val() == "F") {
			$("a.female").css("background-color", "yellow");
	}

	$("a.male").click(function() {
		if ($("#id_gender").val() == "M") {
			$("#id_gender").val("");	
			$(this).css("background-color", "#E6E6E6");
		} else {
			$("#id_gender").val("M");	
			$(this).css("background-color", "yellow");
			$("a.female").css("background-color", "#E6E6E6");
		}
		return false;
	});

	$("a.female").click(function() {
		if ($("#id_gender").val() == "F") {
			$("#id_gender").val("");	
			$(this).css("background-color", "#E6E6E6");
		} else {
			$("#id_gender").val("F");	
			$(this).css("background-color", "yellow");
			$("a.male").css("background-color", "#E6E6E6");
		}
		return false;
	});

	// Birthdate Calendar
	var date = $("#id_birthdate").val().split("-");
  $("div.calendar").datepicker({ onSelect: updateInline, hideIfNoPrevNext: true, yearRange: "1940:2010", defaultDate: new Date(date[0],date[1] -1, date[2]) });

	function updateInline(dateStr) {
		var arrdate = dateStr.split("/");
		$("#id_birthdate").val(arrdate[2] + "-" + arrdate[0] + "-" + arrdate[1]);
	}

});
