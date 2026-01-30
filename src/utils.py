"""
Utility functions for input validation and order parameter processing.
"""

from typing import Tuple
from decimal import Decimal, InvalidOperation
from logger import logger


def validate_symbol(symbol: str) -> str:
    """
    Validate trading symbol format.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
    
    Returns:
        Uppercase symbol string
    
    Raises:
        ValueError: If symbol format is invalid
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    
    symbol = symbol.upper().strip()
    
    if not symbol.endswith('USDT'):
        raise ValueError(f"Invalid symbol '{symbol}': Must end with 'USDT' for USDT-M Futures")
    
    if len(symbol) < 5:
        raise ValueError(f"Invalid symbol '{symbol}': Too short")
    
    logger.debug(f"Symbol validated: {symbol}")
    return symbol


def validate_quantity(quantity: str) -> float:
    """
    Validate and convert quantity to float.
    
    Args:
        quantity: Quantity as string
    
    Returns:
        Validated quantity as float
    
    Raises:
        ValueError: If quantity is invalid or not positive
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{quantity}': Must be a valid number")
    
    if qty <= 0:
        raise ValueError(f"Invalid quantity {qty}: Must be greater than 0")
    
    logger.debug(f"Quantity validated: {qty}")
    return qty


def validate_price(price: str) -> float:
    """
    Validate and convert price to float.
    
    Args:
        price: Price as string
    
    Returns:
        Validated price as float
    
    Raises:
        ValueError: If price is invalid or not positive
    """
    try:
        prc = float(price)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid price '{price}': Must be a valid number")
    
    if prc <= 0:
        raise ValueError(f"Invalid price {prc}: Must be greater than 0")
    
    logger.debug(f"Price validated: {prc}")
    return prc


def validate_side(side: str) -> str:
    """
    Validate order side (BUY/SELL).
    
    Args:
        side: Order side
    
    Returns:
        Uppercase side string
    
    Raises:
        ValueError: If side is not BUY or SELL
    """
    side = side.upper().strip()
    
    if side not in ['BUY', 'SELL']:
        raise ValueError(f"Invalid side '{side}': Must be 'BUY' or 'SELL'")
    
    logger.debug(f"Side validated: {side}")
    return side


def validate_positive_int(value: str, param_name: str) -> int:
    """
    Validate and convert a positive integer parameter.
    
    Args:
        value: Value as string
        param_name: Parameter name for error messages
    
    Returns:
        Validated integer
    
    Raises:
        ValueError: If value is not a positive integer
    """
    try:
        val = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid {param_name} '{value}': Must be a valid integer")
    
    if val <= 0:
        raise ValueError(f"Invalid {param_name} {val}: Must be greater than 0")
    
    logger.debug(f"{param_name} validated: {val}")
    return val


def format_order_response(order: dict) -> str:
    """
    Format order response for logging and display.
    
    Args:
        order: Order response from Binance API
    
    Returns:
        Formatted string representation
    """
    return (
        f"Order placed successfully:\n"
        f"  Order ID: {order.get('orderId', 'N/A')}\n"
        f"  Symbol: {order.get('symbol', 'N/A')}\n"
        f"  Side: {order.get('side', 'N/A')}\n"
        f"  Type: {order.get('type', 'N/A')}\n"
        f"  Quantity: {order.get('origQty', 'N/A')}\n"
        f"  Price: {order.get('price', 'N/A')}\n"
        f"  Status: {order.get('status', 'N/A')}"
    )


def validate_grid_params(lower_price: float, upper_price: float, grid_count: int) -> None:
    """
    Validate grid trading parameters.
    
    Args:
        lower_price: Lower bound price
        upper_price: Upper bound price
        grid_count: Number of grid levels
    
    Raises:
        ValueError: If parameters are invalid
    """
    if lower_price >= upper_price:
        raise ValueError(
            f"Invalid price range: lower_price ({lower_price}) must be "
            f"less than upper_price ({upper_price})"
        )
    
    if grid_count < 2:
        raise ValueError(f"Invalid grid_count {grid_count}: Must be at least 2")
    
    logger.debug(
        f"Grid parameters validated: lower={lower_price}, upper={upper_price}, "
        f"count={grid_count}"
    )
    