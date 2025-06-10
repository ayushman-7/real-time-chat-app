from fastapi import FastAPI
import socketio
import ollama
import asyncio

# Initialize FastAPI and Socket.IO
app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)  # Create Socket.IO ASGI app

# Mount Socket.IO app explicitly
app.mount("/socket.io", socket_app)

# Store connected users
users = {}

@sio.event
async def connect(sid, environ):
    print(f"User connected: {sid}")
    users[sid] = {"username": None}
    await sio.emit('user_list', list(users.values()), skip_sid=sid)

@sio.event
async def disconnect(sid):
    print(f"User disconnected: {sid}")
    del users[sid]
    await sio.emit('user_list', list(users.values()))

@sio.event
async def set_username(sid, data):
    username = data.get('username', 'Anonymous')
    users[sid]['username'] = username
    await sio.emit('user_list', list(users.values()))

@sio.event
async def message(sid, data):
    username = users[sid]['username'] or 'Anonymous'
    user_message = data.get('message', '')

    # Send message to LLM
    response = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': user_message}]
    )
    llm_response = response['message']['content']

    # Broadcast message and LLM response
    await sio.emit('message', {
        'username': username,
        'message': user_message,
        'llm_response': llm_response
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run FastAPI app with Socket.IO mounted