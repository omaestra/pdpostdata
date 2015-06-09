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

/* Rate quality of one order using Font-Awesome fonts */
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
