#!/usr/bin/env python

from engine import BlogEngine
import os, re
import shutil
import sys

username = "aabiji"
cache_folder = f"/home/{username}/projects/blog/.cached"
execution_path = f"/home/{username}/projects/blog/engine"

def help():
    print("Usage: ")
    print("blog create FILENAME TITLE  | Creates a new blog article.")
    print("blog update FILENAME TITLE  | Updated a existing blog article.")
    print("blog feature TITLE          | Features a blog article (puts it in index.html)")
    print("blog remove  TITLE          | Removes a blog article")
    print("blog list                   | Lists all blog articles.")

def load_article_assets(arguments: list):
    global execution_path, cache_folder
    filename = arguments[1]

    if not os.path.isfile(filename):
        sys.exit(f"File not found: {filename}")

    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    img_regex = re.compile(r"!\[.+]\(.+\)")
    markdown_source = open(filename, "r").read()

    for match in img_regex.findall(markdown_source):
        img_alt = match.split("[")[0].replace("[", "")
        img_path = match.split("(")[1].replace(")", "").strip()
        shutil.copy(img_path, cache_folder)

        new_img_path = f"{cache_folder}/{filename}"
        markdown_source.replace(match, f"![{img_alt}]({new_img_path})")

    with open(f"{cache_folder}/{filename}", "w") as outfile:
        outfile.write(markdown_source)

def cleanup(arguments: list):
    global execution_path, cache_folder
    filename = arguments[1]
    shutil.rmtree(cache_folder)

def process_arguments(arguments: list):
    global execution_path

    if len(arguments) == 3:
        load_article_assets(arguments)

    os.chdir(execution_path)
    blog_engine = BlogEngine()
    blog_engine.update_projects_list()

    if len(arguments) == 1 and arguments[0] == "list":
        blog_engine.list_articles()

    elif len(arguments) == 2:
        title = arguments[1]

        if arguments[0] == "remove":
            blog_engine.remove_article(title)

        elif arguments[0] == "feature":
            blog_engine.feature_article(title)

    elif len(arguments) == 3:
        filename, title = f"{cache_folder}/{arguments[1]}", arguments[2]

        if arguments[0] == "create":
            blog_engine.create_article(filename, title)
    
        elif arguments[0] == "update":
            blog_engine.update_article(filename, title)

        cleanup(arguments)    

    else:
        help()
        sys.exit()
   
def publish(arguments: list):
    if arguments[0] != "list":
        title = arguments[1]
        if arguments[0] == "create" or arguments[0] == "update":
            title = arguments[2]

        commit_msg = f"{arguments[0]} {title}"
        os.system("git add .")
        os.system(f"git commit -m '{commit_msg}'")
        os.system("git push -u origin main")

if __name__ == "__main__":
    arguments = sys.argv[1:]
    process_arguments(arguments)
    publish(arguments)
