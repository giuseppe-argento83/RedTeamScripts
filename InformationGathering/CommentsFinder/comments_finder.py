import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from urllib.parse import urljoin, urlparse
from clint.textui import colored
import argparse

def get_links_and_comments(url, depth, outofscope, minlen):
    
    visited_urls = set()
    domain = urlparse(url).netloc
    
    try:
        def crawl_page(current_url, current_depth, outofscope, domain):
            if current_url in visited_urls or current_depth == 0 or (not outofscope and domain not in current_url):
                return

            visited_urls.add(current_url)

            try:
                headers = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                }
                response = requests.get(current_url, headers=headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"{colored.red('[*]')} Error during request to {current_url}: {e}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')

            # Trova e stampa i commenti della pagina
            comments = soup.find_all(string=lambda text: isinstance(text, Comment) and len(text) >= minlen)
            if comments:
                print(f"{colored.blue('[*]')} {current_url}")
                for comment in comments: 
                    comment = comment.replace("\n", "")
                    print(f"{colored.green('[*]')} {comment}")                
            # Trova e stampa i link della pagina
            links = soup.find_all('a', href=True)
            #print(f"Links at {current_url}: {[link['href'] for link in links]}")

            # Ricorsione per ogni link trovato
            for link in links:
                absolute_link = urljoin(current_url, link['href'])
                crawl_page(absolute_link, current_depth - 1, outofscope, domain)

        crawl_page(url, depth, outofscope, domain)
    except KeyboardInterrupt:
        print(f"{colored.red('[*]')} Execution interrupted bu the user.")

def argparser():
    parser = argparse.ArgumentParser(description="comments_finder recursive looks for comments in HTML pages starting from an URL")
    
    parser.add_argument("url", help="Starting URL")
    parser.add_argument("-d","--depth", type=int, default=3, help="Depth value. (Default=3)")
    parser.add_argument("-o","--outofscope", action="store_true", default=False, 
                        help="Follow external domain links (Default=False).")
    parser.add_argument("-m","--minlength", type=int, default=4, help="Minimun length of comments to extract. (Default=4)")
    return parser.parse_args()

if __name__ == "__main__":
    _args = argparser()
    #url_input = input("Inserisci l'URL: ")
    get_links_and_comments(_args.url, _args.depth, _args.outofscope, _args.minlength)
