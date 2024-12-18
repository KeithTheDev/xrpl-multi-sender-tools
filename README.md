# XRPL Trust Line Checker

A Python utility for verifying XRPL fungible token trust lines across multiple wallet addresses. This tool helps token issuers and project managers efficiently verify which wallets have established trust lines for their tokens.

## Features

- Batch checking of multiple wallet addresses
- Support for hex-encoded currency codes
- Detailed trust line information for each wallet
- CSV input and output
- Summary reporting with failed trust line identification

## Prerequisites

- Python 3.8 or higher
- Git
- Active internet connection

## Installation

1. Clone the repository and set up environment:

    ```bash
    git clone git@github.com:yourusername/xrpl-trustline-checker.git
    cd xrpl-trustline-checker
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2. Create a `.env` file: 

    ```env
    XRPL_WEBSOCKET_URL=wss://xrplcluster.com
    TOKEN_ISSURER=rYourTokenIssuerAddress
    TOKEN_CURRENCY=YourHexEncodedCurrencyCode
    INPUT_CSV=wallets.csv
    OUTPUT_CSV=trustline_status.csv
    ```
3. Create your input CSV file (wallets.csv):

    ```csv
    address
    rWalletAddress1
    rWalletAddress2
    ```

## Usage

1. Activate virtual environment (if not already activated):

    ```bash
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2. Run the checker:

    ```bash
    python check_trustlines.py
    ```

The script will:

- Check each wallet for trust lines
- Display real-time results
- Generate a summary of findings
- Create a CSV report with results

## Output

The tool provides:

- Console output showing real-time checking progress
- Summary of trust line status
- List of wallets missing trust lines
- CSV file with complete results

Example console output:
    
    ```text
    Final Summary:
    Total wallets checked: 50
    Wallets with trustline: 45
    Wallets without trustline: 5
    
    Wallets missing trust lines:
    1. rWallet1
    2. rWallet2
    ...
    ```

## Configuration Notes

- For custom tokens longer than 3 characters, use hex-encoded currency code
- Ensure trustline issuer address is correct
- Use mainnet node URL (wss://xrplcluster.com) for production checks

## Support

If you encounter any issues:

1. Verify your .env configuration
2. Check your input CSV format
3. Ensure your virtual environment is activated
4. Verify token currency code and issuer address