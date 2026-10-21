Ebay-dl reads a search term from the command line and collects listings from the first 10 pages of eBay search results. It saves each item's name, price, condition, shipping cost, free-return status, and number sold in a new JSON file that it creates. 
Instructions:

First, make sure beautiful soup is downloaded in your virtual environment:

```bash
python3 -m pip install requests beautifulsoup4
```

Next, to run a search use this line:

```bash
python3 ebay-dl.py --search "Search Term"
```
If the search works then you will get a JSON file create in your project's folder!


Project Link: https://csci40.rtealwitter.com/projects/02_webscraping/project.html