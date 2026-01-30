"""
Limit Orders Module
Places GTC limit orders on Binance USDT-M Futures.
"""

import sys
from binance.exceptions import BinanceAPIException, BinanceOrderException
from config import get_binance_client
from logger import logger
from utils import (
    validate_symbol,
    validate_quantity,
    validate_side,
    validate_price,
    format_order_response
)


def place_limit_order(symbol: str, side: str, quantity: float, price: float) -> dict:
    """
    Place a GTC limit order on Binance Futures.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
        side: Order side (BUY or SELL)
        quantity: Order quantity
        price: Limit price
    
    Returns:
        Order response from Binance API
    
    Raises:
        BinanceAPIException: If API request fails
        ValueError: If parameters are invalid
    """
    client = get_binance_client()
    
    logger.info(f"Placing limit order: {side} {quantity} {symbol} @ {price}")
    
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='LIMIT',
            timeInForce='GTC',  # Good-Till-Cancelled
            quantity=quantity,
            price=price
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
        logger.error(f"Unexpected error placing limit order: {e}", exc_info=True)
        raise


def main():
    """
    CLI entry point for limit orders.
    
    Usage:
        python src/limit_orders.py BTCUSDT SELL 0.01 52000
    """
    if len(sys.argv) != 5:
        print("Usage: python src/limit_orders.py <SYMBOL> <SIDE> <QUANTITY> <PRICE>")
        print("Example: python src/limit_orders.py BTCUSDT SELL 0.01 52000")
        sys.exit(1)
    
    symbol_arg = sys.argv[1]
    side_arg = sys.argv[2]
    quantity_arg = sys.argv[3]
    price_arg = sys.argv[4]
    
    try:
        # Validate inputs
        symbol = validate_symbol(symbol_arg)
        side = validate_side(side_arg)
        quantity = validate_quantity(quantity_arg)
        price = validate_price(price_arg)
        
        # Place order
        order = place_limit_order(symbol, side, quantity, price)
        
        print(f"\n✅ Limit order placed successfully!")
        print(f"Order ID: {order['orderId']}")
        print(f"Symbol: {order['symbol']}")
        print(f"Side: {order['side']}")
        print(f"Quantity: {order['origQty']}")
        print(f"Price: {order['price']}")
        print(f"Status: {order['status']}")
        print(f"Time in Force: {order['timeInForce']}")
        
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