$(document).ready(function() {
    $("#register-form").on("submit", function(e) {
        e.preventDefault();
        var cityname = $("#cityname").val();
        var citycode = $("#citycode").val();

        $.post("/create", { cityname: cityname, citycode: citycode })
            .done(function() {
                window.location.href = "/visit";
            })
            .fail(function(err) {
                showError(err.responseJSON.error);
            });
    });

    function showError(message) {
        $("#error-text").text(message);
        $("#error-alert").show();
    }
});
