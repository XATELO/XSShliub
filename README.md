\# 💘 XSShliub — The Union of Payload \& Browser



\*\*XSShliub\*\* (pronounced "shliub", means "Marriage" in Belarusian) is a powerful \*\*Client-Side XSS Fuzzer\*\*.



Unlike standard scanners that only check HTTP responses, \*\*XSShliub\*\* uses \*\*Selenium (Headless Chrome)\*\* to actually render the page and detect if an `alert()`, `confirm()` or `prompt()` was executed.



!\[Logo](logo.png)



\## 🔥 Features



\*   \*\*True Verification:\*\* Detects XSS only if JS execution really happens (no false positives).

\*   \*\*WAF Evasion:\*\* Random User-Agents and Jitter delay.

\*   \*\*Cross-Platform:\*\* Works on \*\*Kali Linux\*\* (root supported) and \*\*Windows\*\*.

\*   \*\*Smart Fuzzing:\*\* Replaces `FUZZ` keyword in URL with payloads.

\*   \*\*Multi-Threading:\*\* Runs multiple browser instances in parallel.



\## 📦 Installation



\### Linux (Kali) / macOS



It is recommended to use a virtual environment:



1\. Clone the repo:

&nbsp;  git clone https://github.com/YOUR\_USERNAME/XSShliub

&nbsp;  cd XSShliub



2\. Create venv and install requirements:

&nbsp;  python3 -m venv venv

&nbsp;  source venv/bin/activate

&nbsp;  pip install -r requirements.txt



3\. Install system driver (Kali):

&nbsp;  sudo apt update \&\& sudo apt install chromium-driver



\### Windows



1\. Clone the repo:

&nbsp;  git clone https://github.com/YOUR\_USERNAME/XSShliub

&nbsp;  cd XSShliub



2\. Install requirements:

&nbsp;  pip install -r requirements.txt



\## 🚀 Usage



You need to put your payloads into `payloads.txt` file in the same directory.



\### Basic Scan

python xsshliub.py -u "https://target.com/search?q=FUZZ"



\### Debug Mode (Show Browser)

Useful to see if WAF blocks you or if the page loads correctly.

python xsshliub.py -u "https://target.com/search?q=FUZZ" --head



\### Multi-threading (Faster)

Run 5 browsers in parallel with 2 seconds delay between requests.

python xsshliub.py -u "https://target.com/search?q=FUZZ" -t 5 -d 2.0



\## ⚙️ Arguments



-u, --url       Target URL containing 'FUZZ' keyword.

-t, --threads   Number of concurrent browsers (Default: 3).

-d, --delay     Delay between requests in seconds (Default: 1.0).

--head          Disable headless mode (show browser window).



\## ⚠️ Disclaimer

This tool is intended for educational purposes and authorized security testing only. The authors are not responsible for any misuse or damage caused by this program.



---

Made with ❤️ by \*\*DevSecOpter\*\* 

