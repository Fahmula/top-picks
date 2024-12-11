# Top Picks Automation Script

This project automates the "Top Picks" plugin update in Emby using trending data from Trakt. The script runs inside a Docker container with dynamic scheduling powered by cron.

## Features

- Fetches trending movies and TV shows from Trakt.
- Updates Emby "Top Picks" plugin with selected media.
- Fixes issues with "Top Picks" by organizing `.nfo` metadata files into proper season folders.
- Flexible scheduling via the `CRON_SCHEDULE` environment variable.
- Logs Python script output directly to the Docker logs.

---

## Requirements

- **Docker**
- **An Emby server** with the "Top Picks" plugin installed.
- **An Emby API Key**
- **A Trakt API client**

---

## Environment Variables

These variables can be set in a `.env` file or passed directly when running the container:

| Variable          | Description                                                                | Example Value           |
|--------------------|----------------------------------------------------------------------------|-------------------------|
| `EMBY_URL`        | The URL of your Emby server (required).                                    | `http://your-emby-url`  |
| `EMBY_API_KEY`    | Your Emby API key (required).                                              | `your-emby-api-key`     |
| `TRAKT_CLIENT_ID` | Your Trakt API client ID (required).                                       | `your-trakt-client-id`  |
| `MOVIE_FOLDER_NAME` | Folder name for movies in emby library.                                  | `movies-hd`             |
| `TV_FOLDER_NAME`  | Folder name for TV shows in emby library.                                  | `tv`                   |
| `MOVIES_LIMIT`    | Number of movies to include in "Top Picks".                                | `6`                     |
| `SHOWS_LIMIT`     | Number of shows to include in "Top Picks".                                 | `3`                     |
| `CRON_SCHEDULE`   | Cron schedule for running the script. Uses standard cron syntax.           | `0 */3 * * *`           |

---

## Installation

1. **Pull the Docker image:**
   ```bash
   docker pull ghcr.io/fahmula/top-picks:latest
   ```

2. **Setup environment variables:**
   Create a `.env` file with the following contents:
   ```env
   EMBY_URL=http://192.168.1.6:8096
   EMBY_API_KEY=your-emby-api-key
   TRAKT_CLIENT_ID=your-trakt-client-id
   MOVIE_FOLDER_NAME=movies-hd
   TV_FOLDER_NAME=tv
   MOVIES_LIMIT=6
   SHOWS_LIMIT=3
   CRON_SCHEDULE=0 */3 * * *  # Runs every 3 hours
   ```

3. **Mount the Emby data Top Picks folder:**
   Ensure that /emby/data/top-picks folder is mounted to `/media` in the container.

---

## Scheduling

The `CRON_SCHEDULE` environment variable allows you to control when the script runs. It uses standard cron syntax:

| Schedule            | Cron Syntax   |
|---------------------|---------------|
| Every 3 hours       | `0 */3 * * *` |
| Daily at midnight   | `0 0 * * *`   |
| Every 15 minutes    | `*/15 * * * *`|

Logs for cron jobs are stored in `/var/log/cron.log` and streamed to the Docker logs.

---

## Example `docker-compose.yml`

```yaml
version: "3.8"

services:
  top-picks:
    image: ghcr.io/fahmula/top-picks:latest
    container_name: top_picks
    environment:
      - EMBY_URL=http://192.168.1.5:8096
      - EMBY_API_KEY=your-emby-api-key
      - TRAKT_CLIENT_ID=your-trakt-client-id
      - MOVIE_FOLDER_NAME=movies-hd
      - TV_FOLDER_NAME=tv
      - MOVIES_LIMIT=6
      - SHOWS_LIMIT=3
      - CRON_SCHEDULE=0 */3 * * *  # Runs every 3 hours
    volumes:
      - /mnt/cache/appdata/emby/data/top-picks:/media  # Mount your Emby "Top Picks" path to /media
    restart: unless-stopped
```

---

## Verifying the Setup

1. **Check Docker logs:**
   ```bash
   docker logs -f top_picks
   ```

2. **Verify Cron Job:**
   Enter the container and check if the cron job is active:
   ```bash
   docker exec -it top_picks crontab -l
   ```

3. **Check Metadata Updates:**
   Ensure that your Emby "Top Picks" is updated with trending content.

---

## Development and Testing

For local development without Docker:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the script manually:**
   ```bash
   python app.py
   ```

---

## Contributing

Contributions are welcome! Feel free to fork this repository, submit issues, or open pull requests.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---
