# Discord Bot Setup Guide

## Prerequisites
Before setting up the bot, ensure you have the following installed:

- [Python 3.9+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [pip (Python package manager)](https://pip.pypa.io/en/stable/)
- [Virtual Environment (venv)](https://docs.python.org/3/library/venv.html)

## Installation Steps

### 1. Clone the Repository
```sh
git clone https://github.com/BlazingFury3008/renfieldbot_v2
cd your-bot
```

### 2. Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Create a `.env` File
Create a `.env` file in the root directory of the project and add the following environment variables:

```ini
# Discord Bot Token
DISCORD_TOKEN="your-discord-bot-token"

# Log Directory
LOG_HOME="./logs"

# Database Credentials
DATABASE_USERNAME="your-database-username"
DATABASE_PASSWORD="your-database-password"

# Encryption Key
ENCRYPTION_KEY="your-encryption-key"

# Required Roles
REQUIRED_ROLES="Admin,RenfieldTest"

# OpenAI API Configuration (if applicable)
GPT_API_URL=""
OPENAI_API_KEY="your-openai-api-key"
OPENAI_MODEL="gpt-4o-mini"
OPENAI_SYSTEM_CONTENT=""

# Default Voice Channel ID
DEFAULT_VOICE_CHANNEL_ID="your-voice-channel-id"
```

### 5. Run the Bot
Once the `.env` file is set up, start the bot using:
```sh
python bot.py
```

### 6. Running the Bot in Development Mode
For active development, you can use:
```sh
python -m bot
```

### 7. Troubleshooting
- **Issue: Bot doesn't start**
  - Ensure the `.env` file is correctly formatted and all required values are set.
  - Verify that your `DISCORD_TOKEN` is valid.

- **Issue: Permissions error**
  - Ensure the bot has necessary permissions in the Discord server.

- **Issue: Dependencies not installed correctly**
  - Try running `pip install --upgrade -r requirements.txt`.


### Contributing
If you'd like to contribute to this project, feel free to submit a pull request.

### License
This project is licensed under the MIT License.

---

Your bot should now be up and running! 🚀 If you encounter any issues, check the logs or ask for support in the relevant community forums.

