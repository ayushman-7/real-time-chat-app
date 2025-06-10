import streamlit as st
import socketio
import time
import queue

# Initialize session state first
if not hasattr(st.session_state, 'initialized'):
    st.session_state.messages = []
    st.session_state.username = None
    st.session_state.connected = False
    st.session_state.event_queue = queue.Queue()
    st.session_state.user_list = []
    st.session_state.initialized = True

# Initialize Socket.IO client after session state
sio = socketio.Client(logger=True, engineio_logger=True)

# Socket.IO event handlers
@sio.event
def connect():
    st.session_state.event_queue.put(("connect", "Connected to server"))
    st.session_state.connected = True

@sio.event
def disconnect():
    st.session_state.event_queue.put(("disconnect", "Disconnected from server"))
    st.session_state.connected = False

@sio.event
def message(data):
    st.session_state.event_queue.put(("message", data))

@sio.event
def user_list(data):
    st.session_state.event_queue.put(("user_list", data))

# Connect to the backend with retries
def connect_with_retries(max_attempts=5, delay=2):
    # Ensure session state is initialized before connecting
    if not hasattr(st.session_state, 'event_queue'):
        st.session_state.event_queue = queue.Queue()
    for attempt in range(max_attempts):
        try:
            sio.connect('http://backend:8000', transports=['websocket', 'polling'])
            return True
        except Exception as e:
            st.session_state.event_queue.put(("warning", f"Connection attempt {attempt + 1}/{max_attempts} failed: {str(e)}"))
            time.sleep(delay)
    st.session_state.event_queue.put(("error", "Could not connect to server after multiple attempts"))
    return False

# Process queued events in the main thread
def process_queue():
    try:
        while not st.session_state.event_queue.empty():
            event_type, data = st.session_state.event_queue.get()
            if event_type == "connect":
                st.write(data)
            elif event_type == "disconnect":
                st.write(data)
            elif event_type == "message":
                st.session_state.messages.append(data)
            elif event_type == "user_list":
                st.session_state.user_list = data
            elif event_type == "warning":
                st.warning(data)
            elif event_type == "error":
                st.error(data)
    except Exception as e:
        st.error(f"Error processing queue: {str(e)}")

# Attempt connection if not connected
if not st.session_state.connected:
    connect_with_retries()

# Process queued events
process_queue()

# Streamlit UI
st.title("Real-Time Chat with LLM")

# Username input
if not st.session_state.username:
    username = st.text_input("Enter your username:")
    if st.button("Set Username") and st.session_state.connected:
        if username:
            st.session_state.username = username
            sio.emit('set_username', {'username': username})
            st.rerun()
    elif not st.session_state.connected:
        st.warning("Cannot set username: Not connected to server")
else:
    st.write(f"Logged in as: {st.session_state.username}")

# Display user list
if st.session_state.user_list:
    st.subheader("Online Users")
    for user in st.session_state.user_list:
        st.write(user['username'] or 'Anonymous')

# Chat interface
st.subheader("Chat")
message = st.text_input("Your message:")
if st.button("Send") and st.session_state.connected:
    if message:
        sio.emit('message', {'message': message})
        st.rerun()
elif not st.session_state.connected:
    st.warning("Cannot send message: Not connected to server")

# Display messages
for msg in st.session_state.messages:
    st.write(f"**{msg['username']}**: {msg['message']}")
    st.write(f"**LLM**: {msg['llm_response']}")

# Trigger rerun if new events are queued
if not st.session_state.event_queue.empty():
    process_queue()
    st.rerun()