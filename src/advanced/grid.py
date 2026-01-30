"""
Grid Trading Strategy Module
Places multiple limit BUY orders at equal intervals between lower and upper price bounds.

Grid trading is a strategy that profits from price oscillations by placing orders
at predetermined price levels, creating a "grid" of orders.
"""

import sys
from typing import List
from binance.exceptions import BinanceAPIException, BinanceOrderException
from config import get_binance_client
from logger import logger
from utils import (
    validate_symbol,
    validate_quantity,
    validate_price,
    validate_positive_int,
    validate_grid_params
)


def calculate_grid_levels(lower_price: float, upper_price: float, grid_count: int) -> List[float]:
    """
    Calculate evenly spaced grid price levels.
    
    Args:
        lower_price: Lower bound of the grid
        upper_price: Upper bound of the grid
        grid_count: Number of grid levels
    
    Returns:
        List of price levels
    """
    if grid_count == 1:
        return [(lower_price + upper_price) / 2]
    
    step = (upper_price - lower_price) / (grid_count - 1)
    levels = [lower_price + (step * i) for i in range(grid_count)]
    
    logger.debug(f"Calculated {grid_count} grid levels: {levels}")
    return levels


def execute_grid_strategy(
    symbol: str,
    quantity_per_grid: float,
    lower_price: float,
    upper_price: float,
    grid_count: int
) -> List[dict]:
    """
    Execute a grid trading strategy by placing multiple limit BUY orders.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
        quantity_per_grid: Quantity for each grid order
        lower_price: Lower price bound
        upper_price: Upper price bound
        grid_count: Number of grid levels
    
    Returns:
        List of order responses from Binance API
    
    Raises:
        BinanceAPIException: If API request fails
        ValueError: If parameters are invalid
    """
    client = get_binance_client()
    
    # Validate grid parameters
    validate_grid_params(lower_price, upper_price, grid_count)
    
    # Calculate grid levels
    grid_levels = calculate_grid_levels(lower_price, upper_price, grid_count)
    
    logger.info(
        f"Starting grid trading strategy: {symbol} | "
        f"Range: {lower_price} - {upper_price}, Grids: {grid_count}, "
        f"Qty per grid: {quantity_per_grid}"
    )
    
    orders = []
    
    try:
        for i, price in enumerate(grid_levels):
            grid_num = i + 1
            
            logger.info(
                f"Placing grid order {grid_num}/{grid_count}: "
                f"BUY {quantity_per_grid} {symbol} @ {price}"
            )
            
            # Place limit BUY order at this grid level
            order = client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='LIMIT',
                timeInForce='GTC',
                quantity=quantity_per_grid,
                price=price
            )
            
            orders.append(order)
            
            logger.info(
                f"Grid {grid_num} placed successfully | "
                f"Order ID: {order['orderId']}, Price: {order['price']}"
            )
            logger.debug(f"Grid {grid_num} response: {order}")
        
        logger.info(
            f"Grid strategy completed successfully | "
            f"Total orders placed: {len(orders)}"
        )
        
        return orders
        
    except BinanceAPIException as e:
        logger.error(
            f"Binance API error on grid {len(orders) + 1}/{grid_count}: "
            f"{e.status_code} - {e.message}"
        )
        logger.warning(f"Placed {len(orders)} out of {grid_count} grids before error")
        raise
    except BinanceOrderException as e:
        logger.error(
            f"Binance order error on grid {len(orders) + 1}/{grid_count}: "
            f"{e.status_code} - {e.message}"
        )
        logger.warning(f"Placed {len(orders)} out of {grid_count} grids before error")
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error on grid {len(orders) + 1}/{grid_count}: {e}",
            exc_info=True
        )
        logger.warning(f"Placed {len(orders)} out of {grid_count} grids before error")
        raise


def main():
    """
    CLI entry point for grid trading strategy.
    
    Usage:
        python src/advanced/grid.py BTCUSDT 0.01 50000 52000 5
        
    This will place 5 limit BUY orders:
    - At prices: 50000, 50500, 51000, 51500, 52000
    - Each order quantity: 0.01 BTCUSDT
    """
    if len(sys.argv) != 6:
        print("Usage: python src/advanced/grid.py <SYMBOL> <QUANTITY_PER_GRID> <LOWER_PRICE> <UPPER_PRICE> <GRID_COUNT>")
        print("Example: python src/advanced/grid.py BTCUSDT 0.01 50000 52000 5")
        print("\nExplanation:")
        print("  QUANTITY_PER_GRID: Amount to trade at each grid level")
        print("  LOWER_PRICE: Lower bound of the price grid")
        print("  UPPER_PRICE: Upper bound of the price grid")
        print("  GRID_COUNT: Number of equally-spaced grid levels")
        sys.exit(1)
    
    symbol_arg = sys.argv[1]
    quantity_arg = sys.argv[2]
    lower_price_arg = sys.argv[3]
    upper_price_arg = sys.argv[4]
    grid_count_arg = sys.argv[5]
    
    try:
        # Validate inputs
        symbol = validate_symbol(symbol_arg)
        quantity_per_grid = validate_quantity(quantity_arg)
        lower_price = validate_price(lower_price_arg)
        upper_price = validate_price(upper_price_arg)
        grid_count = validate_positive_int(grid_count_arg, "grid_count")
        
        # Additional validation
        if grid_count > 50:
            raise ValueError("grid_count must not exceed 50 for safety")
        
        validate_grid_params(lower_price, upper_price, grid_count)
        
        # Calculate preview
        grid_levels = calculate_grid_levels(lower_price, upper_price, grid_count)
        total_quantity = quantity_per_grid * grid_count
        
        print(f"\n📊 Grid Trading Strategy Configuration:")
        print(f"Symbol: {symbol}")
        print(f"Price Range: {lower_price} - {upper_price}")
        print(f"Grid Levels: {grid_count}")
        print(f"Quantity per Grid: {quantity_per_grid}")
        print(f"Total Quantity: {total_quantity}")
        print(f"\n📍 Grid Levels:")
        for i, level in enumerate(grid_levels, 1):
            print(f"   Grid {i}: {level}")
        
        print("\n⏳ Placing grid orders...\n")
        
        # Execute strategy
        orders = execute_grid_strategy(
            symbol, quantity_per_grid, lower_price, upper_price, grid_count
        )
        
        print(f"\n✅ Grid strategy completed successfully!")
        print(f"\n📊 Execution Summary:")
        print(f"   Total Orders Placed: {len(orders)}")
        print(f"   Total Quantity: {total_quantity}")
        print(f"   Price Range: {lower_price} - {upper_price}")
        print(f"\n📝 Order Details:")
        
        for i, order in enumerate(orders, 1):
            print(f"\n   Grid {i}:")
            print(f"      Order ID: {order['orderId']}")
            print(f"      Price: {order['price']}")
            print(f"      Quantity: {order['origQty']}")
            print(f"      Status: {order['status']}")
        
        print(f"\n💡 Tip: These orders will fill as price moves through the grid levels.")
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Validation error: {e}")
        sys.exit(1)
    except BinanceAPIException as e:
        print(f"\n❌ Binance API error: {e.message}")
        print(f"   Some grid orders may have been placed. Check bot.log for details.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print(f"   Check bot.log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
    