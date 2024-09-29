$(document).ready(function() {
    fetchMessages();

    $('#degreesUpdate').on('submit', function(e) {
        e.preventDefault();
        const message = {
            degrees: $('#degrees').val()
        };
        $.post('/profile/degrees', message, function() {
            fetchMessages(); 
            $('#degrees').val('');
        });
    });

    function fetchMessages() {
        $.get('/profile/get', function(profile) {
            $('#profile').empty();
            $('#profile').append(
                    `<div class="card mt-3">
                        <h2 class="mt-3">Cityprofile</h2>
                        <div class="card-body">
                            <h5 class="card-title">Cityname: ${profile.cityname}</h5>
                            <h6 class="card-subtitle mb-2 text-muted">Degrees: ${profile.degrees}</h6>
                        </div>
                    </div>`
                );
        });
    }
});
