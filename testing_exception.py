from src.custom_exception import CustomException
from src.logger import get_logger
import sys 

logger = get_logger(__name__)

def divide_numbers(a,b):
    try:
        result = a/b
        logger.info(f"Dividing {a} by {b} gives {result}")
        return result
    except Exception as e:
        logger.error("We are dividing by zero")
        raise CustomException('Divison by Zero error', sys)

if __name__ == "__main__":
    try:
        divide_numbers(10,0)
    except CustomException as ce:
        logger.error(str(ce))

