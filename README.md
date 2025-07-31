# TravelPlan AI

TravelPlan AI is an intelligent travel planning tool that leverages CrewAI and Flask to help users design personalized trip itineraries. With an easy-to-use web interface, this project uses AI agents to suggest travel plans, manage destinations, and optimize trip schedules.

---

## Features

- **AI-Powered Planning:** Uses CrewAI agents for smart itinerary suggestions.
- **Web Interface:** Built with Flask for a simple, interactive user experience.
- **Customizable Trips:** Input your preferences and get tailored travel plans.
- **Modern Stack:** Python backend with HTML, CSS, and JavaScript frontend.

---

## Tech Stack

- **Backend:** Python, Flask, CrewAI
- **Frontend:** HTML, CSS, JavaScript
- **Other:** Jinja2 templates

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gaurav21s/tripplanai.git
   cd tripplanai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the Flask app using the main entry point:

```bash
python main.py
```

The application will be available at `http://127.0.0.1:5000/` by default.

---

## Project Structure

```
tripplanai/
│
├── main.py              # Main entry point to run the Flask app
├── app.py               # Additional app logic
├── flask_app.py         # Flask application setup
├── trip_agents.py       # CrewAI agent logic for planning trips
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS)
├── log_output.txt       # Logs
├── pyproject.toml       # Project metadata
└── README.md            # Project documentation
```

---

## Usage

1. Open your browser and visit `http://127.0.0.1:5000/`.
2. Enter your travel preferences (destinations, dates, etc.).
3. Let the AI generate a custom travel itinerary.
4. Review, adjust, and save your plan.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for review.

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Contact

For questions or suggestions, open an issue or contact the repository owner via GitHub.
