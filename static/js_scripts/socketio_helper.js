$(document).ready(() => {
        $('#form_send_msg').on('submit', (e) => {
            e.preventDefault();
        });

        const local_URL = window.location.host;
        const socket = io.connect(local_URL.toString());
        const username = $('#username').text();

        $('#send_msg').on('click', () => {
            socket.send({
                'msg': $('#message_input').val(),
                'username': username
            });
            $('#message_input').val('');
        });

        socket.on('message', data => {
            if (data.msg.length > 0) {
                // if (data.username === 'Service message') {
                    // $('#messages').append(`<li class="text-muted"><strong>${data.username}:</strong> ${data.msg}</li>`);
                //} else {
                    $('#messages').append(`<li><strong>${data.username}:</strong> ${data.msg}</li>`);
                //}
                console.log('Received message');
            }
        });
    });