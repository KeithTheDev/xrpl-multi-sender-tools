import asyncio
import csv
import json
import os
from typing import List, NamedTuple

import pandas as pd
from dotenv import load_dotenv
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.models.requests import AccountLines

# Load environment variables
load_dotenv()


class WalletStatus(NamedTuple):
    address: str
    has_trustline: bool


class TrustLineChecker:
    def __init__(self, websocket_url: str, token_issuer: str, token_currency: str):
        self.websocket_url = websocket_url
        self.token_issuer = (
            token_issuer.split(".")[-1] if "." in token_issuer else token_issuer
        )
        self.token_currency = token_currency
        self.client = None

    async def connect(self):
        """Establish connection to XRPL"""
        print(f"Connecting to {self.websocket_url}...")
        self.client = AsyncWebsocketClient(self.websocket_url)
        await self.client.open()
        print("Connected to XRPL")
        print(f"Checking for token: {self.token_currency}")
        print(f"Issuer address: {self.token_issuer}")

    async def check_trustline(self, wallet_address: str) -> bool:
        """Check if wallet has trustline for the specified token"""
        try:
            request = AccountLines(account=wallet_address)
            response = await self.client.request(request)

            if "error" in response.result:
                print(f"Error response for {wallet_address}: {response.result}")
                return False

            lines = response.result.get("lines", [])
            
            print(f"\n=== Trust lines for {wallet_address} ===")
            if not lines:
                print("No trust lines found")
            else:
                print(f"Found {len(lines)} trust lines:")
                for idx, line in enumerate(lines, 1):
                    print(f"\nTrust Line #{idx}:")
                    print(f"Currency: {line.get('currency', 'N/A')}")
                    print(f"Issuer: {line.get('account', 'N/A')}")
                    print(f"Balance: {line.get('balance', 'N/A')}")
                    print(f"Limit: {line.get('limit', 'N/A')}")
                    print("-" * 50)

                    # Check if this is our target token
                    if (line.get("account") == self.token_issuer and 
                        line.get("currency") == self.token_currency):
                        print("⭐ This is our target token!")

            # After showing debug info, check for the trust line
            for line in lines:
                if (
                    line.get("account") == self.token_issuer
                    and line.get("currency") == self.token_currency
                ):
                    limit = line.get("limit", "0")
                    return limit != "0"
            return False

        except Exception as e:
            print(f"Error checking trustline for {wallet_address}: {str(e)}")
            return False

    async def check_wallets(self, wallets: List[str]) -> List[WalletStatus]:
        """Check trustlines for multiple wallets"""
        results = []
        for wallet in wallets:
            has_trustline = await self.check_trustline(wallet)
            results.append(WalletStatus(wallet, has_trustline))
            status = "✅" if has_trustline else "❌"
            print(f"\nWallet: {wallet} - Trustline: {status}")
            print("-" * 80)  # Separator for readability
        return results

    async def close(self):
        """Close the connection"""
        if self.client:
            await self.client.close()
            print("\nConnection closed")


def load_wallets(csv_path: str) -> List[str]:
    """Load wallet addresses from CSV file"""
    try:
        wallets = []
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            if 'address' not in reader.fieldnames:
                raise ValueError("CSV file must have a column named 'address'")
            
            for row in reader:
                address = row['address'].strip()
                if address:  # Only add non-empty addresses
                    wallets.append(address)
                    
        if not wallets:
            raise ValueError("No wallet addresses found in CSV file")
            
        print(f"Loaded {len(wallets)} wallet addresses from {csv_path}")
        return wallets
        
    except FileNotFoundError:
        raise Exception(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")


def save_results(results: List[WalletStatus], output_file: str):
    """Save results to CSV with clear TRUE/FALSE indicators"""
    df = pd.DataFrame(
        [
            {
                "address": r.address,
                "has_trustline": "TRUE" if r.has_trustline else "FALSE",
            }
            for r in results
        ]
    )
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")


async def main():
    # Load configuration
    websocket_url = os.getenv("XRPL_WEBSOCKET_URL")
    token_issuer = os.getenv("TOKEN_ISSUER")
    token_currency = os.getenv("TOKEN_CURRENCY")
    input_csv = os.getenv("INPUT_CSV", "wallets.csv")
    output_csv = os.getenv("OUTPUT_CSV", "trustline_status.csv")

    if not all([websocket_url, token_issuer, token_currency]):
        print("Error: Missing required environment variables.")
        print(
            "Please ensure XRPL_WEBSOCKET_URL, TOKEN_ISSUER, and TOKEN_CURRENCY are set in .env"
        )
        return

    print(f"\nChecking trustlines for {token_currency} token issued by {token_issuer}")
    print("-" * 80)

    try:
        # Load wallets from CSV
        wallets = load_wallets(input_csv)

        # Initialize and run checker
        checker = TrustLineChecker(websocket_url, token_issuer, token_currency)
        await checker.connect()

        results = await checker.check_wallets(wallets)

        # Save and display summary
        save_results(results, output_csv)

        trustlines_count = sum(1 for r in results if r.has_trustline)
        wallets_without_trustlines = [r.address for r in results if not r.has_trustline]
        
        print("\nFinal Summary:")
        print(f"Total wallets checked: {len(results)}")
        print(f"Wallets with trustline: {trustlines_count}")
        print(f"Wallets without trustline: {len(results) - trustlines_count}")
        
        if wallets_without_trustlines:
            print("\nWallets missing trust lines:")
            for idx, wallet in enumerate(wallets_without_trustlines, 1):
                print(f"{idx}. {wallet}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if "checker" in locals():
            await checker.close()


if __name__ == "__main__":
    asyncio.run(main())