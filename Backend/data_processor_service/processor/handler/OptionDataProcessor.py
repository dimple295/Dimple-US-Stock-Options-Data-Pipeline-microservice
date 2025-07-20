import pandas as pd
import logging
import re
from processor.handler.DataPreprocessor import DataPreprocessor
from processor.utils.logConfig import LogConfig

logger = LogConfig()

def extract_stock_symbol(contract_symbol):
    """
    Extract stock symbol from contract symbol.
    Contract symbols can have various formats:
    - AAPL240119C00150000 (AAPL + date + C/P + strike)
    - AAPL  240119C00150000 (with spaces)
    - AAPL240119C00150000 (no spaces)
    """
    if not contract_symbol:
        return None
    
    # Remove any spaces and convert to uppercase
    clean_symbol = contract_symbol.replace(' ', '').upper()
    
    # Common stock symbols are 1-5 characters
    # Look for patterns like: SYMBOL + DATE + OPTION_TYPE + STRIKE
    # The stock symbol is typically at the beginning
    
    # Try to extract stock symbol using regex
    # Pattern: 1-5 letters followed by numbers or option indicators
    match = re.match(r'^([A-Z]{1,5})', clean_symbol)
    if match:
        return match.group(1)
    
    # Fallback: take first 3-5 characters if they look like a stock symbol
    # Stock symbols are typically 1-5 characters and all uppercase letters
    for length in range(5, 0, -1):
        candidate = clean_symbol[:length]
        if candidate.isalpha() and candidate.isupper():
            return candidate
    
    # If all else fails, return the first 3 characters (original behavior)
    return clean_symbol[:3] if len(clean_symbol) >= 3 else clean_symbol

def OptionDataProcessor(data):
    
    logger.info(f"PROCESSOR CALLED OPTIONDATAPROCESSOR")

    try:
        if not data or len(data) == 0:
            logger.error("Empty data received in OptionDataProcessor")
            return data
        
        # Extract stock symbol from the first contract symbol
        first_contract = data[0].get("contractSymbol", "")
        sym = extract_stock_symbol(first_contract)
        logger.info(f"Extracted stock symbol '{sym}' from contract symbol '{first_contract}'")

        # Process all records and extract stock symbols
        for value in data:
            contract_symbol = value.get("contractSymbol", "")
            extracted_symbol = extract_stock_symbol(contract_symbol)
            value['symbol'] = extracted_symbol
            value['StockName'] = extracted_symbol  # Ensure StockName is also set

        # Convert values to DataFrame for processing
        data_df = pd.DataFrame(data)
        
        # Ensure we have the required columns
        required_columns = ["contractSymbol", "symbol", "lastTradeDate", "strike", "lastPrice", "bid", "ask", "change", "percentChange", "volume", "openInterest", "impliedVolatility", "inTheMoney", "contractSize", "currency", "expirationDate", "type"]
        
        # Filter to only include columns that exist in the data
        available_columns = [col for col in required_columns if col in data_df.columns]
        df = data_df[available_columns]
        
        logger.info(f"Processing options data for symbol: {sym}")
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"Available columns: {list(df.columns)}")
        
        # Initialize preprocessor for options data
        preprocessor = DataPreprocessor(data_type='options')
        
        # Apply comprehensive preprocessing
        processed_data = preprocessor.preprocess_stock_data(df)

        # Additional options-specific validation
        processed_data = _validate_options_specific_data(processed_data)
        
        logger.info(f"Options data processing completed for {sym}")
        logger.info(f"Processed data sending back to Processor: {processed_data}")

        return processed_data
        
    except Exception as e:
        logger.error(f"Options data processing error: {str(e)}")
        # Return original data if processing fails
        return data

def _validate_options_specific_data(data):
    """
    Additional validation specific to options data
    """
    try:
        df = pd.DataFrame(data['values'])
        original_count = len(df)
        
        # Options-specific validation rules can be added here
        # For now, we'll use the same stock validation
        # but this can be extended for options-specific fields like:
        # - strike price validation
        # - expiration date validation
        # - option type validation (call/put)
        # - implied volatility ranges
        
        # Example: If options data has strike prices
        if 'strike' in df.columns:
            # Remove invalid strike prices (negative or zero)
            df = df[df['strike'] > 0]
        
        # Example: If options data has expiration dates
        if 'expiration' in df.columns:
            df['expiration'] = pd.to_datetime(df['expiration'], errors='coerce')
            df = df.dropna(subset=['expiration'])
            # Remove expired options (optional based on business logic)
            # current_date = pd.Timestamp.now()
            # df = df[df['expiration'] >= current_date]
        
        data['values'] = df.to_dict(orient='records')
        
        if len(df) != original_count:
            logger.info(f"Options-specific validation removed {original_count - len(df)} invalid records")
        
        return data
        
    except Exception as e:
        logger.error(f"Options-specific validation error: {str(e)}")
        return data