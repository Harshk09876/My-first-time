#!/usr/bin/env python3
import argparse
import asyncio
import sys
import json
import datetime
import random
import shutil
import os
from urllib.parse import urlparse

# --- Cyber-Warrior's Dependencies ---
# Gear up with: pip install telethon colorama pysocks
from telethon import TelegramClient, errors
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam, InputReportReasonFake, InputReportReasonViolence,
    InputReportReasonPornography, InputReportReasonChildAbuse, InputReportReasonOther,
    Channel
)
import colorama

# --- Secret Agency Credentials ---
# Get your own from my.telegram.org to avoid suspicion. Shhh!
API_ID = 29030596
API_HASH = "6f7c293741d1b3a43266e9127cbb1a37"
SESSION_NAME = 'message_reporter' # A cooler session name

# --- Neon Color Palette ---
colorama.init()
class Color:
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    RED = colorama.Fore.RED
    BLUE = colorama.Fore.BLUE
    CYAN = colorama.Fore.CYAN
    MAGENTA = colorama.Fore.MAGENTA
    RESET = colorama.Style.RESET_ALL

def print_color(text, color):
    """Paints the town... or at least, this text."""
    print(f"{color}{text}{Color.RESET}")

def print_banner():
    """Prints a banner worthy of a Cyber-Samurai."""
    banner = rf"""
{Color.MAGENTA}======================================================================================={Color.RESET}
{Color.CYAN}
       />___________________________________________________________
 [##[]/_____________________________________________________________/
      \                                                            \
       \        {Color.YELLOW}C Y B E R - SYSTEM BY RAJA BHAI  A N T I - S P A M{Color.CYAN}       \
<[##[]\_____________________________________________________________\
       \/>                                                             (0)
{Color.RESET}
{Color.MAGENTA}     --=[ 100% FULL WORKING MAA TO CHOD KE RAHUNGA  ]=--{Color.RESET}
{Color.MAGENTA}======================================================================================={Color.RESET}
    """
    print(banner)

def parse_proxy(proxy_str):
    """Deciphers the proxy enigma."""
    try:
        host, port, user, password = proxy_str.strip().split(':')
        return {'proxy_type': 'socks5', 'addr': host, 'port': int(port), 'username': user, 'password': password}
    except (ValueError, IndexError):
        return None

def get_report_reason(reason_str):
    """Chooses the right weapon for the battle."""
    reasons = {
        'spam': InputReportReasonSpam(), 'scam': InputReportReasonFake(), 'fake': InputReportReasonFake(),
        'violence': InputReportReasonViolence(), 'pornography': InputReportReasonPornography(),
        'adult': InputReportReasonPornography(), 'childabuse': InputReportReasonChildAbuse(),
        'other': InputReportReasonOther()
    }
    return reasons.get(reason_str.lower(), InputReportReasonSpam())

first_print = True
def print_dynamic_details(sent, failed, limit, proxy_info, reason, channel_info, status_msg, status_color, current_url=None, report_message=""):
    """Updates our mission's HUD (Heads-Up Display)."""
    global first_print
    
    # --- Line 1: Score and Target ---
    url_display = (current_url[:45] + '...' if current_url and len(current_url) > 45 else current_url) or 'N/A'
    line1 = f" {Color.GREEN}🗡️ Successful Hits: {sent}{Color.RESET} | {Color.RED}🛡️ Fails: {failed}{Color.RESET} | {Color.YELLOW}🎯 Mission: {limit if limit > 0 else '∞'}{Color.RESET} | {Color.CYAN}URL: {url_display:<45}{Color.RESET}"
    
    # --- Line 2: Adversary Info ---
    channel_name = channel_info.get('name', 'Analyzing...')
    members = channel_info.get('members', '???')
    line2 = f" {Color.BLUE}👤 Adversary: {channel_name[:25]:<25}{Color.RESET} | {Color.YELLOW}👥 Allies: {members:<8}{Color.RESET} | {Color.MAGENTA}📜 Reason: {reason.capitalize()}{Color.RESET}"
    
    # --- Line 3: The Blade's Message ---
    report_msg_display = (report_message[:60] + '...' if len(report_message) > 60 else report_message)
    line3 = f" {Color.BLUE}✉️ Scroll: {Color.RESET}{report_msg_display}"

    # --- Line 4: Status and Camouflage (Proxy) ---
    status_str = f"{status_color}{status_msg}{Color.RESET}"
    proxy_status = f"{Color.GREEN}✅ Online{Color.RESET}" if proxy_info['connected'] else f"{Color.RED}❌ Offline{Color.RESET}" if proxy_info['connected'] is False else "👻 No Camouflage"
    proxy_display = f"{proxy_info['str']} ({proxy_status})"
    line4 = f" 🌐 Camouflage: {proxy_display:<30} | 💥 Status: {status_str}"

    if not first_print:
        sys.stdout.write('\x1b[4A')  # Teleport the cursor up!

    sys.stdout.write('\x1b[J')  # Clear the screen like a ninja
    sys.stdout.write(line1 + '\n')
    sys.stdout.write(line2 + '\n')
    sys.stdout.write(line3 + '\n')
    sys.stdout.write(line4 + '\n')
    sys.stdout.flush()
    
    first_print = False

async def handle_report_command(client, args, proxies, initial_proxy_str, report_messages):
    """Orchestrates the symphony of digital justice."""
    print_color("--- 🥷 VIGILANTE MODE ACTIVATED 🥷 ---", Color.MAGENTA)
    
    urls_to_process = []
    if args.url:
        urls_to_process.append(args.url)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                urls_to_process = [line.strip() for line in f if line.strip()]
            if not urls_to_process:
                print_color(f"The scroll '{args.file}' is blank. No missions.", Color.RED); return
            print_color(f"📜 {len(urls_to_process)} missions loaded from '{args.file}'.", Color.BLUE)
        except FileNotFoundError:
            print_color(f"Error: The scroll '{args.file}' has vanished.", Color.RED); return

    successful_reports, failed_reports = 0, 0
    reason_obj = get_report_reason(args.reason)
    
    proxy_info = {
        "str": initial_proxy_str,
        "connected": client.is_connected() if initial_proxy_str != "None" else None
    }
    
    if proxies:
        print_color("Camouflage (proxy) will rotate every 30 hits for maximum discretion.", Color.YELLOW)
    
    await asyncio.sleep(2)

    try:
        while args.limit == 0 or successful_reports < args.limit:
            if proxies and successful_reports > 0 and successful_reports % 30 == 0:
                print_dynamic_details(successful_reports, failed_reports, args.limit, proxy_info, args.reason, {}, "🌪️ Changing camouflage...", Color.MAGENTA)
                await client.disconnect()
                await asyncio.sleep(2)
                new_proxy_str = random.choice(proxies)
                new_proxy_dict = parse_proxy(new_proxy_str)
                if not new_proxy_dict: continue
                client.set_proxy(new_proxy_dict)
                proxy_info['str'] = f"{new_proxy_dict['addr']}:{new_proxy_dict['port']}"
                await client.connect()
                proxy_info['connected'] = client.is_connected()
                if not await client.is_user_authorized():
                    print_color("\nThe new identity has been compromised. Abort mission!", Color.RED); break
            
            target_url = random.choice(urls_to_process)
            current_report_message = random.choice(report_messages)
            channel_info = {'name': 'Exploring...', 'members': '...'}
            
            try:
                print_dynamic_details(successful_reports, failed_reports, args.limit, proxy_info, args.reason, channel_info, "📡 Scanning target...", Color.YELLOW, target_url, current_report_message)
                
                path = urlparse(target_url).path.strip('/').split('/')
                # Ninja logic to decipher complex URLs
                if path and path[0] == 'c' and len(path) >= 3:
                    channel_identifier, _ = (int(path[1]), int(path[2]))
                elif len(path) >= 2 and path[1].isdigit():
                     channel_identifier, _ = (path[0], int(path[1]))
                elif len(path) >= 1:
                     channel_identifier, _ = (path[0], None)
                else:
                    raise ValueError("Undecipherable URL or unknown format")

                peer = await client.get_entity(channel_identifier)
                try:
                    if isinstance(peer, Channel):
                        full_channel = await client(GetFullChannelRequest(channel=peer))
                        channel_info = {'name': peer.title, 'members': full_channel.full_chat.participants_count}
                    else:
                        full_name = getattr(peer, 'title', f"{getattr(peer, 'first_name', '')} {getattr(peer, 'last_name', '')}".strip())
                        channel_info = {'name': full_name, 'members': 'N/A'}
                except Exception:
                     channel_info = {'name': getattr(peer, 'title', "In the shadows"), 'members': 'N/A'}

                print_dynamic_details(successful_reports, failed_reports, args.limit, proxy_info, args.reason, channel_info, "⚔️ Launching attack!", Color.YELLOW, target_url, current_report_message)
                await client(ReportPeerRequest(peer=peer, reason=reason_obj, message=current_report_message))
                
                successful_reports += 1
                print_dynamic_details(successful_reports, failed_reports, args.limit, proxy_info, args.reason, channel_info, "✅ Target Impacted!", Color.GREEN, target_url, current_report_message)
                
                # A samurai needs to meditate between strikes
                current_delay = random.uniform(args.delay_min, args.delay_max)
                await asyncio.sleep(current_delay)

            except (ValueError, TypeError) as e:
                failed_reports += 1
                print_dynamic_details(successful_reports, failed_reports, args.limit, proxy_info, args.reason, {'name': 'Corrupt URL', 'members': 'N/A'}, "Discarding target...", Color.RED, target_url, f"Error: {e}")
                await asyncio.sleep(5)
            except errors.FloodWaitError as e:
                print_color(f"\n🌊 Flood storm! The enemy is defending. Meditating for {e.seconds}s...", Color.YELLOW)
                await asyncio.sleep(e.seconds + 15) # Patience, young grasshopper
            except Exception as e:
                failed_reports += 1
                error_message = str(e).split('\n')[0]
                print_dynamic_details(successful_reports, failed_reports, args.limit, proxy_info, args.reason, channel_info, f"❌ Error. Regrouping.", Color.RED, target_url, f"Detail: {error_message[:40]}")
                await asyncio.sleep(10)

    except KeyboardInterrupt:
        print_color("\n\n\nThe samurai retreats to the shadows... for now.", Color.YELLOW)
    
    print(f"\n\n\n{Color.GREEN}--- MISSION ACCOMPLISHED ---{Color.RESET}")
    print_color(f"🗡️ Total Successful Hits: {successful_reports}", Color.GREEN)
    print_color(f"🛡️ Total Failed Attacks: {failed_reports}", Color.RED)

async def main():
    parser = argparse.ArgumentParser(description="CYBER-SAMURAI ANTI-SPAM [v2.0 Hype Edition]", formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', required=True, help='Choose your combat technique:')
    report_parser = subparsers.add_parser('katana', help='Unsheathe your katana to report a channel/group/user.')
    report_group = report_parser.add_mutually_exclusive_group(required=True)
    report_group.add_argument('-u', '--url', help='Coordinates of a single adversary.')
    report_group.add_argument('-f', '--file', help='Scroll with the list of adversaries.')
    report_parser.add_argument('-r', '--reason', default='spam', choices=['spam', 'scam', 'fake', 'violence', 'pornography', 'adult', 'childabuse', 'other'], help='The reason for your justice.')
    report_parser.add_argument('-l', '--limit', type=int, default=100, help='Number of strikes to deliver (0 for an infinite battle).')
    report_parser.add_argument('--proxy-file', type=str, default='proxy.txt', help='File of secret routes (proxies).')
    report_parser.add_argument('--messages-file', type=str, default='messages.txt', help='Scrolls with custom war messages.')
    report_parser.add_argument('--delay-min', type=int, default=8, help='Minimum meditation time (in seconds) between attacks.')
    report_parser.add_argument('--delay-max', type=int, default=20, help='Maximum meditation time (in seconds) between attacks.')
    args = parser.parse_args()

    # Load the war scrolls
    report_messages = ["For the honor of the code, you are reported."] # Default message
    if os.path.exists(args.messages_file):
        with open(args.messages_file, 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
            if messages:
                report_messages = messages
                print_color(f"🔥 {len(report_messages)} war scrolls loaded and ready.", Color.GREEN)
            else:
                print_color(f"The file '{args.messages_file}' is empty. Using the default oath.", Color.YELLOW)
    else:
        print_color(f"Could not find '{args.messages_file}'. Using the samurai's oath.", Color.YELLOW)

    proxies, initial_proxy, initial_proxy_str = [], None, "None"
    if args.command == 'katana' and os.path.exists(args.proxy_file):
        try:
            with open(args.proxy_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip() and len(line.strip().split(':')) == 4]
            if proxies:
                print_color(f"🌐 {len(proxies)} camouflage routes loaded.", Color.GREEN)
                proxy_str = random.choice(proxies)
                initial_proxy = parse_proxy(proxy_str)
                if initial_proxy: initial_proxy_str = f"{initial_proxy['addr']}:{initial_proxy['port']}"
        except FileNotFoundError:
            print_color(f"Camouflage file not found. Proceeding without stealth.", Color.YELLOW)

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH, proxy=initial_proxy)
    try:
        async with client:
            print_banner()
            me = await client.get_me()
            username_display = f"(@{me.username})" if me.username else "(A ghost in the machine)"
            print_color(f"Connected to the Dojo as: {Color.YELLOW}{me.first_name} {username_display}{Color.GREEN}", Color.GREEN)
            if args.command == 'katana':
                await handle_report_command(client, args, proxies, initial_proxy_str, report_messages)
    except ConnectionError:
        print_color("\nSignal lost. Check your net connection and camouflage routes.", Color.RED)
    except Exception as e:
        print_color(f"\n\nCatastrophic system error!: {e}", Color.RED)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except ImportError:
        print_color("You're missing equipment. Install PySocks for camouflage: pip install pysocks", Color.RED)
    except Exception as e:
         print_color(f"\n\nAn unexpected bug has sabotaged the mission: {e}", Color.RED)
    finally:
         print_color("\n\nThe Cyber-Samurai sheathes his katana. The night is safe.", Color.MAGENTA)