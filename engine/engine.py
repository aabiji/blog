from mark import markdown
from datetime import datetime
from bs4 import BeautifulSoup
import hashlib
import requests
import json
import re
import os

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

        self.tag_regex = re.compile(r"\s*<.+>")
        self.indent_regex = re.compile(r"^(\s*)", re.MULTILINE)
        self.indent = 4

    def load_database(self):
        with open(self.db_path, "r") as file:
            contents = file.read()

        if len(contents) > 0:
            return json.loads(contents)
        else:
            return {"articles": {}, "featured": {}, "projects_count": 0}

    def update_database(self):
        with open(self.db_path, "w") as file:
            file.write(json.dumps(self.db))

    def write_html(self, filepath: str, dom_obj: BeautifulSoup):
        html = self.indent_regex.sub(r"\1" * self.indent, dom_obj.prettify())
        html = html.split("\n")

        # Correcting a weird indentation anomality in BeautifulSoup.prettify
        inside_codeblock = False
        for i in range(len(html)):
            line = html[i]
            
            if "<code>" in line:
                inside_codeblock = True
            elif "</code>" in line:
                inside_codeblock = False

            if not self.tag_regex.match(line) and not inside_codeblock:
                if not self.tag_regex.match(html[i - 1]) and i > 0:
                    previous_whitespace_count = len(html[i - 1]) - len(html[i - 1].lstrip())
                    html[i] = html[i].lstrip()
                    html[i] = (" " * previous_whitespace_count) + html[i]

        html_str = ""
        for i in html:
            html_str += i + "\n"

        with open(filepath, "w") as file:
            file.write(html_str)

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
            self.filename = self.filename.split("(")[0].rstrip() + f" ({iteration if iteration > 0 else ''})"

        date = datetime.today().strftime("%d-%m-%Y")
        title_hash = hashlib.md5(self.title.encode("utf-8")).hexdigest()

        path = f"../essays/{self.title.replace(' ', '_')}.html"
        html = self.markdown_compiler.compile(self.base_indent)

        entry = {"date": date, "title_hash": title_hash, "path": path}
        self.db[table][self.title] = entry
        self.update_database()

        return self.title, entry, html

    def create_archive_entry(self, html: BeautifulSoup, title: str, entry: dict):
        article_div = html.new_tag("div", **{"class": "article"}, id=entry['title_hash'])
        p = html.new_tag("p", id="date")
        p.string = entry['date']

        link_wrapper = html.new_tag("p")
        link = html.new_tag("a", id="title", href=entry['path'].replace("../", ""))
        link.string = title
        link_wrapper.append(link)

        article_div.append(p)
        article_div.append(link_wrapper)

        return article_div

    # $ blog create FILENAME TITLE
    def create_article(self):
        title, entry, html = self.insert_entry("articles", False)

        self.base_indent = 3
        content_div = self.template_html.find("div", {"id": "content"})
        content_div.append(BeautifulSoup(html, "html.parser"))
        self.write_html(f"../essays/{self.title}.html", self.template_html)

        archive_content_div = self.archive_html.find("div", {"id":"content"})
        archive_content_div.append(self.create_archive_entry(self.archive_html, title, entry))

        self.write_html("../archive.html", self.archive_html)

    def update_article_listing(self, html: BeautifulSoup, title: str, entry: dict):
        previous_article_div = html.find("div", {"id": entry['title_hash']})
        previous_article_div.decompose()

        content_div = html.find("div", {"id": "content"})
        h3 = content_div.find("h3")
        h3.decompose()

        content_div.insert(1, self.create_archive_entry(html, title, entry))
        new_h3 = html.new_tag("h3")
        new_h3.string = "My writings"
        content_div.insert(1, new_h3)

        self.write_html("../archive.html", html)

    # $ blog update FILENAME TITLE
    def update_article(self):
        if self.title not in self.db['articles']:
            print(f"Article not found: {self.title}")
            return

        title, entry, html = self.insert_entry("articles", True)
        if self.title in self.db['featured']:
            self.insert_entry("featured", True)

        archive_content_div = self.archive_html.find("div", {"id": "content"})
        index_content_div = self.index_html.find("div", {"id": "content"})
        
        if len(archive_content_div.find_all("div", {"id": entry["title_hash"]})) > 0:
            self.update_article_listing(self.archive_html, title, entry)

        if len(index_content_div.find_all("div", {"id": entry["title_hash"]})) > 0:
            self.update_article_listing(self.index_html, title, entry)

    # $ blog remove TITLE
    def remove_article(self):
        if self.title not in self.db['articles']:
            print(f"Article not found: {self.title}")
            return

        entry = self.db['articles'][self.title]

        if len(self.archive_html.find_all("div", {"id": entry['title_hash']})) > 0:
            archive_entry_div = self.archive_html.find("div", {"id": entry['title_hash']})
            archive_entry_div.decompose()
            self.write_html("../archive.html", self.archive_html)

        # If article has been marked as favorite
        if len(self.index_html.find_all("div", {"id": entry['title_hash']})) > 0:
            index_entry_div = self.index_html.find("div", {"id": entry['title_hash']})
            index_entry_div.decompose()
            self.write_html("../index.html", self.index_html)

        # Remove assets associated with it
        os.remove(entry['path'])

        del self.db['articles'][self.title]
        if self.title in self.db['featured']:
            del self.db['featured'][self.title]

        self.update_database()
   
    # $ blog feature TITLE
    # Like creating a blog article, except the html file for the article is already present
    def feature_article(self):
        if self.title not in self.db['articles']:
            print(f"Article not found: {self.title}")
            return

        title, entry, html = self.insert_entry("featured", False)
        index_html_content_div = self.index_html.find("div", {"id": "content"})
        index_html_content_div.append(self.create_archive_entry(self.index_html, title, entry))
        self.write_html("../index.html", self.index_html)

    def list_table(self, table: str):
        print(" " * 15, "-" * 15, table[0].upper() + table[1:], "-" * 15)

        max_title_length = 3
        for key in self.db[table]:
            if len(key) > max_title_length:
                max_title_length = len(key)

        for key in self.db[table]:
            i = self.db['articles'][key]
            title, date, title_hash, path = key, i['date'], i['title_hash'], i['path']
            print(f"{date}   ", end="")
            print(title, " " * (max_title_length - len(key)), "   ", end="")
            print(f"# {title_hash}   @ {path}")

        print()

    # $ blog list
    def list_articles(self):
        self.list_table("featured")
        self.list_table("articles")
