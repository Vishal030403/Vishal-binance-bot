"""
Stop-Limit Orders Module
Places stop-limit orders that trigger a limit order when stop price is reached.
Compatible with Binance USDT-M Futures.
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


def place_stop_limit_order(
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
    limit_price: float
) -> dict:
    """
    Place a stop-limit order on Binance Futures.
    
    When the stop price is reached, a limit order is placed at the limit price.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
        side: Order side (BUY or SELL)
        quantity: Order quantity
        stop_price: Price that triggers the limit order
        limit_price: Limit price for the triggered order
    
    Returns:
        Order response from Binance API
    
    Raises:
        BinanceAPIException: If API request fails
        ValueError: If parameters are invalid
    """
    client = get_binance_client()
    
    logger.info(
        f"Placing stop-limit order: {side} {quantity} {symbol} | "
        f"Stop: {stop_price}, Limit: {limit_price}"
    )
    
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='STOP',  # Stop-limit order type for Futures
            timeInForce='GTC',
            quantity=quantity,
            price=limit_price,
            stopPrice=stop_price
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
        logger.error(f"Unexpected error placing stop-limit order: {e}", exc_info=True)
        raise


def main():
    """
    CLI entry point for stop-limit orders.
    
    Usage:
        python src/advanced/stop_limit.py BTCUSDT SELL 0.01 51000 50800
        
    This places a SELL stop-limit order that:
    - Triggers when price drops to 51000 (stop price)
    - Places a limit sell order at 50800 (limit price)
    """
    if len(sys.argv) != 6:
        print("Usage: python src/advanced/stop_limit.py <SYMBOL> <SIDE> <QUANTITY> <STOP_PRICE> <LIMIT_PRICE>")
        print("Example: python src/advanced/stop_limit.py BTCUSDT SELL 0.01 51000 50800")
        print("\nExplanation:")
        print("  STOP_PRICE: Price that triggers the limit order")
        print("  LIMIT_PRICE: Price at which the limit order will be placed")
        sys.exit(1)
    
    symbol_arg = sys.argv[1]
    side_arg = sys.argv[2]
    quantity_arg = sys.argv[3]
    stop_price_arg = sys.argv[4]
    limit_price_arg = sys.argv[5]
    
    try:
        # Validate inputs
        symbol = validate_symbol(symbol_arg)
        side = validate_side(side_arg)
        quantity = validate_quantity(quantity_arg)
        stop_price = validate_price(stop_price_arg)
        limit_price = validate_price(limit_price_arg)
        
        # Place order
        order = place_stop_limit_order(symbol, side, quantity, stop_price, limit_price)
        
        print(f"\n✅ Stop-limit order placed successfully!")
        print(f"Order ID: {order['orderId']}")
        print(f"Symbol: {order['symbol']}")
        print(f"Side: {order['side']}")
        print(f"Type: {order['type']}")
        print(f"Quantity: {order['origQty']}")
        print(f"Stop Price: {order['stopPrice']}")
        print(f"Limit Price: {order['price']}")
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