# import bs4
# from urllib.request import urlopen as ureq
# from bs4 import BeautifulSoup as soup

# def web_scrapper_all_products(url):
#     try:
#         # Open the URL and read the page
#         uclient = ureq(url)
#         page_html = uclient.read()
#         uclient.close()

#         # Parse the page using BeautifulSoup
#         page_soup = soup(page_html, "html.parser")
        
#         # Find all product containers
#         products = page_soup.findAll("article", {"class": "product_pod"})
        
#         # List to store all product information
#         all_products = []
        
#         for product in products:
#             # Extract product name
#             product_name = product.h3.a['title']
            
#             # Extract product price
#             product_price = product.find("p", {"class": "price_color"}).text.strip()[1:].replace(',', '')
            
#             # Extract product URL (to simulate ID, using the URL)
#             product_url = product.h3.a['href']
#             product_id = product_url.split('/')[-2]  # Assuming last part of URL is a product ID
            
#             # Clean the price (extract integer part)
#             integer_price = product_price.split('.')[0]
            
#             # Append product info to the list
#             all_products.append({
#                 "Product Name": product_name,
#                 "Product ID": product_id,
#                 "Price": integer_price
#             })

#         return all_products
    
#     except Exception as e:
#         return f"Error occurred: {e}"

# # Example usage with a section URL:
# url = 'http://books.toscrape.com/catalogue/category/books/science_22/index.html'
# products_info = web_scrapper_all_products(url)

# # Print all product info
# for product in products_info:
#     print(product)


# http://books.toscrape.com/catalogue/category/books/science_22/index.html

from flask import Flask, render_template, request, send_file
import bs4
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Function to scrape all products
from urllib.parse import urljoin

# Function to scrape all products
def scrape_products(url):
    try:
        uclient = ureq(url)
        page_html = uclient.read()
        uclient.close()

        page_soup = soup(page_html, "html.parser")
        products = page_soup.findAll("article", {"class": "product_pod"})
        
        all_products = []
        
        for product in products:
            # Product name
            product_name = product.h3.a['title']
            
            # Product price
            product_price = product.find("p", {"class": "price_color"}).text.strip()[1:].replace(',', '')
            integer_price = product_price.split('.')[0]
            
            # Product rating (class="star-rating {Rating}")
            rating_tag = product.find("p", {"class": "star-rating"})
            rating_class = rating_tag.get('class')
            product_rating = rating_class[1]  # This gives us the rating (e.g., "Four")

            # Product image
            image_url = product.find("img")['src']  # Get image source URL
            
            # Convert relative URL to absolute URL
            image_url = urljoin(url, image_url)  # Make the URL absolute
            
            all_products.append({
                "Product Name": product_name,
                "Price": integer_price,
                "Rating": product_rating,
                "Image URL": image_url  # Store image URL
            })

        return all_products
    
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/', methods=['GET', 'POST'])
def home():
    products = []
    if request.method == 'POST':
        url = request.form['url']
        products = scrape_products(url)
        
    return render_template('index.html', products=products)

@app.route('/download_csv', methods=['POST'])
def download_csv():
    products = request.form['products_data']
    
    # Convert string back to a list of dicts
    products_list = eval(products)
    
    df = pd.DataFrame(products_list)
    
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(output, mimetype='text/csv', as_attachment=True, attachment_filename='scraped_products.csv')

if __name__ == "__main__":
    app.run(debug=True)
