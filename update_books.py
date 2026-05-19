import os
import json
import re
from urllib.parse import quote

def parse_filename(filename):
    """
    升级版解析：完美兼容作者名字中带有点（. 或 ·）的情况
    匹配格式: [分类]书名-作者.扩展名
    """
    # 1. 先安全地剥离文件后缀名（无论前面有多少个点，os.path.splitext 都能精准拿到真正的后缀）
    name_without_ext, ext = os.path.splitext(filename)
    
    # 2. 用正则表达式只解析去掉后缀后的干净名称
    # 这里的 $ 确保了匹配到字符串的末尾，横杠后面的内容全部归为作者
    match = re.match(r'^\[(.*?)\](.*?)[\-—](.*?)$', name_without_ext)
    if match:
        genre = match.group(1).strip()
        title = match.group(2).strip()
        author = match.group(3).strip()
        return genre, title, author
    else:
        return "未分类", name_without_ext, "未知作者"

def main():
    books_dir = "./books"
    json_path = "./data.json"
    
    if not os.path.exists(books_dir):
        print(f"找不到 {books_dir} 文件夹，请先创建它！")
        return

    # 1. 扫描本地 books 文件夹
    local_books = {}
    for file in os.listdir(books_dir):
        if file.endswith(('.epub', '.pdf')):
            genre, title, author = parse_filename(file)
            
            encoded_file = quote(file)
            raw_url = f"https://raw.githubusercontent.com/qqhsx/book/main/books/{encoded_file}"
            
            if file.endswith('.epub'):
                viewer_path = f"/lib/epub/index.html?file={raw_url}"
            else:
                viewer_path = f"/lib/pdf/web/viewer.html?file={raw_url}"
                
            local_books[title] = {
                "title": title,
                "author": author,
                "genre": genre,
                "file_path": viewer_path
            }

    # 2. 读取现有 JSON
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try: old_data = json.load(f)
            except json.JSONDecodeError: old_data = []
    else:
        old_data = []

    new_data = []
    has_changes = False
    seen_titles = set()

    # 3. 比对更新与同步
    for book in old_data:
        title = book.get("title")
        if title in local_books:
            if (book.get("author") != local_books[title]["author"] or
                book.get("genre") != local_books[title]["genre"] or
                book.get("file_path") != local_books[title]["file_path"]):
                new_data.append(local_books[title])
                print(f"🔄 已更新书籍信息: 《{title}》")
                has_changes = True
            else:
                new_data.append(book)
            seen_titles.add(title)
        else:
            print(f"🗑️ 已移除不存在的旧数据: 《{title}》")
            has_changes = True

    # 4. 追加入库
    for title, book_info in local_books.items():
        if title not in seen_titles:
            new_data.append(book_info)
            print(f"✨ 成功自动添加: 《{title}》")
            has_changes = True

    if has_changes:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
        print("🎉 data.json 文件已完成同步更新！")
    else:
        print("😎 检查完毕：无需更新。")

if __name__ == "__main__":
    main()