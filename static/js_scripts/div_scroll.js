function scrollToBottom (id) {
   var div = document.getElementById(id);
   div.scrollTop = div.scrollHeight - div.clientHeight;
   var btn = document.getElementById('scrollToBottom_btn');
   btn.style.visibility = 'hidden';
}
function button_Activation(id){
    var div = document.getElementById(id);
   var btn = document.getElementById('scrollToBottom_btn');
   if (div.scrollTop != div.scrollHeight - div.clientHeight){
      btn.style.visibility = 'visible';
   }
}
//function scrollToTop (id) {
//   var div = document.getElementById(id);
//   div.scrollTop = 0;
//}
//
////Require jQuery
//function scrollSmoothToBottom (id) {
//   var div = document.getElementById(id);
//   $('#' + id).animate({
//      scrollTop: div.scrollHeight - div.clientHeight
//   }, 500);
//}
//
////Require jQuery
//function scrollSmoothToTop (id) {
//   var div = document.getElementById(id);
//   $('#' + id).animate({
//      scrollTop: 0
//   }, 500);
//}
