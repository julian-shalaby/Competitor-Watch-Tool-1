import csv
from datetime import datetime

def save_negative_posts(posts):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"negative_posts_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Link', 'Sentiment'])  # Header
        writer.writerows(posts)
    
    return filename