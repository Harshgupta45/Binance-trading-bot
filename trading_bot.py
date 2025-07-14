import argparse
import logging
import sys
import time
from binance import Client
from binance.exceptions import BinanceAPIException

class BasicBot:
    def __init__(self, api_key, api_secret):
        """
        Initialize trading bot with Binance API credentials
        """
        # Configure logging first
        self.logger = logging.getLogger("BinanceBot")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('trading_bot.log', encoding='utf-8')
            ]
        )

        try:
            # Initialize client with testnet configuration
            self.client = Client(
                api_key=api_key,
                api_secret=api_secret,
                testnet=True
            )
            
            # Test API connectivity
            self.test_connection()
            self.logger.info("Trading bot initialized successfully")
            
        except Exception as e:
            self.logger.error("Initialization failed: %s", str(e))
            raise

    def test_connection(self):
        """Verify API credentials and connectivity"""
        try:
            # Test connectivity
            start_time = time.time()
            self.client.futures_ping()
            ping_time = (time.time() - start_time) * 1000
            
            # Get server time
            server_time = self.client.futures_time()
            human_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                    time.gmtime(server_time['serverTime']/1000))
            
            self.logger.info("API Connection Successful | Ping: %.2fms", ping_time)
            self.logger.info("Binance Server Time: %s UTC", human_time)
            
            # Check account status
            account_info = self.client.futures_account()
            self.logger.info("Account Status: CanTrade=%s", account_info['canTrade'])
            
            # Check balance
            balance = self.client.futures_account_balance()
            usdt_balance = next((item for item in balance if item['asset'] == 'USDT'), None)
            
            if usdt_balance:
                self.logger.info("Available Balance: %s USDT", usdt_balance['balance'])
            else:
                self.logger.warning("No USDT balance found")
                
        except BinanceAPIException as e:
            self.logger.error("API Error: %s - %s", e.status_code, e.message)
            raise
        except Exception as e:
            self.logger.error("Connection test failed: %s", str(e))
            raise

    def place_order(self, symbol, side, order_type, quantity, price=None):
        """
        Place futures order with validation and error handling
        """
        try:
            # Input validation
            symbol = symbol.upper().strip()
            if not symbol.endswith('USDT'):
                raise ValueError("Symbol must be a USDT-M pair (e.g., BTCUSDT)")
                
            side = side.upper().strip()
            if side not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
                
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
                
            order_type = order_type.upper().strip()
            valid_types = ['MARKET', 'LIMIT']
            if order_type not in valid_types:
                raise ValueError("Order type must be MARKET or LIMIT")

            # Prepare order parameters
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity
            }

            # Add price for limit orders
            if order_type == 'LIMIT':
                if price is None:
                    raise ValueError("Price is required for limit orders")
                    
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be positive")
                    
                params['price'] = price
                params['timeInForce'] = 'GTC'

            self.logger.info("Placing order: %s", params)
            response = self.client.futures_create_order(**params)
            self.logger.info("Order successful: %s", response)
            return response
            
        except BinanceAPIException as e:
            error_msg = f"API Error {e.status_code}: {e.message}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Order failed: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

def main():
    # Handle Unicode output for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Command-line interface setup
    parser = argparse.ArgumentParser(
        description='Binance Futures Testnet Trading Bot',
        epilog="Examples:\n"
               "  Market Buy: python trading_bot.py BTCUSDT buy market 0.001 --api_key YOUR_KEY --api_secret YOUR_SECRET\n"
               "  Limit Sell: python trading_bot.py ETHUSDT sell limit 0.1 2500 --api_key YOUR_KEY --api_secret YOUR_SECRET"
    )
    
    # Required arguments
    parser.add_argument('symbol', help='Trading pair (e.g., BTCUSDT)')
    parser.add_argument('side', choices=['buy', 'sell'], help='Order side')
    parser.add_argument('type', choices=['market', 'limit'], help='Order type')
    parser.add_argument('quantity', type=float, help='Order quantity')
    parser.add_argument('price', nargs='?', type=float, default=None,
                       help='Price for limit orders (required for limit type)')
    parser.add_argument('--api_key', required=True, help='Binance API key')
    parser.add_argument('--api_secret', required=True, help='Binance API secret')
    
    args = parser.parse_args()
    
    try:
        # Initialize bot
        print("Initializing bot and testing API credentials...")
        bot = BasicBot(args.api_key, args.api_secret)
        
        # Validate limit order price requirement
        if args.type == 'limit' and args.price is None:
            raise ValueError("Price is required for limit orders")
        
        # Place order
        print("Placing order...")
        response = bot.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price
        )
        
        # Output order details
        print("\n" + "="*50)
        print("[SUCCESS] Order Execution Details:")
        print("="*50)
        print(f"Order ID: {response['orderId']}")
        print(f"Symbol: {response['symbol']}")
        print(f"Status: {response['status']}")
        print(f"Side: {response['side']}")
        print(f"Type: {response['type']}")
        print(f"Quantity: {response['origQty']}")
        if 'price' in response:
            print(f"Price: {response['price']}")
        print(f"Executed Qty: {response['executedQty']}")
        if 'avgPrice' in response:
            print(f"Avg Price: {response['avgPrice']}")
        print("="*50)
        print("Check Binance Testnet for full order details")
        print("https://testnet.binancefuture.com")
        
    except ValueError as e:
        print(f"\n[ERROR] Validation Error: {str(e)}")
        print("Use -h for help with command usage")
        exit(1)
    except RuntimeError as e:
        print(f"\n[ERROR] Trading Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
    