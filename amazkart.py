import sys
import os
import re
import argparse
import validators
from price_tracker import load_products, save_products
from config import PRODUCTS_CSV

BASE_LINK = "https://www.amazon.in/dp/"

def extract_asin(link):
    if not link:
        return None
    pattern = r"/dp/([A-Z0-9]{10})"
    match = re.search(pattern, link)
    if match:
        return match.group(1)
    
    pattern_gp = r"/gp/product/([A-Z0-9]{10})"
    match_gp = re.search(pattern_gp, link)
    if match_gp:
        return match_gp.group(1)
    
    return None

def list_products():
    products = load_products()
    if not products:
        print("\n[!] No products found in products.csv")
        return

    print(f"\n{'Index':<5} {'Name':<50} {'Price':<10} {'Status':<15} {'ASIN':<15}")
    print("-" * 105)
    for i, p in enumerate(products):
        name = p.get('name', '')
        if not name:
            name = "Unnamed Product"
        
        if len(name) > 47:
            name = name[:47] + "..."
        
        link = p.get('link', '')
        asin = extract_asin(link) or "N/A"
        print(f"{i:<5} {name:<50} {p.get('price', ''):<10} {p.get('status', ''):<15} {asin:<15}")
    print("-" * 105)

def add_product(link, name=None):
    if not link:
        print("Error: No link provided.")
        return False
        
    asin = extract_asin(link)
    if not asin:
        print(f"Error: Could not extract ASIN from {link}")
        return False

    products = load_products()
    
    # Check if already exists
    full_link = f"{BASE_LINK}{asin}"
    for p in products:
        if asin in p.get('link', ''):
            print(f"Product {asin} already exists.")
            return False

    new_product = {
        "name": name if name else "",
        "price": "0",
        "status": "",
        "important": "",
        "link": full_link
    }
    products.append(new_product)
    save_products(products)
    print(f"Successfully added: {asin}")
    return True

def remove_product(identifier):
    products = load_products()
    if not products:
        print("No products to remove.")
        return False

    removed = False
    # Try as index
    try:
        index = int(identifier)
        if 0 <= index < len(products):
            p = products.pop(index)
            removed = True
            print(f"Removed product: {p.get('name', 'N/A')} ({extract_asin(p.get('link', ''))})")
    except ValueError:
        # Try as ASIN
        new_products = []
        for p in products:
            if identifier in p.get('link', ''):
                print(f"Removed product: {p.get('name', 'N/A')} ({identifier})")
                removed = True
            else:
                new_products.append(p)
        products = new_products

    if removed:
        save_products(products)
    else:
        print(f"Could not find product with index or ASIN: {identifier}")
    return removed

def print_help():
    print("\nAvailable Commands:")
    print("  list          - Show all products")
    print("  add [url]     - Add a new product (prompts for URL if not provided)")
    print("  remove [id]   - Remove product by Index or ASIN")
    print("  help          - Show this help message")
    print("  exit / quit   - Close the tool")

def interactive_mode():
    print("\n" + "="*30)
    print("   AMAZKART PRODUCT MANAGER")
    print("="*30)
    list_products()
    print_help()
    
    while True:
        try:
            line = input("\namazkart > ").strip()
            if not line:
                continue
                
            parts = line.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ['exit', 'quit']:
                print("Exiting...")
                break
            
            elif cmd == 'list':
                list_products()
            
            elif cmd == 'help':
                print_help()
            
            elif cmd == 'add':
                if args:
                    add_product(args[0])
                else:
                    url = input("Enter product URL: ").strip()
                    if url:
                        add_product(url)
            
            elif cmd == 'remove':
                if args:
                    remove_product(args[0])
                else:
                    val = input("Enter index or ASIN to remove: ").strip()
                    if val:
                        remove_product(val)
            
            else:
                print(f"Unknown command: '{cmd}'. Type 'help' for a list of commands.")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            break

def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Amazkart CLI Tool")
        subparsers = parser.add_subparsers(dest="command")

        # List command
        subparsers.add_parser("list", help="List all products")

        # Add command
        add_parser = subparsers.add_parser("add", help="Add a new product")
        add_parser.add_argument("link", nargs="?", help="Amazon product link")
        add_parser.add_argument("--name", help="Optional name for the product")

        # Remove command
        remove_parser = subparsers.add_parser("remove", help="Remove a product by index or ASIN")
        remove_parser.add_argument("id", help="Index or ASIN of the product to remove")

        args = parser.parse_args()

        if args.command == "list":
            list_products()
        elif args.command == "add":
            add_product(args.link, args.name)
        elif args.command == "remove":
            remove_product(args.id)
        else:
            parser.print_help()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()