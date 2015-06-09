$(document).ready(function() {
    var $btnSets = $('#responsive'),
    $btnLinks = $btnSets.find('a');

    $btnLinks.click(function(e) {
        e.preventDefault();
        $(this).siblings('a.active').removeClass("active");
        $(this).addClass("active");
        var index = $(this).index();
        $("div.user-menu>div.user-menu-content").removeClass("active");
        $("div.user-menu>div.user-menu-content").eq(index).addClass("active");
    });
});

$( document ).ready(function() {
    $("[rel='tooltip']").tooltip();

    $('.view').hover(
        function(){
            $(this).find('.caption').slideDown(250); //.fadeIn(250)
        },
        function(){
            $(this).find('.caption').slideUp(250); //.fadeOut(205)
        }
    );
});

$('#rateOrderModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var user = button.data('user') // Extract info from data-* attributes
    var order_number = button.data('order_number') //Extract info from data-* attributes
    var order_id = button.data('order_id') //Extract info from data-* attributes

    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.

    var modal = $(this)
    modal.find('#rateOrderModalLabel').text('Danos tu opinion ' + user + '!')
    modal.find('.modal-header #order-label').text('Pedido Nro. #' + order_number)
    modal.find('.modal-body #recipient-name').val(user)
    modal.find('.modal-body #message-text').val("")
    modal.find('.modal-header #order-id').val(order_id)
})

$("#sendRateOrderForm").click(function(e){
    e.preventDefault()
    var mForm = $("#rateOrderForm").serialize()

    $.ajax({
        type: "POST",
        url: "{% url 'ajax_rate_order' %}",
        data: mForm,
        success: function(data){
            console.log(data)
            $("#rateOrderModalMessage").html("<p>" + data + "</p>")
            $("#rateOrderModal").modal("hide");
        },
        error: function(data){
            // console.log(data)
            // console.log(data.responseJSON)
            var obj = data.responseJSON
            // console.log(obj)
            // console.log(obj.email)
            $("#rateOrderModalMessage").html("<p style='color:red;'>" + obj + "</p>")
        },
    });
});

var $star_rating = $('.star-rating .fa');
var rating_text = "";

var SetRatingStar = function() {
    return $star_rating.each(function() {
        if (parseInt($star_rating.siblings('input.rating-value').val()) >= parseInt($(this).data('rating'))) {
            return $(this).removeClass('fa-star-o').addClass('fa-star');
        } else {
            return $(this).removeClass('fa-star').addClass('fa-star-o');
        }
    });
};

$star_rating.on('click', function() {
    $star_rating.siblings('input.rating-value').val($(this).data('rating'));
    switch($(this).data('rating')) {
        case 1:
            rating_text = "Muy Mal";
            break;
        case 2:
            rating_text = "Mal";
            break;
        case 3:
            rating_text = "Normal";
            break;
        case 4:
            rating_text = "Muy Bueno!";
            break;
        case 5:
            rating_text = "Excelente!";
            break;
    }
    $('#ratingLabel').text(rating_text);

    return SetRatingStar();
});

SetRatingStar();

/**
 * Created by oswaldomaestra on 5/28/15.
 */
