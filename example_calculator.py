"""
Example Calculator Module

A simple calculator with history tracking, demonstrating
README-Sync's ability to detect code changes and update documentation.
"""
from typing import List, Optional
from datetime import datetime


class Calculator:
    """A calculator with operation history tracking."""
    
    def __init__(self):
        """Initialize calculator with empty history."""
        self.history: List[dict] = []
        self._last_result: Optional[float] = None
    
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        result = a + b
        self._record("add", a, b, result)
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract b from a.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Difference of a and b
        """
        result = a - b
        self._record("subtract", a, b, result)
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b
        """
        result = a * b
        self._record("multiply", a, b, result)
        return result
    
    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b.
        
        Args:
            a: Numerator
            b: Denominator
            
        Returns:
            Quotient of a divided by b
            
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._record("divide", a, b, result)
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """
        Raise base to the power of exponent.
        
        Args:
            base: The base number
            exponent: The exponent
            
        Returns:
            base raised to the power of exponent
        """
        result = base ** exponent
        self._record("power", base, exponent, result)
        return result
    
    def square_root(self, a: float) -> float:
        """
        Calculate the square root of a number.
        
        Args:
            a: The number to find the square root of
            
        Returns:
            Square root of a
            
        Raises:
            ValueError: If a is negative
        """
        import math
        if a < 0:
            raise ValueError("Cannot calculate square root of a negative number")
        result = math.sqrt(a)
        self._record("square_root", a, 0, result)
        return result
    
    def _record(self, operation: str, a: float, b: float, result: float):
        """Record an operation in history."""
        self.history.append({
            "operation": operation,
            "operands": (a, b),
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        self._last_result = result
    
    def get_history(self) -> List[dict]:
        """Get the full operation history."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear the operation history."""
        self.history.clear()
        self._last_result = None
    
    @property
    def last_result(self) -> Optional[float]:
        """Get the result of the last operation."""
        return self._last_result


def quick_calculate(expression: str) -> float:
    """
    Perform a quick calculation from a string expression.
    
    Supports basic operations: +, -, *, /
    
    Args:
        expression: A simple math expression like "2 + 3"
        
    Returns:
        The result of the calculation
        
    Raises:
        ValueError: If the expression is invalid
    """
    calc = Calculator()
    parts = expression.strip().split()
    
    if len(parts) != 3:
        raise ValueError(f"Invalid expression: {expression}")
    
    a, op, b = float(parts[0]), parts[1], float(parts[2])
    
    if op == "sqrt":
        return calc.square_root(a)
        
    operations = {
        "+": calc.add,
        "-": calc.subtract,
        "*": calc.multiply,
        "/": calc.divide,
    }
    
    if op not in operations:
        raise ValueError(f"Unsupported operator: {op}")
    
    return operations[op](a, b)


if __name__ == "__main__":
    calc = Calculator()
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"5 * 6 = {calc.multiply(5, 6)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
    print(f"2 ^ 8 = {calc.power(2, 8)}")
    print(f"\nHistory: {len(calc.get_history())} operations")
