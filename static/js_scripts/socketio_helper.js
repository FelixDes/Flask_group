var now = new Date();
$(document).ready(() => {
    $('#form_send_msg').on('submit', (e) => {
        e.preventDefault();
    });

    //Текущий URL
    const local_URL = window.location.host;
    // Подключаем сокетное соединение
    const socket = io.connect(local_URL.toString());
    //Берём текущий юзернейм из соответствующего поля
    if ($('#username').text()) {
    var username = $('#username').text();
    }
    else {
    var username = $('#username_admin').text() + '<sup>admin</sup>';
    }
    var username = username.toLowerCase()
    var username = username.charAt(0).toUpperCase() + username.slice(1);

    //Listener кнопки
    $('#send_msg').on('click', () => {
        socket.send({
            'msg': $('#message_input').val(),
            'username': username
        }); //Отправляем сообщение через сокет
        $('#message_input').val('');
    });

    //Если сообщени отправлено, то отображаем его в контейнере ul

    socket.on('message', data => {
        if (data.msg.length > 0) {
            // if (data.username === 'Service message') {
            // $('#messages').append(`<li class="text-muted"><strong>${data.username}:</strong> ${data.msg}</li>`);
            //} else {
            $('#messages').append(`<li><strong>${data.username}: </strong> ${data.msg}<sub> ${now.getHours()}:${now.getMinutes()}</sub></li>`);
            //}
            console.log('Received message');
        }
    });
});