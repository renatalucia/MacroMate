AI-Powered Diet Assistant
This repository hosts the code for an AI-based web application designed to assist users in achieving their dietary goals. The application computes personalized energetic and macronutrient requirements, generates tailored diet plans, and allows for dynamic customization through a chatbot interface.

Key Features
Personalized Diet Generation:

Calculates user-specific energetic and macronutrient needs.
Generates diet plans using a template-based approach for reliability and consistency.
Option to create diets from a collection of recipes.
Integrated Nutrition Data:

Connects to Open Food Facts to fetch accurate and reliable nutritional values.
Interactive Chatbot:

Enables users to refine and adapt their diet plans according to their preferences in real time.
Modern Web Interface:

Developed using Streamlit for an intuitive and seamless user experience.
Technical Stack
Generative AI: Powered by LangChain to generate and adapt diet plans.
Frontend: Built with Streamlit for quick and interactive interfaces.
Backend: Python-based logic for energy and macro computations, integrated with Open Food Facts API.
Containerization: Fully containerized with Docker for consistent and scalable deployment.
Cloud Deployment: Designed to run on AWS, leveraging its robust infrastructure for scalability and reliability.
Getting Started
Prerequisites
Python 3.9+
Docker
AWS Account (optional, for deployment)
Installation
Clone the repository:
bash
Copy code
git clone https://github.com/<your-username>/ai-diet-assistant.git
cd ai-diet-assistant
Build the Docker container:
bash
Copy code
docker build -t ai-diet-assistant .
Run the application locally:
bash
Copy code
docker run -p 8501:8501 ai-diet-assistant
Access the app at http://localhost:8501.
Deployment on AWS
Instructions for deploying the application on AWS are provided in the deployment directory.

Contributing
Contributions are welcome! If you'd like to improve the application or add new features, feel free to open a pull request or file an issue.

