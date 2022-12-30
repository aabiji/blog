from mark import markdown
from datetime import datetime
from bs4 import BeautifulSoup
import hashlib
import requests
import json
import re

class BlogEngine:
    def __init__(self, filename: str, title=None):
        self.filename = filename
        self.title = title if title != None else filename.replace(".md", "")
        self.title = self.title[0].upper() + self.title[1: ]

        self.base_indent = 0
        self.markdown_source = open(self.filename, "r").read()
        self.markdown_compiler = markdown.Compiler(self.markdown_source, 
            debug_lexer=False, debug_parser=False, prettify=True
        )

        self.db_path = "../assets/data/blog.json"
        self.db = self.load_database()

        self.index_html_raw = open("../index.html", "r").read()
        self.archive_html_raw = open("../archive.html", "r").read()
        self.template_html_raw = open("../essays/__template__.html", "r").read()

        self.index_html = BeautifulSoup(self.index_html_raw, "html.parser")
        self.archive_html = BeautifulSoup(self.archive_html_raw, "html.parser")
        self.template_html = BeautifulSoup(self.template_html_raw, "html.parser")

        self.indent_regex = re.compile(r"^(\s*)", re.MULTILINE)
        self.indent = 4
    
    def load_database(self):
        with open(self.db_path, "r") as file:
            contents = file.read()

        if len(contents) > 0:
            return json.loads(contents)
        else:
            return {"articles": {}, "favorites": [], "projects_count": 0}

    def update_database(self):
        with open(self.db_path, "w") as file:
            file.write(json.dumps(self.db))

    def write_html(self, filepath: str, dom_obj: BeautifulSoup):
        html = self.indent_regex.sub(r"\1" * self.indent, dom_obj.prettify())
        with open(filepath, "w") as file:
            file.write(html)

    def update_projects_list(self):
        repo_api = "https://api.github.com/users/aabiji/repos"
        response = requests.get(repo_api).json()
        
        if len(response) != self.db['projects_count']:
            projects_div = self.index_html.find("div", {"id": "projects"})

            for existing_child in projects_div.find_all():
                existing_child.decompose()

            h3 = self.index_html.new_tag("h3")
            h3.string = "Some things I've built: "
            projects_div.append(h3)

            for i in response:
                name, description, html_url = i['name'], i['description'], i['html_url']

                new_project_div = self.index_html.new_tag("div", id="project")
                link = self.index_html.new_tag("a", href=html_url)
                link.string = name
                p = self.index_html.new_tag("p")
                p.string = description

                new_project_div.append(link)
                new_project_div.append(p)
                projects_div.append(new_project_div)

            projects_div.append(self.index_html.new_tag("hr"))

            self.db['projects_count'] = len(response)
            self.update_database()
            self.write_html("../index.html", self.index_html)

    # If creating_entry=True, the value associated with it's key should be overwritten
    def insert_entry(self, table: str, creating_entry: bool):
        # Resolving conflicts in blog article title
        iteration = 0
        while self.title in self.db[table] and not creating_entry:
            iteration += 1
            self.title = self.title.split("(")[0].rstrip() + f" ({iteration if iteration > 0 else ''})"

        date = datetime.today().strftime("%d-%m-%Y")
        title_hash = hashlib.md5(self.title.encode("utf-8")).hexdigest()

        self.filename = self.filename.replace(".md", "")
        self.filename = self.filename.split("/")[-1]
        self.filename = self.filename[0].upper() + self.filename[1:]
        path = f"../essays/{self.filename}.html"

        html = self.markdown_compiler.compile(self.base_indent)

        entry = {"date": date, "title_hash": title_hash, "path": path}
        self.db[table][self.title] = entry
        self.update_database()

        return self.title, entry, html

    def create_archive_entry(self, title: str, entry: dict):
        article_div = self.archive_html.new_tag("div", **{"class": "article"}, id=entry['title_hash'])
        p = self.archive_html.new_tag("p", id="date")
        p.string = entry['date']

        link_wrapper = self.archive_html.new_tag("p")
        link = self.archive_html.new_tag("a", id="title", href=entry['path'].replace("../", ""))
        link.string = title
        link_wrapper.append(link)

        article_div.append(p)
        article_div.append(link_wrapper)

        return article_div

    def create_article(self):
        title, entry, html = self.insert_entry("articles", False)

        self.base_indent = 3
        content_div = self.template_html.find("div", {"id": "content"})
        content_div.append(BeautifulSoup(html, "html.parser"))
        self.write_html("test.html", self.template_html)

        archive_content_div = self.archive_html.find("div", {"id":"content"})
        archive_content_div.append(self.create_archive_entry(title, entry))

        self.write_html("../archive.html", self.archive_html)

    def _update_article(self, html: BeautifulSoup, title: str, entry: dict):
        previous_article_div = html.find("div", {"id": entry['title_hash']})
        previous_article_div.decompose()

        content_div = html.find("div", {"id": "content"})
        h3 = content_div.find("h3")
        h3.decompose()

        content_div.insert(1, self.create_archive_entry(title, entry))
        new_h3 = html.new_tag("h3")
        new_h3.string = "My writings"
        content_div.insert(1, new_h3)

        self.write_html("../archive.html", html)

    def update_article(self):
        title, entry, html = self.insert_entry("articles", True)

        archive_content_div = self.archive_html.find("div", {"id": "content"})
        index_content_div = self.index_html.find("div", {"id": "content"})
        
        if len(archive_content_div.find_all("div", {"id": entry["title_hash"]})) > 0:
            self._update_article(self.archive_html, title, entry)

        if len(index_content_div.find_all("div", {"id": entry["title_hash"]})) > 0:
            self._update_article(self.index_html, title, entry)

e = BlogEngine("example.md", "Example (2)")
e.update_article()
