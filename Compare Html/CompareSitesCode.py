from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import etree
import json

def fetch_and_save_html(url, filename):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)

    driver.get(url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    html_content = driver.page_source

    soup = BeautifulSoup(html_content, 'html.parser')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    driver.quit()
    print(f"HTML content for {url} saved as '{filename}'")



from lxml.etree import _Element

def get_tags_with_text_with_lines_from_file(file_path):
    with open(file_path, 'rb') as f:
        parser = etree.HTMLParser()
        tree = etree.parse(f, parser)

    tags_with_details = []
    for elem in tree.iter():
        try:
            # Only process real element tags (skip comments, doctypes, etc.)
            if not isinstance(elem, _Element):
                continue

            tag_name = elem.tag
            if not isinstance(tag_name, str):
                continue  # Skip weird node types like comments or doctypes

            line_number = elem.sourceline

            inner_text = elem.text.strip() if elem.text else ''
            if not inner_text:
                continue  

            full_html = etree.tostring(elem, encoding='unicode', method='html')
            num_lines = full_html.count('\n')
            end_line = line_number + num_lines if line_number else None

            tags_with_details.append({
                'tag': tag_name,
                'text': inner_text,
                'start_line': line_number,
                'end_line': end_line
            })
        except Exception:
            continue

    return tags_with_details




def extract_matching_tags(file1, file2, output_json):
    tags1 = get_tags_with_text_with_lines_from_file(file1)
    tags2 = get_tags_with_text_with_lines_from_file(file2)

    matching_tags = []
    for t1 in tags1:
        for t2 in tags2:
            if t1['tag'] == t2['tag'] and t1['text'] == t2['text']:
                matching_tags.append({
                    "Tag Name": str(t1['tag']),
                    "Inner Text": str(t1['text']),
                    "File1 Start Line": int(t1['start_line']) if t1['start_line'] else None,
                    "File1 End Line": int(t1['end_line']) if t1['end_line'] else None,
                    "File2 Start Line": int(t2['start_line']) if t2['start_line'] else None,
                    "File2 End Line": int(t2['end_line']) if t2['end_line'] else None
                })
                break

    with open(output_json, 'w', encoding='utf-8') as jsonfile:
        json.dump(matching_tags, jsonfile, indent=4)

    print(f"Matching tags saved to '{output_json}'")



if __name__ == "__main__":
    url1 = input("Enter the first URL: ")
    url2 = input("Enter the second URL: ")

    file1 = 'page_content_1.html'
    file2 = 'page_content_2.html'
    output_json = 'matching_tags.json'  

    fetch_and_save_html(url1, file1)
    fetch_and_save_html(url2, file2)
    extract_matching_tags(file1, file2, output_json)
