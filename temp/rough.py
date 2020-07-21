<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<!-- ============================================================================================ -->
	<script type="text/javascript">
		$(document).ready(function() {
		  $("#success-alert").hide();
		  $("#myWish").show(function showAlert() {
		    $("#success-alert").fadeTo(2000, 500).slideUp(500, function() {
		      $("#success-alert").slideUp(500);
		    });
		  });
		});
	</script>

	{% with messages = get_flashed_messages() %}
	  {% if messages %}
	    {% for message in messages %}
	    	<div id="myWish">
		    	<div class="alert alert-success alert-dismissible" id="success-alert">
				  <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
				  		<p >{{message}}!</p>
				</div>
		    </div>
		{% endfor %}
	  {% endif %}
	{% endwith %}
	
	<!-- ============================================================================================= -->