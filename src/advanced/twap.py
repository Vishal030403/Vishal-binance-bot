"""
TWAP (Time-Weighted Average Price) Strategy Module
Splits a large order into smaller chunks executed at fixed time intervals.

This strategy helps reduce market impact by distributing the order over time,
avoiding sudden price movements that could occur with a single large order.
"""

import sys
import time
from typing import List
from binance.exceptions import BinanceAPIException, BinanceOrderException
from config import get_binance_client
from logger import logger
from utils import (
    validate_symbol,
    validate_quantity,
    validate_side,
    validate_positive_int
)


def execute_twap_strategy(
    symbol: str,
    side: str,
    total_quantity: float,
    num_slices: int,
    interval_seconds: int
) -> List[dict]:
    """
    Execute a TWAP strategy by splitting an order into equal slices.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
        side: Order side (BUY or SELL)
        total_quantity: Total quantity to trade
        num_slices: Number of slices to split the order into
        interval_seconds: Time interval between slices in seconds
    
    Returns:
        List of order responses from Binance API
    
    Raises:
        BinanceAPIException: If API request fails
        ValueError: If parameters are invalid
    """
    client = get_binance_client()
    
    # Calculate quantity per slice
    quantity_per_slice = total_quantity / num_slices
    
    logger.info(
        f"Starting TWAP strategy: {side} {total_quantity} {symbol} | "
        f"Slices: {num_slices}, Interval: {interval_seconds}s, "
        f"Per slice: {quantity_per_slice}"
    )
    
    orders = []
    
    try:
        for i in range(num_slices):
            slice_num = i + 1
            
            logger.info(
                f"Executing slice {slice_num}/{num_slices}: "
                f"{side} {quantity_per_slice} {symbol}"
            )
            
            # Place market order for this slice
            order = client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity_per_slice
            )
            
            orders.append(order)
            
            logger.info(
                f"Slice {slice_num} executed successfully | "
                f"Order ID: {order['orderId']}, Status: {order['status']}"
            )
            logger.debug(f"Slice {slice_num} response: {order}")
            
            # Wait before next slice (except for the last one)
            if i < num_slices - 1:
                logger.info(f"Waiting {interval_seconds} seconds before next slice...")
                time.sleep(interval_seconds)
        
        logger.info(
            f"TWAP strategy completed successfully | "
            f"Total orders placed: {len(orders)}"
        )
        
        return orders
        
    except BinanceAPIException as e:
        logger.error(
            f"Binance API error on slice {len(orders) + 1}/{num_slices}: "
            f"{e.status_code} - {e.message}"
        )
        logger.warning(f"Completed {len(orders)} out of {num_slices} slices before error")
        raise
    except BinanceOrderException as e:
        logger.error(
            f"Binance order error on slice {len(orders) + 1}/{num_slices}: "
            f"{e.status_code} - {e.message}"
        )
        logger.warning(f"Completed {len(orders)} out of {num_slices} slices before error")
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error on slice {len(orders) + 1}/{num_slices}: {e}",
            exc_info=True
        )
        logger.warning(f"Completed {len(orders)} out of {num_slices} slices before error")
        raise


def main():
    """
    CLI entry point for TWAP strategy.
    
    Usage:
        python src/advanced/twap.py BTCUSDT BUY 0.1 5 10
        
    This will:
    - Buy a total of 0.1 BTCUSDT
    - Split into 5 slices of 0.02 each
    - Execute each slice with 10 second intervals
    """
    if len(sys.argv) != 6:
        print("Usage: python src/advanced/twap.py <SYMBOL> <SIDE> <TOTAL_QUANTITY> <NUM_SLICES> <INTERVAL_SECONDS>")
        print("Example: python src/advanced/twap.py BTCUSDT BUY 0.1 5 10")
        print("\nExplanation:")
        print("  TOTAL_QUANTITY: Total amount to trade")
        print("  NUM_SLICES: Number of equal slices to split the order into")
        print("  INTERVAL_SECONDS: Time in seconds between each slice execution")
        sys.exit(1)
    
    symbol_arg = sys.argv[1]
    side_arg = sys.argv[2]
    total_qty_arg = sys.argv[3]
    slices_arg = sys.argv[4]
    interval_arg = sys.argv[5]
    
    try:
        # Validate inputs
        symbol = validate_symbol(symbol_arg)
        side = validate_side(side_arg)
        total_quantity = validate_quantity(total_qty_arg)
        num_slices = validate_positive_int(slices_arg, "num_slices")
        interval_seconds = validate_positive_int(interval_arg, "interval_seconds")
        
        # Additional validation
        if num_slices > 100:
            raise ValueError("num_slices must not exceed 100 for safety")
        
        quantity_per_slice = total_quantity / num_slices
        
        print(f"\n🎯 TWAP Strategy Configuration:")
        print(f"Symbol: {symbol}")
        print(f"Side: {side}")
        print(f"Total Quantity: {total_quantity}")
        print(f"Number of Slices: {num_slices}")
        print(f"Quantity per Slice: {quantity_per_slice}")
        print(f"Interval: {interval_seconds} seconds")
        print(f"Total Execution Time: ~{(num_slices - 1) * interval_seconds} seconds")
        print("\n⏳ Starting execution...\n")
        
        # Execute strategy
        orders = execute_twap_strategy(
            symbol, side, total_quantity, num_slices, interval_seconds
        )
        
        print(f"\n✅ TWAP strategy completed successfully!")
        print(f"\n📊 Execution Summary:")
        print(f"   Total Orders Placed: {len(orders)}")
        print(f"   Total Quantity Executed: {total_quantity}")
        print(f"\n📝 Order Details:")
        
        for i, order in enumerate(orders, 1):
            print(f"\n   Slice {i}:")
            print(f"      Order ID: {order['orderId']}")
            print(f"      Quantity: {order['origQty']}")
            print(f"      Status: {order['status']}")
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation error: {e}")
        sys.exit(1)
    except BinanceAPIException as e:
        print(f"\n❌ Binance API error: {e.message}")
        print(f"   Some slices may have been executed. Check bot.log for details.")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("TWAP execution interrupted by user")
        print(f"\n⚠️  Execution interrupted! Check bot.log to see which slices were completed.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print(f"   Check bot.log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()