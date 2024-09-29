$(document).ready(function () {
    $("#login-form").on("submit", function (e) {
        e.preventDefault();
        var cityname = $("#cityname").val();
        var citycode = $("#citycode").val();

        $.ajax({
            url: "/visit",
            method: 'POST',
            data: { cityname: cityname, citycode: citycode },
            xhrFields: {
                withCredentials: true
            },
            success: function () {
                window.location.href = "/";
            },
            error: function (err) {
                showError(err.responseJSON.error);
            }
        });
    });

    function showError(message) {
        $("#error-text").text(message);
        $("#error-alert").show();
    }
});
