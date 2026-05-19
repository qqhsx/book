import os
import json
import re
from urllib.parse import quote

def parse_filename(filename):
    """
    解析文件名，匹配格式: [分类]书名-作者.扩展名
    """
    match = re.match(r'^\[(.*?)\](.*?)[\-—](.*?)\.(.*?)$', filename)
    if match:
        genre = match.group(1).strip()
        title = match.group(2).strip()
        author = match.group(3).strip()
        return genre, title, author
    else:
        name_without_ext = os.path.splitext(filename)[0]
        return "未分类", name_without_ext, "未知作者"

def main():
    books_dir = "./books"
    json_path = "./data.json"
    
    if not os.path.exists(books_dir):
        print(f"找不到 {books_dir} 文件夹，请先创建它！")
        return

    # 1. 扫描本地 books 文件夹中实际存在的所有书籍
    local_books = {}
    for file in os.listdir(books_dir):
        if file.endswith(('.epub', '.pdf')):
            genre, title, author = parse_filename(file)
            
            # 生成标准的 GitHub Raw URL 链接
            encoded_file = quote(file)
            raw_url = f"https://raw.githubusercontent.com/qqhsx/book/main/books/{encoded_file}"
            
            if file.endswith('.epub'):
                viewer_path = f"/lib/epub/index.html?file={raw_url}"
            else:
                viewer_path = f"/lib/pdf/web/viewer.html?file={raw_url}"
                
            # 以“书名”作为唯一键，记录本地最新的元数据
            local_books[title] = {
                "title": title,
                "author": author,
                "genre": genre,
                "file_path": viewer_path
            }

    # 2. 读取现有的 data.json
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                old_data = []
    else:
        old_data = []

    new_data = []
    has_changes = False
    seen_titles = set()

    # 3. 检查 JSON 中的老数据，处理“更新”和“删除”
    for book in old_data:
        title = book.get("title")
        
        # 如果这本书在本地依然存在
        if title in local_books:
            # 检查是否有内容发生变更（比如你改了分类、作者，或者改了文件名导致 file_path 变了）
            if (book.get("author") != local_books[title]["author"] or
                book.get("genre") != local_books[title]["genre"] or
                book.get("file_path") != local_books[title]["file_path"]):
                
                new_data.append(local_books[title]) # 写入本地最新的数据（实现同步更改）
                print(f"🔄 监测到内容变更，已更新书籍信息: 《{title}》")
                has_changes = True
            else:
                new_data.append(book) # 没有变动，保持原样
                
            seen_titles.add(title)
        else:
            # 如果本地已经没有这本书了（说明你删除了文件，或者改了书名）
            print(f"🗑️ 监测到本地文件已不存在，已从 JSON 中移除旧数据: 《{title}》")
            has_changes = True

    # 4. 检查本地有哪些是全新添加的临时书（JSON里还没记录的）
    for title, book_info in local_books.items():
        if title not in seen_titles:
            new_data.append(book_info)
            print(f"✨ 发现新书籍，已成功添加: 《{title}》")
            has_changes = True

    # 5. 如果发生过任何[新增/删除/修改]，重新写入 data.json
    if has_changes:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
        print("🎉 data.json 文件已完成清扫与同步更新！")
    else:
        print("😎 检查完毕：本地文件与 data.json 完全一致，无需更新。")

if __name__ == "__main__":
    main()