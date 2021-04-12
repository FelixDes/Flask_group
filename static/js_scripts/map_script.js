ymaps.ready(init);

function init() {
    var myMap = new ymaps.Map("map", {
        center: [51.656677, 39.206890],
        zoom: 16
    });
}

$('html, body').stop().animate({
    'scrollTop': $target.offset().top - 100
}, 900, 'swing', function () {
    window.location.hash = target;
});