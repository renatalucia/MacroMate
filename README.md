# Macro Mate - an AI Diet Assistant

This repository hosts the code for an AI-based web application designed to assist users in achieving their dietary goals. The application computes personalized energetic and macronutrient requirements, generates tailored diet plans, and allows for dynamic customization through a chatbot interface.

## Key Features

### Personalized Diet Generation
- Calculates user-specific energetic and macronutrient needs.
- Generates diet plans using a template-based approach for reliability and consistency.
- Option to create diets from a collection of recipes.

### Integrated Nutrition Data
- Connects to Open Food Facts to fetch accurate and reliable nutritional values.

### Interactive Chatbot
- Enables users to refine and adapt their diet plans according to their preferences in real time.

### Modern Web Interface
- Developed using Streamlit for an intuitive and seamless user experience.

## Technical Stack
- **Generative AI**: Powered by LangChain to generate and adapt diet plans.
- **Frontend**: Built with Streamlit for quick and interactive interfaces.
- **Backend**: Python-based logic for energy and macro computations, integrated with Open Food Facts API.
- **Containerization**: Fully containerized with Docker for consistent and scalable deployment.

## Getting Started

### Prerequisites
- Python 3.9+
- Docker

### Installation

#### Clone the repository:
```bash
git clone  https://github.com/renatalucia/MacroMate.git
cd MacroMate 
```
#### Edit the config.json file inside the \app folder to include your API KEYS.

#### Build the Docker container:
```bash
docker build -t streamlit .
```

#### Run the application:
```bash
docker run -p 8501:8501 streamlit
```

#### Open the application:
Access the app at http://localhost:8501.

