$(document).ready(function() {
    var create_scrap = $('#get_site');

    create_scrap.on('click', function(e) {
        $('section#scrapper #progress').addClass('active')
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:8000/",
            data: {
                "url": $("input#scrapper").val(),
                "csrfmiddlewaretoken": $(".csrf input[type='hidden']").val()
            },
            dataType: "json",
            success: function (response) {
                var cards = response.cards
                var cards_section = $('section#cards').find('.row')
                
                cards.forEach(card => {
                    cards_section.append(card);
                })

                $('section#scrapper #progress').removeClass('active')
            },
            error: function(response) {
                console.log(response)
            }
        });    
    })
})