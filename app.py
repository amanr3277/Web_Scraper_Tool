from flask import Flask, jsonify, request, render_template
import requests
from bs4 import BeautifulSoup
import calendar
from flask_cors import CORS

app = Flask(__name__, static_folder="templates/static")
CORS(app)

def fetch_blog_data(base_url, specific_data):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/94.0.4606.81 Safari/537.36"
    })

    blog_data = []
    months = {month.lower() for month in calendar.month_name[1:]}
    page_num = 1

    while True:
        url = f"{base_url}page/{page_num}/"
        response = session.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            blog_posts = soup.find_all('div', class_='wrap')

            if not blog_posts:
                break

            for post in blog_posts:
                image_link = post.find('a', class_='rocket-lazyload')

                if image_link and 'data-bg' in image_link.attrs:
                    image_url = image_link['data-bg']
                else:
                    image_url = "NaN"

                blog_title = post.find('div', class_='content')
                if blog_title:
                    title_element = blog_title.find('h6')
                    title = title_element.text.strip() if title_element else "Title Not Found"
                else:
                    title = "Title Not Found"

                blog_date = post.find('div', class_='bd-item')

                if blog_date:
                    date_icon = blog_date.find('i', class_='material-design-icon-history-clock-button')
                    if date_icon:
                        next_element = date_icon.find_next('span')
                        if next_element and any(month in next_element.text.lower() for month in months):
                            publication_date = next_element.text.strip()
                        else:
                            publication_date = "Date Not Found"
                    else:
                        publication_date = "Date Not Found"
                else:
                    publication_date = "Date Not Found"

                likes_tag = post.find('a', class_='zilla-likes')
                if likes_tag:
                    likes_span = likes_tag.find('span')
                    likes_count = likes_span.text.strip('"') if likes_span else "no likes"
                else:
                    likes_count = "no likes"

                blog_data.append({
                    'Blog Title': title if specific_data["Blog Title"] else None,
                    'Blog images URL': image_url if specific_data["Blog images URL"] else None,
                    'Blog Date': publication_date if specific_data["Blog Date"] else None,
                    'Blog Likes Count': likes_count if specific_data["Blog Likes Count"] else None,
                })

        else:
            break

        page_num += 1

    return blog_data

@app.route('/')

def index():
    return render_template('index.html')


@app.route('/get_blog_data', methods=['GET'])
def get_blog_data():
    base_url = request.args.get('base_url')
    blog_date = request.args.get('blog_date', default=False, type=bool)
    blog_title = request.args.get('blog_title', default=False, type=bool)
    blog_image_url = request.args.get('blog_image_url', default=False, type=bool)
    blog_likes_count = request.args.get('blog_likes_count', default=False, type=bool)

    specific_data = {
        "Blog Date": blog_date,
        "Blog Title": blog_title,
        "Blog images URL": blog_image_url,
        "Blog Likes Count": blog_likes_count,
    }

    # Validate that at least one type is requested
    if not any(specific_data.values()):
        return jsonify({"error": "At least one type of data should be requested."}), 400

    blog_data = fetch_blog_data(base_url, specific_data)
    return jsonify(blog_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)