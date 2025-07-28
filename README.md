VK Account Checker - Detailed Usage Guide
Table of Contents

    Requirements

    Installation

    Preparation

    Configuration

    Running the Checker

    Understanding the Output

    Troubleshooting

    Security Notes

Requirements

    Python 3.10 or higher

    Pip package manager

    Internet connection

    VK accounts list (login:password format)

    (Optional) Proxy list for better anonymity

Installation

    First, install Python from python.org

    Install required dependencies by running:
    bash

    pip install requests colorama concurrent-log-handler xevel pysocks

    Download the script and save it as VKBrutforce_new_captcha-xevil.py

Preparation

    Create a text file named accounts.txt in the same folder as the script

        Format: login:password one per line

        Example:
        text

        +79123456000:password123
        email@example.com:qwerty

    (Optional) For proxy support:

        Create proxies.txt file

        Add proxies in format: ip:port or username:password@ip:port

        Supported proxy types: HTTP, HTTPS, SOCKS4, SOCKS5

Configuration

Edit these variables at the top of the script if needed:
python

# Basic settings
THREADS = 3               # Number of concurrent checks (3-5 recommended)
DELAY = (5, 15)           # Random delay between requests in seconds
TIMEOUT = 20              # Request timeout in seconds

# Proxy settings
USE_PROXY = False         # Set to True to enable proxy support
PROXY_TYPE = None         # 'http', 'socks4', or 'socks5'

# Captcha settings
USE_XEVEL = False         # Set to True for automatic captcha solving
XEVEL_API_KEY = "your_api_key_here"  # Your Xevel API key

Running the Checker

    Open command prompt/terminal in the script's folder

    Run the script:
    bash

    python vk_checker.py

    Follow the interactive prompts:

        Choose whether to use proxies

        Select proxy type if enabled

        Choose whether to use Xevel captcha solving

Understanding the Output

    Green messages: Valid accounts found

    Red messages: Invalid accounts or errors

    Yellow messages: Warnings or captcha requests

    Cyan messages: Progress information

Output files:

    good.txt: Working accounts (login:password:token)

    bad.txt: Non-working accounts (login:password:error)

    working_proxies.txt: Verified working proxies (if proxy enabled)

Troubleshooting

Common issues:

    SSL errors:

        Update your Python and OpenSSL

        Try using different proxies

    Connection errors:

        Check your internet connection

        Verify proxy settings

        Increase TIMEOUT value

    Captcha problems:

        Consider enabling Xevel service

        Increase delays between requests

        Reduce number of threads

    Account blocks:

        Use quality proxies

        Increase random delays

        Avoid checking too many accounts from same IP

Security Notes

    This tool is for educational purposes only

    Never use this tool to check accounts you don't own

    Store account lists securely and delete after use

    Be aware that VK may detect and block automated checks

    Using proxies is highly recommended to avoid IP bans

For optimal results:

    Use residential proxies

    Keep threads low (3-5)

    Set realistic delays (5-15 seconds)

    Rotate proxies frequently

Remember that unauthorized access to accounts is illegal in most jurisdictions. Use this tool responsibly and only on accounts you have permission to check.
