# Introduce
This project is server app, which is apart of smart curtain system and written in Flask python.
![System Architecture](/image/System.png)
It provides APIs and websockets connect to any client app can connect and control smart curtain in their device.
# Prequisite
1. Install python 3.10 and pip
2. Create a your free HiveMQ Cloud connected to ESP32
You can create your HiveMq cloud cluster on free tier [here](https://console.hivemq.cloud/)
Create credentials with a username, password, and permissions in the Access Management tab.
![HiveMq Cloud](/image/HiveMq%20cluster.png)
**Note: Remember your username and password of your broker.**
3. Connect to your MongoDB DB
You can use MongoDB Atlas or a local MongoDB.
**Note: Remember your database URL, username, and password of Database.**
# How to Build This Project in a Local Environment
** The following instructions are for linux os. For windows use pip instead of pip3**
1. Clone this project
```bash
    git clone https://github.com/nkt780426/Smart_Curtain_BE
```
2. Create a virtual environment
```bash
    sudo apt install python3-venv
    python3.10 -m venv venv
    source venv/bin/activate
```
2. Install all dependencies
```bash
    pip3 install -r requirements.txt
```
3. Update Database and HiveMq with your configuration in .env file
4. Run project
## For linux
```bash
    python3 app.py
```
# How to expose this project to internet
**Note: Make sure you have install nodejs and npm before do this**
1. Install vercel CLI
```bash
    npm install	-g vercel
```
2. Login to vercel
```bash
    vercel login
```
3. Deploy this app
```
    vercel
```
# All APIs and Websockets to client app
A client app that wants to control the smart curtain must use these APIs and Websockets.
1. Start this app and vist [http://localhost:5000](http://localhost:5000) to see all APIs and details of it
![APIs Documentation](/image/APIs%20document.png)
2. Connect to the following websockets
- **esp32_status**
- **inform**
- **auto_mode**
# Connecting to broker
This app publishes and subscribes the follow topic to HiveMQ cloud
1. Publish messages to topics
- auto_requests (QoS = 2)
```json
{
	"auto_status": true,
	"correlation_data": "123"
}
```
- handle_requests (QoS = 2)
```json
{		
	"percent": 50,
	"correlation_data": "456"
}
```
2. Subcribe messages to topics
- esp32_status (QoS = 2)
```json
{
	"activate": true
}
```
- inform (QoS = 1)
```json
{
	"indoor":250,
	"outdoor": 400,
	"ledState": true,
	"percent": 50,
}
```
- auto_responses (QoS = 2)
```json
{
	"status": true,
	"correlation_data": "123"
}
```
- handle_responses (QoS = 2)
```json
{
	"auto_status": true,
	"correlation_data": "456"
}
```
