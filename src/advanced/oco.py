"""
OCO-Style Orders Module
Simulates OCO (One-Cancels-Other) functionality for Binance Futures.

Since Binance Futures doesn't support classic OCO orders, this module simulates
OCO behavior by placing both a Take-Profit Market order and a Stop-Loss Market
order simultaneously. When one order is filled, the other should be manually
cancelled or managed through position risk settings.
"""

import sys
from typing import Dict, Tuple
from binance.exceptions import BinanceAPIException, BinanceOrderException
from config import get_binance_client
from logger import logger
from utils import (
    validate_symbol,
    validate_quantity,
    validate_side,
    validate_price
)


def place_oco_style_orders(
    symbol: str,
    side: str,
    quantity: float,
    take_profit_price: float,
    stop_loss_price: float
) -> Tuple[dict, dict]:
    """
    Place OCO-style orders using Take-Profit and Stop-Loss market orders.
    
    This simulates OCO behavior for Futures by placing:
    1. Take-Profit Market order (triggers at take_profit_price)
    2. Stop-Loss Market order (triggers at stop_loss_price)
    
    NOTE: Since Binance Futures doesn't natively support OCO, both orders
    will remain active. In a real scenario, you would need to implement
    logic to cancel the unfilled order when one is executed, or use
    position-based risk management.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
        side: Order side (BUY or SELL) - should be opposite to your position
        quantity: Order quantity (should match position size)
        take_profit_price: Price to take profit
        stop_loss_price: Price to stop loss
    
    Returns:
        Tuple of (take_profit_order, stop_loss_order) responses
    
    Raises:
        BinanceAPIException: If API request fails
        ValueError: If parameters are invalid
    """
    client = get_binance_client()
    
    logger.info(
        f"Placing OCO-style orders: {side} {quantity} {symbol} | "
        f"TP: {take_profit_price}, SL: {stop_loss_price}"
    )
    
    try:
        # Determine the opposite side for closing positions
        # If we have a LONG position, we place SELL orders to close
        # If we have a SHORT position, we place BUY orders to close
        close_side = side
        
        # Place Take-Profit Market order
        logger.info(f"Placing Take-Profit order at {take_profit_price}")
        take_profit_order = client.futures_create_order(
            symbol=symbol,
            side=close_side,
            type='TAKE_PROFIT_MARKET',
            stopPrice=take_profit_price,
            closePosition='true'  # Automatically close the entire position
        )
        
        logger.info(f"Take-Profit order placed: Order ID {take_profit_order['orderId']}")
        logger.debug(f"Take-Profit order response: {take_profit_order}")
        
        # Place Stop-Loss Market order
        logger.info(f"Placing Stop-Loss order at {stop_loss_price}")
        stop_loss_order = client.futures_create_order(
            symbol=symbol,
            side=close_side,
            type='STOP_MARKET',
            stopPrice=stop_loss_price,
            closePosition='true'  # Automatically close the entire position
        )
        
        logger.info(f"Stop-Loss order placed: Order ID {stop_loss_order['orderId']}")
        logger.debug(f"Stop-Loss order response: {stop_loss_order}")
        
        logger.info("OCO-style orders placed successfully")
        
        return take_profit_order, stop_loss_order
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e.status_code} - {e.message}")
        raise
    except BinanceOrderException as e:
        logger.error(f"Binance order error: {e.status_code} - {e.message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error placing OCO-style orders: {e}", exc_info=True)
        raise


def main():
    """
    CLI entry point for OCO-style orders.
    
    Usage:
        python src/advanced/oco.py BTCUSDT SELL 0.01 52000 50000
        
    This places OCO-style orders that will:
    - Take profit at 52000 (sell when price reaches 52000)
    - Stop loss at 50000 (sell when price drops to 50000)
    
    IMPORTANT: This assumes you have an open LONG position in BTCUSDT.
    The orders will close your position when triggered.
    """
    if len(sys.argv) != 6:
        print("Usage: python src/advanced/oco.py <SYMBOL> <SIDE> <QUANTITY> <TAKE_PROFIT_PRICE> <STOP_LOSS_PRICE>")
        print("Example: python src/advanced/oco.py BTCUSDT SELL 0.01 52000 50000")
        print("\nExplanation:")
        print("  SIDE: Should be opposite to your position (SELL for LONG, BUY for SHORT)")
        print("  TAKE_PROFIT_PRICE: Price to take profit")
        print("  STOP_LOSS_PRICE: Price to stop loss")
        print("\nNOTE: This simulates OCO using Take-Profit and Stop-Loss market orders.")
        print("      Both orders will close your position when triggered.")
        sys.exit(1)
    
    symbol_arg = sys.argv[1]
    side_arg = sys.argv[2]
    quantity_arg = sys.argv[3]
    tp_price_arg = sys.argv[4]
    sl_price_arg = sys.argv[5]
    
    try:
        # Validate inputs
        symbol = validate_symbol(symbol_arg)
        side = validate_side(side_arg)
        quantity = validate_quantity(quantity_arg)
        take_profit_price = validate_price(tp_price_arg)
        stop_loss_price = validate_price(sl_price_arg)
        
        # Validate price logic
        if side == 'SELL':
            if take_profit_price <= stop_loss_price:
                raise ValueError(
                    "For SELL orders: Take-Profit price must be higher than Stop-Loss price"
                )
        else:  # BUY
            if take_profit_price >= stop_loss_price:
                raise ValueError(
                    "For BUY orders: Take-Profit price must be lower than Stop-Loss price"
                )
        
        # Place orders
        tp_order, sl_order = place_oco_style_orders(
            symbol, side, quantity, take_profit_price, stop_loss_price
        )
        
        print(f"\n✅ OCO-style orders placed successfully!")
        print("\n📈 Take-Profit Order:")
        print(f"   Order ID: {tp_order['orderId']}")
        print(f"   Type: {tp_order['type']}")
        print(f"   Stop Price: {tp_order['stopPrice']}")
        print(f"   Status: {tp_order['status']}")
        
        print("\n📉 Stop-Loss Order:")
        print(f"   Order ID: {sl_order['orderId']}")
        print(f"   Type: {sl_order['type']}")
        print(f"   Stop Price: {sl_order['stopPrice']}")
        print(f"   Status: {sl_order['status']}")
        
        print("\n⚠️  NOTE: Both orders are now active. When one is triggered and fills,")
        print("   the other will remain active unless you cancel it manually or it's")
        print("   triggered by price movement in the opposite direction.")
        
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