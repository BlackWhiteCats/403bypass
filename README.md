# 403bypass

# 403Bypasser

![image](https://github.com/user-attachments/assets/d0ac9438-9ec4-486a-9998-601f31539958)


403Bypasser is an educational tool designed for ethical hackers and bug bounty hunters. It automates various techniques to bypass HTTP 403 Forbidden responses by manipulating URL paths, HTTP methods, and headers.

Features

* Automatic URL parsing and path extraction
* Supports single URL (`-u`) or a list of targets (`--targets`)
* Tests 403 bypass via:

  * Path manipulation (e.g., `/secret/..;/`, `/./secret`, etc.)
  * HTTP method manipulation (GET and POST)
  * Header injection (e.g., `X-Forwarded-For`, `X-Original-URL`, etc.)
* Prints only status 200 (success) results
* Summary of successful techniques at the end when using `--targets`

Installation

```
# Clone the repository
$ git clone https://github.com/YOUR_USERNAME/403bypasser.git

# Navigate to the project
$ cd 403bypasser

# (Optional) Create a virtual environment
$ python3 -m venv venv
$ source venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt
```

Requirements

* Python 3.7+
* Modules:

  * `requests`
  * `validators`
  * `colorama`
  * `pyfiglet`

You can install all required modules with:

```bash
pip install -r requirements.txt
```

Usage

Scan a Single URL

```bash
python 403bypasser.py -u http://example.com/secret
```

Scan Multiple URLs from File

```bash
python 403bypasser.py --targets targets.txt
```

Where `targets.txt` contains:

```
http://example.com/secret
http://test.com/admin
...
```

Output

* Only bypasses that return **HTTP 200** are considered successful
* When scanning a list (`--targets`), a final summary will display which methods worked on which URLs

---

Example Output

```
✔ GET http://target.com/secret/..;/ -> 200
✔ HEADER_OVERRIDE -> X-Original-URL: /secret (status 200)
✔ HEADER_INJECT -> X-Forwarded-For: 127.0.0.1 (status 200)

=== Resumo de bypasses bem-sucedidos ===
http://target.com/secret via GET http://target.com/secret/..;/ -> 200
http://target.com/secret via HEADER_OVERRIDE X-Original-URL: /secret -> 200
```
