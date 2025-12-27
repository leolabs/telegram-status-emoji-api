# Telegram Emoji Status Updater

A FastAPI-based HTTP server that allows you to update your Telegram account's status emoji using Telethon.

I'm using this to let my friends know when I'm currently driving, or when I'm working.

## Getting Started

To use this script, you need to create a Telegram client on [my.telegram.org](https://my.telegram.org).

First, you'll need to log into your Telegram account to create a session file.
If you're using Docker, you can create a session file by running the following command:

```sh
docker run --rm -it \
  -e TG_API_ID=your_api_id \
  -e TG_API_HASH=your_api_hash \
  -v ./session:/app/session \
  leolabs2/telegram-status-emoji-api
```

Once you have a .session file, you can run the Docker container in the background.
Here's an example using Docker Compose:

```yaml
services:
  telegram-status-emoji-api:
    image: leolabs2/telegram-status-emoji-api
    restart: unless-stopped
    env_file: .env
    ports:
      - 8000:8000
    volumes:
      - ./session:/app/session
```

This Docker Compose file references a `.env` file with the following contents:

```env
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash
```

### Running the Script Without Docker

If you prefer to run the application directly with Python, follow these steps:

1. Clone the repository and create a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Telegram credentials:
   ```env
   TG_API_ID=your_api_id
   TG_API_HASH=your_api_hash
   ```

4. Run the application:
   ```sh
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

The first time you run the application, it will prompt you for your phone number and the verification
code sent by Telegram. This will create a session file that will be used for subsequent runs.

## Securing the Endpoints

You can specify an API key using the `API_KEY` environment variable. When this is set,
all requests to the API need to be authorized using an `Authorization: Bearer` header
containing the API key.

If you're exposing this script to the internet, I'd highly recommend setting an API key.

## Available Endpoints

- `GET /current-emoji` returns the current emoji and optionally how long it will
  be displayed
- `POST /update-emoji` updates the emoji, accepts a JSON body
  - `document_id` is the ID of the emoji
  - `until` is an optional timestamp of when the emoji should be cleared
- `POST /undo-emoji` undoes the emoji change, helpful for temporary states

## Some Select Emoji Document IDs

There are hundreds of status emoji to choose from, but these are the ones I went with:

- duck-blush: `5379732256644405206`
- duck-laptop: `5444965061749644170`
- duck-sleep: `5418028873705069979`
- duck-car: `5233638613358486264`
- duck-phone: `5201990176175299013`
- duck-do-not-disturb: `5445350865776941647`
- mashup-rock: `5454112830989025752`