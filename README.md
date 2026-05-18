### 本仓库目录结构规范

qqhsx/book (仓库根目录)  
├── .github/  
│   └── workflows/  
│       └── auto_update.yml       # GitHub Actions 自动化工作流配置文件  
├── books/                        # 电子书源文件存放处（不按分类建子文件夹）  
│   ├── 经济学原理.pdf  
│   └── 动物农场.epub  
├── covers/                       # 书籍封面图片存放处  
│   ├── 经济学原理.jpg  
│   └── 动物农场.jpg  
├── .gitignore                    # 忽略临时文件（如 Python 缓存）  
├── README.md                     # 仓库说明文档  
├── data.json                     # 自动生成的数据库文件（Hexo 读取它）  
└── update_books.py               # 核心自动化 Python 脚本  



#### PDF 文件的“命名协议”

正如前面所说，EPUB 可以被脚本自动读取作者、书名，但 **PDF 往往读不出来**。为了让脚本能自动提取 PDF 的信息，建议你在上传 PDF 时，采用固定的命名格式。

- **推荐格式**：`[分类]作者-书名.pdf`
- **示例**：`[经济]亚当·斯密-国富论.pdf`
- **脚本解析逻辑**：Python 脚本看到这个文件名，会自动切片：
  - 中括号里的是 `genre`（经济）
  - 横杠前面的是 `author`（亚当·斯密）
  - 横杠后面的是 `title`（国富论）