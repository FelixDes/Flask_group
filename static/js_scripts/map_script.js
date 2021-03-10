ymaps.ready(init);
function init(){
            var myMap = new ymaps.Map("map", {
                center: [51.661155, 39.207532],
                zoom: 15
            });
        }

 $('html, body').stop().animate({
    'scrollTop': $target.offset().top - 100
 }, 900, 'swing', function () {
    window.location.hash = target;
 });