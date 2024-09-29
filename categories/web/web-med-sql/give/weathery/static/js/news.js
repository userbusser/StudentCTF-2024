$(document).ready(function() {
    fetchMessages();

    $('#newsForm').on('submit', function(e) {
        e.preventDefault();
        const message = {
            newstitle: $('#newstitle').val(),
            newsbody: $('#newsbody').val(),
        };
        $.post('/news/send', message, function() {
            fetchMessages();
            $('#newstitle').val('');
            $('#newsbody').val('');
        });
    });

    function fetchMessages() {
        $.get('/news/get', function(data) {
            $('#news').empty();
            var news = data['news'].reverse(); 
            news.forEach(function(news1) {
                $('#news').append(
                    `<div class="card mt-3">
                        <div class="card-body">
                            <h5 class="card-title">${news1.newstitle}</h5>
                            <h6 class="card-subtitle mb-2 text-muted">${news1.cityname}</h6>
                            <p class="card-text">${news1.newsbody}</p>
                        </div>
                    </div>`
                );
            });
        });
    }
});
