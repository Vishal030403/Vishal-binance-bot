"""
Market Orders Module
Executes immediate BUY/SELL market orders on Binance USDT-M Futures.
"""

import sys
from binance.exceptions import BinanceAPIException, BinanceOrderException
from config import get_binance_client
from logger import logger
from utils import validate_symbol, validate_quantity, validate_side, format_order_response


def place_market_order(symbol: str, side: str, quantity: float) -> dict:
    """
    Place a market order on Binance Futures.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
        side: Order side (BUY or SELL)
        quantity: Order quantity
    
    Returns:
        Order response from Binance API
    
    Raises:
        BinanceAPIException: If API request fails
        ValueError: If parameters are invalid
    """
    client = get_binance_client()
    
    logger.info(f"Placing market order: {side} {quantity} {symbol}")
    
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        
        logger.info(format_order_response(order))
        logger.debug(f"Full order response: {order}")
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e.status_code} - {e.message}")
        raise
    except BinanceOrderException as e:
        logger.error(f"Binance order error: {e.status_code} - {e.message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error placing market order: {e}", exc_info=True)
        raise


def main():
    """
    CLI entry point for market orders.
    
    Usage:
        python src/market_orders.py BTCUSDT BUY 0.01
    """
    if len(sys.argv) != 4:
        print("Usage: python src/market_orders.py <SYMBOL> <SIDE> <QUANTITY>")
        print("Example: python src/market_orders.py BTCUSDT BUY 0.01")
        sys.exit(1)
    
    symbol_arg = sys.argv[1]
    side_arg = sys.argv[2]
    quantity_arg = sys.argv[3]
    
    try:
        # Validate inputs
        symbol = validate_symbol(symbol_arg)
        side = validate_side(side_arg)
        quantity = validate_quantity(quantity_arg)
        
        # Place order
        order = place_market_order(symbol, side, quantity)
        
        print(f"\n✅ Market order executed successfully!")
        print(f"Order ID: {order['orderId']}")
        print(f"Symbol: {order['symbol']}")
        print(f"Side: {order['side']}")
        print(f"Quantity: {order['origQty']}")
        print(f"Status: {order['status']}")
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation error: {e}")
        sys.exit(1)
    except BinanceAPIException as e:
        print(f"\n❌ Binance API error: {e.message}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()