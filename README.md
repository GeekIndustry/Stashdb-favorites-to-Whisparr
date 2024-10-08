# Stashdb-favorites-to-Whisparr

Stashdb favorites to Whisparr is a tool designed to synchronize upcoming scenes of favorites performers or studios between StashDB and Whisparr. It allows you to configure and schedule the synchronization process using a simple web interface.

## Features

- Synchronize performers and studios from StashDB to Whisparr.
- Add upcoming scenes of favorites performers or studios to Whisparr.
- Schedule auto-scan of your Stash library with your defaults settings.
- Schedule synchronization using cron jobs.
- Exclude or include specific genders, tags, and studios.
- Easy-to-use web interface for configuration.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/GeekIndustry/Stashdb-favorites-to-Whisparr.git
   cd Stashdb-favorites-to-Whisparr

2. Build the Docker image:

    ```bash
    docker-compose build

3. Start the service:

    ```bash
    docker-compose up -d

4. Access the web interface by navigating to http://localhost:5000 or http://server-ip-adress:5000 in your browser.

## Configuration

### Web Interface

You can configure the following options directly from the web interface:

- **StashDB API Key**: Your API key for StashDB.
- **Whisparr API Key**: Your API key for Whisparr.
- **Whisparr URL**: The URL of your Whisparr instance.
- **Root Folder Path**: The root folder path where media is stored.
- **Tags to Add**: Comma-separated list of tags to add to each item.
- **Cron Expression**: The cron expression for scheduling synchronization.

### Configuration File

Settings are saved in a `config.json` file located in the root of the project. You can manually edit this file if needed.

## Usage

Once the application is running, visit the web interface, configure your settings, and start the synchronization process. The cron job will automatically trigger based on your specified schedule.

![Screenshot of part 1 of the webui.](/img/webui%20part1.png)

![Screenshot of part 2 of the webui.](/img/webui%20part2.png)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bugs you encounter.

## License
This project is licensed under the MIT License. See the [LICENSE](/LICENSE.md) file for details.