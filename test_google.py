from googlesearch import search

try:
    results = search("Learn Docker free", advanced=True, num_results=5)
    for r in results:
        print(r.title, r.url)
except Exception as e:
    print(e)
