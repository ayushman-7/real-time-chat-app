Real-Time Chat Application with Ollama, Socket.IO, and Streamlit
This is a real-time chat application powered by a local LLM (LLaMA 3) using Ollama, with Socket.IO for asynchronous messaging and Streamlit for the frontend. The entire system is containerized using Docker.
Prerequisites

Docker and Docker Compose
Git

Setup Instructions

Clone the repository:
git clone https://github.com/ayushman-7/real-time-chat-app.git
cd real-time-chat-app


Start the application:
docker-compose up --build


This pulls the LLaMA 3 model, builds the backend and frontend, and starts all services.


Access the application:

Open your browser and go to http://localhost:8501.
Enter a username, send messages, and interact with the LLM in real-time.



Usage

Set Username: Enter a username to join the chat.
Send Messages: Type a message and click "Send" to broadcast it and get an LLM response.
View Users: See the list of online users in real-time.

Project Structure

backend/: FastAPI + Socket.IO server for handling real-time messaging and LLM integration.
frontend/: Streamlit app for the user interface.
docker-compose.yml: Orchestrates the Ollama, backend, and frontend services.

Notes

The application uses LLaMA 3 via Ollama. You can switch to another model (e.g., Mistral) by modifying the docker-compose.yml command.
Ensure Docker has sufficient resources (RAM, CPU) to run the LLM.

Troubleshooting

If the frontend cannot connect to the backend, ensure the backend is running on http://localhost:8000.
If Ollama fails to start, check the container logs: docker logs ollama.


Built for the 21Spheres Assignment. Submitted by Ayushman Tripathi.
