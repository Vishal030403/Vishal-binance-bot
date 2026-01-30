"""
Configuration module for Binance Futures client initialization.
Loads API credentials from environment variables and creates client instance.
"""

import os
from pathlib import Path
from typing import Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
from logger import logger


class BinanceConfig:
    """Manages Binance API configuration and client initialization."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load .env file from project root
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.use_testnet = os.getenv('USE_TESTNET', 'True').lower() == 'true'
        
        self._validate_credentials()
        self.client: Optional[Client] = None
    
    def _validate_credentials(self) -> None:
        """
        Validate that API credentials are present.
        
        Raises:
            ValueError: If API credentials are missing
        """
        if not self.api_key or not self.api_secret:
            error_msg = (
                "Missing API credentials. Please set BINANCE_API_KEY and "
                "BINANCE_API_SECRET in your .env file."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if self.api_key == 'your_api_key_here' or self.api_secret == 'your_api_secret_here':
            error_msg = (
                "Please replace placeholder API credentials in .env file with "
                "your actual Binance API key and secret."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_client(self) -> Client:
        """
        Get or create Binance Futures client instance.
        
        Returns:
            Configured Binance Client instance
        """
        if self.client is None:
            try:
                self.client = Client(
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    testnet=self.use_testnet
                )
                
                # Test connection
                self.client.futures_ping()
                
                mode = "TESTNET" if self.use_testnet else "MAINNET"
                logger.info(f"Successfully connected to Binance Futures {mode}")
                
            except BinanceAPIException as e:
                logger.error(f"Binance API error during client initialization: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error during client initialization: {e}")
                raise
        
        return self.client


# Global configuration instance
config = BinanceConfig()


def get_binance_client() -> Client:
    """
    Convenience function to get the Binance client.
    
    Returns:
        Configured Binance Client instance
    """
    return config.get_client()