# test_credentials.py
from binance import Client
import sys
import time

def test_api_credentials(api_key, api_secret):
    try:
        print("Testing Binance API credentials...")
        
        # Initialize client
        client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True,
            tld='us'
        )
        
        # 1. Test connectivity
        start_time = time.time()
        client.futures_ping()
        ping_time = (time.time() - start_time) * 1000
        print(f"[SUCCESS] API Connectivity: Working (Ping: {ping_time:.2f}ms)")
        
        # 2. Test server time
        server_time = client.futures_time()
        human_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                  time.gmtime(server_time['serverTime']/1000))
        print(f"[SUCCESS] Server Time: {human_time} UTC")
        
        # 3. Test authenticated endpoint (using valid method)
        account_info = client.futures_account()
        print(f"[SUCCESS] Account Information Received")
        print(f"    Can Trade: {account_info['canTrade']}")
        print(f"    Can Withdraw: {account_info['canWithdraw']}")
        print(f"    Can Deposit: {account_info['canDeposit']}")
        
        # 4. Get account balance
        balance = client.futures_account_balance()
        usdt_balance = next((item for item in balance if item['asset'] == 'USDT'), None)
        
        if usdt_balance:
            print(f"[SUCCESS] USDT Balance: {usdt_balance['balance']}")
        else:
            print("[WARNING] No USDT balance found")
            
        print("\n[SUCCESS] All tests passed! Credentials are valid.")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Credential Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Replace with your actual testnet keys
    API_KEY = "47ced759d309480e9c66a0d85e2c81234e547a7410f05ef6842812619d2f8619"
    API_SECRET = "6c1b7f57d1e5fbad7e6d244b93d25310dcab8bccff1cb98300b9769bc2dc710e"
    
    # Handle Unicode output for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    test_api_credentials(API_KEY, API_SECRET)