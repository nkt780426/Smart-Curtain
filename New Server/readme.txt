Chọn Giao Thức Web Server:
Flask tích hợp một máy chủ phát triển mà bạn có thể sử dụng trong quá trình phát triển, nhưng nó không được khuyến khích sử dụng trong môi trường production. Thay vào đó, bạn nên sử dụng một máy chủ web như Gunicorn, uWSGI hoặc mod_wsgi để triển khai ứng dụng Flask.

Ví dụ với Gunicorn:
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
Ở đây, -w 4 chỉ định số lượng workers (luồng) và app:app là module:instance cho ứng dụng Flask của bạn.