from bs4 import BeautifulSoup
from datetime import datetime
import mark.markdown as markdown
import hashlib
import json
import re

class BlogEngine:
    def __init__(self, filepath, title=None):
        self.html_base_indent = 0

        self.filepath = filepath
        self.db_path = "../assets/data/articles.json"
        self.template_path = "../essays/_template_.html"

        self.db = self.read_database()
        self.title = self.filepath.replace(".md", "") if title == None else title

        self.html_dom = BeautifulSoup(self.get_html_output(), "html.parser")
        self.index_html = BeautifulSoup(open("../index.html", "r").read(), "html.parser")
        self.archive_html = BeautifulSoup(open("../archive.html", "r").read(), "html.parser")

        self.pretty_indent_regex = re.compile(r"^(\s*)", re.MULTILINE)

    def read_database(self):
        with open(self.db_path, "r") as json_file:
            json_str = json_file.read()

        if len(json_str) == 0:
            self.db = {}
            self.write_database()
            return self.db

        db = json.loads(json_str)
        return db

    def write_database(self):
        with open(self.db_path, "w") as outfile:
            outfile.write(json.dumps(self.db))
            outfile.write("\n")

    def write_html(self, filepath, bs4_obj):
        with open(filepath, "w") as outfile:
            outfile.write(self.prettify_html(bs4_obj))

    def get_html_output(self):
        with open(self.filepath, "r") as file:
            markdown_source = file.read()

        markdown_compiler = markdown.Compiler(markdown_source,
            debug_lexer=False, debug_parser=False, prettify=True
        )

        return markdown_compiler.compile(self.html_base_indent)

    # Since BeautifulSoup prettifies the html, but does it with 1 space indenting
    def prettify_html(self, bs4_obj):
        indent = 4
        return self.pretty_indent_regex.sub(r"\1" * indent, bs4_obj.prettify(None, 'minimal'))

    def create_article_html(self):
        template = BeautifulSoup(open(self.template_path, "r").read(), "html.parser")

        file = BeautifulSoup("<!DOCTYPE html>", "html.parser").new_tag("html")
        file.append(template.head)
        file.append(template.body)

        content_div = file.find("div", {"id":"content"})
        content_div.append(BeautifulSoup(self.get_html_output(), "html.parser"))

        title = file.find("title")
        title.string = f"Some thoughts: {self.title}"

        return file

    def publish_article(self):
        self.title = self.title[0].upper() + self.title[1:]

        path = self.title.replace(" ", "_")
        path = f"../essays/{path}.html"
        current_date = datetime.today().strftime("%d-%m-%Y")

        # Adding the database and writing new html file
        # Hashing the title and current date together to avoid collisions in article title
        article_hash = hashlib.md5((self.title + current_date).encode("utf-8")).hexdigest()
        new_article = {"date": current_date, "title": self.title, "path": path}
        self.db[article_hash] = new_article
        self.write_html(path, self.create_article_html())
        self.write_database()

        # Updating archive.html content div
        content_div = self.archive_html.find("div", {"id":"content"})

        new_div = self.archive_html.new_tag("div", id="article")
        title_a = self.archive_html.new_tag("a", href=path.replace("../", ""), id="title")
        title_a.string = self.title
        p = self.archive_html.new_tag("p")
        p.append(title_a)

        date_p = self.archive_html.new_tag("p", id="date")
        date_p.string = current_date

        new_div.append(date_p)
        new_div.append(p)
        content_div.append(new_div)

        self.write_html("../archive.html", self.archive_html)

    def remove_article(self):
        pass

    def feature_article(self):
        pass

    # Update projects div in index.html if nessesary
    def update_projects_list(self):
        github_api_url = "https://api.github.com/users/aabiji/repos"

engine = BlogEngine("example.md")
engine.publish_article()
