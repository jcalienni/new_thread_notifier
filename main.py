import requests
from bs4 import BeautifulSoup
from time import sleep
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    url = "https://www.mpgh.net/forum/forumdisplay.php?s=&f=756&page=1&pp=40&daysprune=-1&sort=dateline&prefixid=&order=desc"
    
    with open("last.txt", "r", encoding="utf-8") as f:
        last_threads_list = f.read()

    while True:
        response = requests.get(url)

        if response.status_code == 200:
            # Get the HTML content of the page
            html_content = response.text
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            threads = soup.find(id="threads")
            elements = threads.find_all(lambda tag: tag.name == 'li' and tag.has_attr('id') and "thread_" in tag['id'])
            threads_list = []
            for element in elements:
                thread_title = element.find(lambda tag: tag.has_attr('id') and "thread_" in tag['id']).text
                thread_date = element.find(lambda tag: tag.has_attr('title') and "Started by " in tag['title']).next_sibling
                threads_list.append({'title': thread_title, 'date': thread_date})

            if str(threads_list) != last_threads_list:
                send_telegram_notification("\n\n".join([str(d) for d in threads_list[:4]]))
                with open("last.txt", "w", encoding="utf-8") as f:
                    f.write(str(threads_list))
                last_threads_list = str(threads_list)

        else:
            send_telegram_notification(f"Failed to retrieve the page. Status code: {response.status_code}")
        sleep(600)

def send_telegram_notification(message: str):
    requests.post(f"https://api.telegram.org/{os.getenv('BOT')}/sendMessage?chat_id={os.getenv('CHAT_ID')}&text={message}")

if __name__ == '__main__':
    main()