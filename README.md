# BookBeats

BookBeats creates personalized reading soundtracks by combining your Spotify listening history with the book you're currently reading.

## Tech Stack

*   **Frontend:** HTML, TailwindCSS, Jinja2Templates
*   **Backend:** FastAPI
*   **APIs:** Spotify Web API, Open Library API

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the required Python dependencies:
   ```bash
   pip install fastapi uvicorn jinja2 requests
   ```

## Usage

Start the local development server:
```bash
uvicorn main:app --reload
```
Open your browser and navigate to `http://127.0.0.1:8000`.

## Key Features

*   **Automatic Song Selection:** Instantly pairs your current book's mood with matching Spotify tracks.
*   **Pages Per Minute (PPM):** Tracks your real-time reading pace to sync audio transitions.
*   **TBR List:** A built-in "To-Be-Read" queue to organize your next literary adventures.

## Additional Features

*   **Evaluate Reading Habits:**
    *   **Book Counter:** Tracks total books read across weeks, months, and years.
    *   **Insights:** Highlights your most-read authors.
    *   **Reading Streak:** Displays consecutive days spent reading to keep you motivated.
    *   **Packages:** Send book recommendations to your friends.