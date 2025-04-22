from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

# 讀取 .env
load_dotenv()
VOCUS_EMAIL = os.getenv("VOCUS_EMAIL")
VOCUS_PASSWORD = os.getenv("VOCUS_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("🚀 前往 Vocus 登入頁面")
    page.goto("https://vocus.cc/login")
    page.wait_for_timeout(3000)

    #HW3 填入 email 和 password
    email_input = page.locator("input[placeholder='常用 Email'][class*='sc-bd3c07ea-1']")
    email_input.click()
    page.keyboard.type(VOCUS_EMAIL, delay=100)

    password_input = page.locator("input[id='password']")
    password_input.click()
    page.keyboard.type(VOCUS_PASSWORD, delay=100)

    #HW3點擊登入
    login_button = page.locator("button.sc-2a891af6-0.hJKOrI.sc-4f5c95a4-4.drPQJ[shape='block'][type='']")
    login_button.click()

    #HW3 等待登入
    page.wait_for_timeout(5000)

    #HW3 點擊「創作」
    create_button = page.wait_for_selector("button:has(span:text('創作')):has(i.icon-addPost)", timeout=5000)
    create_button.click()
    page.wait_for_timeout(1000)

    #HW3 點擊「文章」
    write_article_button = page.locator("div[data-id='start-writing-button']")
    write_article_button.click()

    #HW3 等待文章編輯器載入
    page.wait_for_timeout(3000)

    title = page.locator("textarea[data-id='editor-title-textarea']")
    title.click()
    title.type('使用python撰寫自動發文',delay=100)

    paragraph = page.locator('p.lexical__paragraph')
    paragraph.click()
    paragraph.type('測試python撰寫內容', delay=100)

    publish = page.locator("button[data-id='ready-to-publish-button']")
    publish.scroll_into_view_if_needed()
    publish.click()

    page.locator("div.css-1uafkga-control").click()
    page.wait_for_timeout(1000)

    web3_option = page.locator("div[class*='option']:has-text('Web3')")
    web3_option.click()
    page.wait_for_timeout(1000)

    next_button = page.locator("button[data-id='publish-next-button']")
    next_button.scroll_into_view_if_needed()
    next_button.click()

    page.wait_for_timeout(1000)
    next_button = page.locator("button[data-id='publish-next-button']")   
    next_button.scroll_into_view_if_needed()     
    next_button.click()
    page.wait_for_timeout(3000)
    
    private_radio = page.locator("input#private[type='radio'][name='publishMethod'][value='private']")
    private_radio.click()
    page.wait_for_timeout(2000)

    finish_publish = page.locator("button[data-id='publish-publish-button']")
    finish_publish.click()
    page.wait_for_timeout(10000)

    go_to_article_btn = page.locator("button[data-id='publish-popup-go-to-article-button']")
    go_to_article_btn.click()
    page.wait_for_timeout(5000)
    print('成功完成V')

    browser.close()
