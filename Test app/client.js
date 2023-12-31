const io = require('socket.io-client');

// Thay thế 'http://localhost:5000' bằng URL thực tế của Flask-SocketIO server của bạn
const socket = io('http://localhost:5000');

// Kết nối thành công
socket.on('connect', () => {
    console.log('Connected to server');
});

// Nhận thông điệp từ sự kiện 'inform'
socket.on('inform', (data) => {
    console.log('Received inform message:', data);
});

// Nhận thông điệp khi chế độ auto tắt
socket.on('auto_mode', (data) => {
    console.log('Received inform message:', data);
});

socket.on('esp32_status', (data) => {
    //xử lý nó sập kiểu redirecrt nó đến 1 trang nào khác
    console.log('Received inform message:', data);
    // Nhận về 2 thông điệp true hoặc false
});


// Xử lý sự kiện khi mất kết nối
socket.on('disconnect', () => {
    console.log('Disconnected from server');
});
