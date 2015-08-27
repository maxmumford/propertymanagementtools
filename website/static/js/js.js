$(document).ready(function () {
	// select2
	$('select').select2();

	// chaining selects
	$.each($('.chained'), function(propertyName, selectElement){
		selectElement = $(selectElement);
		var startEnabled = selectElement.data("chainStartEnabled");
		var chain_from = selectElement.data('chainFrom');
		var chain_endpoint = selectElement.data('chainEndpoint');
		var chain_from_element = $('#id_' + chain_from);

		// disable the element because something else must be selected first
		if (startEnabled != true){
			selectElement.select2('enable', false)
			$($('#id_building').closest('form')[0]).on('submit', function(){
				selectElement.prop('disabled', false)
			});
		}

		// set on change to dynamically load new values when chain_from changes
		chain_from_element.on("change", function() {
		    var selected_value = $(this).val();

		    if (startEnabled == true){
		    	// disable during ajax
		    	selectElement.prop('disabled', true);
		    }

		    // prepare values for ajax call
		    if (selected_value == ''){
		    	selected_value = '0';
		    }
		    var ajax_url = chain_endpoint + '?' + chain_from + '_id=' +  selected_value;

	    	$.getJSON(ajax_url, function(data){
	    		// empty the select and add a blank and the returned options
		    	selectElement.empty();
	    		selectElement.append('<option value="" selected="selected">---------</option>');

            	$.each(data, function(key, value){
                    selectElement.append('<option value="' + key + '">' + value +'</option>');
            	});

            	// auto select if returned just 1 option, otherwise deselect
            	var data_count = $.map(data, function(n, i) { return i; }).length;
            	if (data_count == 1){
		    		selectElement.select2("val", selectElement.children('option').last().val())
		    	}
		    	else {
		    		selectElement.select2("val", selectElement.children('option').first().val())
		    	}

		    	// enable if startEnabled or more than 1 option returned
		    	if (startEnabled == true || data_count > 1){
		    		selectElement.select2('enable', true);
		    	}
	    	});
		});
	});

});
