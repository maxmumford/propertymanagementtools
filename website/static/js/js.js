$(document).ready(function () {
	// select2
	$('select').select2();

	// chaining selects
	$.each($('.chained'), function(propertyName, selectElement){
		selectElement = $(selectElement);
		var start_disabled = selectElement.data('chainStartDisabled');
		var autoselect = selectElement.data('chainAutoselect');

		// disable chained element
		if (start_disabled != false){
			selectElement.select2('enable', false);
		}

		// set on change to dynamically load new values and enable the original select
		var chain_from = selectElement.data('chainFrom');
		var chain_endpoint = selectElement.data('chainEndpoint');
		var chain_from_element = $('#id_' + chain_from);

		chain_from_element.on("change", function() {
		    var $this = $(this);
		    var select_value = $this.val();

		    if (select_value != ''){
		    	// tenancy selected
				selectElement.select2('enable', false);
		    	$.getJSON(chain_endpoint + '?' + chain_from + '_id=' +  select_value, function(data){
			    	selectElement.empty()
                	$.each(data, function(key, value){
	                    selectElement.append('<option value="' + key + '">' + value +'</option>');
                	});
                	if (autoselect == true){
	                	selectElement.select2("val", selectElement.children().first().val())
                	}
                	else {
	                	selectElement.select2('enable', true);
                	}
		    	});
		    }
		    else {
		    	// nothing selected so repopulate with default list
	    		$.getJSON(chain_endpoint + '?' + chain_from + '_id=' +  0, function(data){
			    	selectElement.empty()
                	$.each(data, function(key, value){
	                    selectElement.append('<option value="' + key + '">' + value +'</option>');
                	});
                	selectElement.select2("val", '')
                	selectElement.select2('enable', true);
		    	});
		    }
		});
	});
});
