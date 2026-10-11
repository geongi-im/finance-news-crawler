import json
import os
import sys
import requests
import base64
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from fake_useragent import UserAgent
from utils.api_util import ApiUtil, ApiError
from utils.logger_util import LoggerUtil
from utils.telegram_util import TelegramUtil

# 네이버 언론사 코드와 언론사명 매핑
# 조간(전날 17-19시에 지면이 올라옴, 머니투데이는 당일 새벽에 올라오는 날도 있음)
#   014 파이낸셜뉴스 / 008 머니투데이 / 015 한국경제 / 009 매일경제 / 011 서울경제
# 석간(당일 오전 8-12시에 지면이 올라옴)
#   016 헤럴드경제 / 277 아시아경제
PRESS_NAME_MAP = {
    "014": "파이낸셜뉴스",
    "008": "머니투데이",
    "015": "한국경제",
    "009": "매일경제",
    "011": "서울경제",
    "016": "헤럴드경제",
    "277": "아시아경제",
}


def getFirstArticleInfo(press_code, date, headers):
    """신문 1면 페이지에서 첫 번째 기사 제목, 링크를 추출"""
    url = f"https://media.naver.com/press/{press_code}/newspaper?date={date}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"🛑 기사 목록 요청 실패: {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")
    brick_div = soup.find("div", class_="newspaper_brick_item _start_page")
    ul = brick_div.find("ul", class_="newspaper_article_lst") if brick_div else None
    first_li = ul.find("li") if ul else None
    link_tag = first_li.find("a") if first_li else None
    # newspaper_txt_box
    title = link_tag.find("div", class_="newspaper_txt_box").get_text(strip=True) if link_tag else "❌ 제목 없음"

    if not (link_tag and link_tag.has_attr("href")):
        raise Exception("🛑 기사 링크를 찾을 수 없습니다.")

    return link_tag["href"], title


def resolvePressList(codes):
    """실행 인자로 받은 언론사 코드를 수집 대상 목록으로 변환"""
    # 인자가 없으면 등록된 언론사를 전부 수집한다
    target_codes = codes if codes else list(PRESS_NAME_MAP)

    press_list = []
    unknown_codes = []
    for code in target_codes:
        name = PRESS_NAME_MAP.get(code)
        if name:
            press_list.append({"code": code, "name": name})
        else:
            unknown_codes.append(code)

    return press_list, unknown_codes


if __name__ == "__main__":
    logger = LoggerUtil().get_logger()
    api_util = ApiUtil()
    telegram = TelegramUtil()

    # 1. 수집 대상 언론사 결정 (실행 인자로 언론사 코드를 넘긴다)
    press_code_list, unknown_codes = resolvePressList(sys.argv[1:])

    for code in unknown_codes:
        logger.error(f"❌ 알 수 없는 언론사 코드: {code}")

    if not press_code_list:
        logger.error("🛑 수집할 언론사가 없습니다. 실행 인자의 언론사 코드를 확인하세요.")
        sys.exit(1)

    logger.info(f"수집 대상 언론사: {', '.join(press['name'] for press in press_code_list)}")

    # 2. 날짜 및 헤더 설정
    today = datetime.today().strftime("%Y-%m-%d")
    today_str = today.replace("-", "")
    ua = UserAgent()
    headers = {"User-Agent": ua.random}

    # 3. 기사 링크 크롤링 → 내용 크롤링
    # 언론사 단위로 예외를 처리해 한 곳이 실패해도 나머지 언론사는 계속 수집한다
    success_list = []
    fail_list = []

    for press in press_code_list:
        try:
            article_url, title = getFirstArticleInfo(press["code"], today_str, headers)
        except Exception as e:
            fail_list.append(press["name"])
            logger.error(f"❌ {press['name']} 1면 기사 크롤링 실패: {e}")
            continue

        logger.info(f"✅ {press['name']} 오늘의 뉴스 1면 기사 링크: {article_url} 제목: {title}")

        # 오늘의 뉴스 1면 API 생성
        try:
            logger.info("오늘의 뉴스 1면 API 생성 시작")
            api_util.create_top_news(
                news_date=today,
                company=press["name"],
                title=title,
                source_url=article_url
            )
            logger.info("오늘의 뉴스 1면 API 생성 완료")
            success_list.append(press["name"])
        except ApiError as e:
            fail_list.append(press["name"])
            error_message = f"❌ 오늘의 뉴스 1면 API 생성 오류\n\n{e.message}"
            telegram.send_test_message(error_message)
            logger.error(f"오늘의 뉴스 1면 API 생성 오류: {e.message}")
        except Exception as e:
            fail_list.append(press["name"])
            logger.error(f"❌ {press['name']} 오늘의 뉴스 1면 API 생성 중 예상치 못한 오류: {e}")

    logger.info(
        f"📊 처리 완료 - 성공 {len(success_list)}/{len(press_code_list)}"
        + (f" | 실패: {', '.join(fail_list)}" if fail_list else "")
    )
