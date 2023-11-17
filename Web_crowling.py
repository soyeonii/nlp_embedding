import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait as wait
from webdriver_manager.chrome import ChromeDriverManager
from word2vec.DB_connect import DB_connect

db = DB_connect()

# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
# 불필요한 에러 메시지 없애기
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "none"

driver = webdriver.Chrome(
    executable_path=ChromeDriverManager().install(),
    options=chrome_options,
    desired_capabilities=caps,
)
driver.implicitly_wait(5)  # 웹페이지가 로딩될때까지 5초 기다림

driver.get("https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do#none")
wait(driver, 1)


def date_search(start_date, end_date):
    global driver
    # 시작날짜 입력
    input_start = driver.find_element(By.NAME, "sOpenYearS")
    input_start.send_keys(start_date)
    sleep(1)
    # 끝날짜 입력
    driver.find_element(By.NAME, "sOpenYearE").click()  # 끝날짜 텍스트창 클릭
    sleep(1)
    driver.find_element(By.NAME, "sOpenYearE").clear()  # 저절로 값이 입력되므로 텍스트창 클리어
    sleep(1)
    driver.switch_to.alert.accept()  # alert 자동 확인
    input_end = driver.find_element(By.NAME, "sOpenYearE")  # 끝날짜 텍스트창 재선택
    input_end.send_keys(end_date)  # 끝날짜 입력

    driver.find_element(
        By.XPATH, "/html/body/div[1]/div[2]/div[2]"
    ).click()  # 화면 클릭해 달력창 닫기
    sleep(1)
    driver.find_element(
        By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/form/div[1]/div[5]/button[1]"
    ).send_keys(
        Keys.ENTER
    )  # 조회 버튼 클릭 "click() 함수로는 안됨"
    sleep(1)


def last_page_check():
    global driver
    last_Page = driver.find_element(
        By.CSS_SELECTOR, "#pagingForm > div > a.btn.last"
    ).get_attribute("onclick")
    last_page_num = int(
        re.sub(r"[^0-9]", "", last_Page)
    )  # re.sub(patter, replace, str)  list가 아닌 text 형태로 바로 보기 위해서 사용
    print(last_page_num, type(last_page_num))

    return last_page_num


def data_collection(last_page_num):
    global driver
    li_index = 1
    driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div[2]/div[2]/div[4]/div[1]/div/div/select/option[4]",
    ).click()
    sleep(1)
    for _ in range(51):
        driver.find_element(By.CLASS_NAME, "btn.next").click()
        sleep(1)
    for i in range(last_page_num):
        driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[2]/div[2]/div[4]/form/div/ul/li[{}]/a".format(
                li_index
            ),
        ).click()

        sleep(1)

        tag_tbody = driver.find_element(
            By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[4]/table/tbody"
        )
        sleep(1)
        tag_tr = tag_tbody.find_elements(By.TAG_NAME, "tr")
        # 해당 페이지 목록 순회(10의 배수 아닐 때)
        for j in range(len(tag_tr)):
            sleep(1)
            tag_tr[j].find_element(
                By.XPATH,
                '//*[@id="content"]/div[4]/table/tbody/tr[{}]/td[1]/span/a'.format(
                    j + 1
                ),
            ).click()  # tag_tr 리스트 인덱스는 0번부터 XPATH 내 tr[{}] 인덱스는 1번부터
            sleep(1)
            title_value = driver.find_element(
                By.XPATH, "/html/body/div[3]/div[1]/div[1]/div/strong"
            ).text
            plot_value = driver.find_element(By.CLASS_NAME, "desc_info").text
            summary_value = driver.find_element(
                By.XPATH, "/html/body/div[3]/div[2]/div/div[1]/div[2]/dl/dd[4]"
            ).text
            poster_value = driver.find_element(By.CLASS_NAME, "fl.thumb").get_attribute(
                "href"
            )
            # ui-id-3 > div > div.item_tab.basic > div.ovf.info.info1 > a

            if (
                plot_value
                and "[주연]" not in plot_value
                and "http" not in plot_value
                and "감독" not in plot_value
                and "제작사" not in plot_value
                and "배급사" not in plot_value
                and "성애영화" not in plot_value
            ):
                if "성인물" not in summary_value and "에로" not in summary_value:
                    print(title_value, plot_value, sep="\n")
                    db.insert(
                        "INSERT INTO movies (title, plot) VALUES (%s, %s)",
                        (title_value, plot_value),
                    )

            driver.find_element(
                By.XPATH, "/html/body/div[3]/div[1]/div[1]/a[2]/span"
            ).click()  # 닫기버튼 클릭
            sleep(1)
            # 페이지 번호가 10의 배수일 때 다음 목록 클릭
        if li_index % 10 == 0:
            driver.find_element(By.CLASS_NAME, "btn.next").click()  # 다음 페이지 목록
            li_index = 0
            sleep(1)
        li_index += 1


# start_date = '1900-01-01'
# end_date = '2023-11-13'

# date_search(start_date, end_date)
last_page_num = last_page_check()
data_collection(last_page_num)
