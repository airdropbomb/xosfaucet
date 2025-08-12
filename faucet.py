from seleniumbase import Driver
import random, time, re
from colorama import Fore, Style

# Welcome message function
def welcome():
    print(
        f"""
        {Fore.GREEN + Style.BRIGHT}       █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
        {Fore.GREEN + Style.BRIGHT}      ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
        {Fore.GREEN + Style.BRIGHT}      ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
        {Fore.GREEN + Style.BRIGHT}      ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
        {Fore.GREEN + Style.BRIGHT}      ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
        {Fore.GREEN + Style.BRIGHT}      ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
        {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE
        """
    )

welcome()

# Function to parse time from "Next daily claim available in Xh Ym"
def parse_wait_time(text):
    hours = 0
    minutes = 0
    if 'h' in text:
        hours = int(re.search(r'(\d+)h', text).group(1))
    if 'm' in text:
        minutes_match = re.search(r'(\d+)m', text)
        if minutes_match:
            minutes = int(minutes_match.group(1))
    return hours * 3600 + minutes * 60  # Convert to seconds

# Read wallets from file
with open("wallets.txt", "r") as file:
    wallets = [line.strip() for line in file if line.strip()]

while True:  # Infinite loop to keep retrying
    for i, address in enumerate(wallets, start=1):
        try:
            with Driver(uc=True, headless=True) as driver:
                print(f"\n\n🧾 Wallet-{i}: {address}")
                print("🌐 Opening XOS Faucet Web (https://faucet.x.ink/)...")
                driver.get("https://faucet.x.ink/")
                driver.sleep(5)

                print("🔎 Waiting Until The Input Address Appears....")
                driver.wait_for_element('div.address-input input', timeout=120)
                driver.sleep(5)

                print("⌨️ Entering The Address Into The Input Field...")
                driver.click('div.address-input input')
                driver.type('div.address-input input', address)
                driver.sleep(5)

                print("⏳ Checking Eligibility Status...")
                for _ in range(20):
                    if driver.is_element_visible('div.address-eligibility.error span'):
                        print("❌ Not Eligible:", driver.get_text('div.address-eligibility.error span'))
                        break
                    elif driver.is_element_visible('div.address-eligibility.waiting'):
                        wait_text = driver.get_text('div.address-eligibility.waiting')
                        print("🕒 Already Claimed:", wait_text)
                        wait_time = parse_wait_time(wait_text)
                        print(f"⏲️ Waiting for {wait_time} seconds before retrying this wallet...")
                        time.sleep(wait_time)
                        break
                    elif driver.is_element_visible('div.address-eligibility.eligible'):
                        print("✅ Eligible:", driver.get_text('div.address-eligibility.eligible'))

                        print("🧩 Waiting For Turnstile to be Completed...")
                        for _ in range(20):
                            try:
                                token = driver.get_attribute('input[name="cf-turnstile-response"]', 'value')
                                if token and len(token) > 50:
                                    print("🔓 Turnstile Completed Successfully.")
                                    break
                            except:
                                pass
                            time.sleep(0.5)
                        else:
                            print("❌ Turnstile Not Completed, Skipping This Wallet.")
                            break

                        print("🎯 Waiting For The Claim Button to be Active...")
                        for _ in range(20):
                            if driver.is_element_visible("button.send-button"):
                                driver.click("button.send-button")
                                print("🚀 XOS Faucet Claimed Successfully")
                                break
                            else:
                                print("⏳ The Claim Button Isn't Active Yet, Please Wait...")
                                time.sleep(1)
                        else:
                            print("❌ Claim Button Is Inactive After Waiting For a While, Skipping This Wallet")
                        break
                    else:
                        print("🔍 Waiting For Further Response From The System...")
                        time.sleep(1)

        except Exception as e:
            print(f"⚠️ Error While Processing Account: {str(e)}")

        delay = random.randint(5, 10)
        print(f"\n⏸️ Wait For {delay} Seconds Before Proceeding To The Next Account...")
        time.sleep(delay)

    print("\n🔄 Finished processing all wallets. Starting over in 60 seconds...")
    time.sleep(60)  # Wait before restarting the loop
