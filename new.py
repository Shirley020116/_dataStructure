import requests
import csv

url = "https://www.odaily.news/v1/openapi/feeds_zhtw"

# filter news accorrding to the keywords
keywords = ["BTC", "比特幣", "Bitcoin", "ETH", "以太坊"]
filtered_articles = []

for i in range(8):
  params = {"length": i + 1}
  response = requests.get(url, params=params)

  if response.status_code == 200:
    data = response.json().get("data",{})
    new_list = data.get("arr_news",[])

    for article in new_list:
      title = article.get("title", "")
      desc = article.get('description',"")
      combined_text = title + desc

      if any(kw.lower() in combined_text.lower() for kw in keywords):
        filtered_articles.append({
          "title": title,
          "description": desc,
          "published_at": article.get("published_at"),
          "link": article.get("link"),
          "type": article.get("type"),
          "id": article.get("id"),
          })
  else:
    print(f"第 {i+1} 天請求失敗，status_code: {response.status_code}")


csv_file = "filtered_crypto_news.csv"
with open(csv_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=filtered_articles[0].keys())
    writer.writeheader()
    writer.writerows(filtered_articles)

print(f"共篩選出 {len(filtered_articles)} 筆新聞，已儲存至 {csv_file}")
