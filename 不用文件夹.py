import pprint
import time
import os
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options
import markdownify
from bs4 import BeautifulSoup
import requests


def html_to_markdown(html_content, base_url=None):
    """
    将 HTML 转换为 Markdown，并保留图片的原始外链。
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 更新图片路径为绝对路径（如果需要）
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and base_url:
            img['src'] = urljoin(base_url, src)

    markdown_content = markdownify.markdownify(str(soup))
    return markdown_content


# 传入正确的资源url,得到对应的markdown文档
def get_markdown(url, path):
    driver.get(url)
    time.sleep(2)  # 等待 JS 加载
    source = driver.page_source
    max_length = len(source)

    # 尝试获取最长的页面内容
    for _ in range(2):
        driver.get(url)
        time.sleep(2)  # 等待 JS 加载
        if max_length < len(driver.page_source):
            max_length = len(driver.page_source)
            source = driver.page_source

    # 转换 HTML 为 Markdown，同时保留图片的外链
    markdown_content = html_to_markdown(source, base_url=url)

    # 保存 Markdown 文件
    with open(path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)


def get_gen(url):
    """
    获取资源根目录
    """
    if url.find(".html"):
        _ = url.split("/")
        for item in _:
            try:
                if item.find(".html") != -1:
                    index = url.find(item)
                    url1 = url[:index]
                    print(url1)
                    return url1
            except Exception as e:
                return ""


def get_start(url):
    """
    获取可访问的根目录
    """
    url = get_gen(url)
    r = requests.get(url)
    if r.status_code == 200:
        return url
    else:
        try:
            while requests.get(url).status_code != 200:
                url = url.rsplit("/", 2)[0]
            return url + "/"
        except Exception as e:
            return ""


def get_index_element1(url):
    """
    根据根目录获取目录结构
    """
    url = get_start(url)
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements_with_href = soup.find_all(href=True)

    elements = []
    for element in elements_with_href:
        if 'class' in element.attrs:
            elements.append(element)

    # 统计类出现的次数
    pin = {}
    for element in elements:
        class_str = str(element["class"])
        if class_str in pin:
            pin[class_str] += 1
        else:
            pin[class_str] = 1

    # 过滤掉出现次数小于等于 2 的元素
    elements = [element for element in elements if pin[str(element["class"])] > 2]
    # 去重
    elements = list(dict.fromkeys(elements))
    # 过滤掉空文本的元素
    elements = [element for element in elements if element.get_text()]

    return elements


def get_index1(url, tree, start_url):
    """
    构建一级目录
    """
    elements = get_index_element1(url)
    for element in elements:
        tree[element.get_text()] = {
            "href": start_url + element["href"],
            "index": len(tree),
            "child": {}
        }


def baocun(tree):
    """
    保存文件树
    """
    for node1 in tree:
        # 清理文件名
        file_name = node1.replace("\\", "").replace("/", "").strip()
        file_path = f"{file_name}.md"

        try:
            # 保存 Markdown 文件到当前目录
            get_markdown(tree[node1]["href"], file_path)
        except Exception as e:
            print(f"保存文件 {file_path} 时出错: {e}")


if __name__ == '__main__':
    tree = {}  # 字典表示结构
    # 替换为实际的 URL
    url = "https://dockertips.readthedocs.io/en/latest/docker-install/docker-intro.html"
    start_url = get_start(url)
    zi_yuan_url = get_gen(url)

    service = Service(EdgeChromiumDriverManager().install())
    options = Options()
    options.add_argument('--headless')  # 如果需要无头模式可以取消注释
    driver = webdriver.Edge(service=service, options=options)

    get_index1(url, tree, start_url)
    pprint.pprint(tree)
    baocun(tree)