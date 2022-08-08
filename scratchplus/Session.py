import re
import requests
import json
from .Exceptions import ScratchLoginException, ScratchForumException, UserNotFound
from .Users import YourUser, AnotherUser
from .Project import YourProject, AnotherProject
from .Studios import Studio
from .Comments import ScratchDataComment
from .Cloud import CloudConnection
from .Forum import ForumPost, ForumTopic


class Session:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._login()
        self.studio = Studio
        self.CloudConnection = CloudConnection

    def _login(self, language="en"):
        if True:
            headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": f"scratchcsrftoken=a;scratchlanguage={language};",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }
            data = json.dumps({"username": self.username, "password": self.password})

            request = requests.post(
                "https://scratch.mit.edu/login/", data=data, headers=headers
            )

            try:
                self.session_id = re.search('"(.*)"', request.headers["Set-Cookie"]).group()
                self.token = request.json()[0]["token"]
            except AttributeError:
                raise ScratchLoginException("Your login password or username is incorrect")
            headers = {
                "x-requested-with": "XMLHttpRequest",
                "Cookie": f"scratchlanguage={language};permissions=%7B%7D;",
                "referer": "https://scratch.mit.edu",
            }
            request = requests.get("https://scratch.mit.edu/csrf_token/", headers=headers)
            self.csrf_token = re.search(
                "scratchcsrftoken=(.*?);", request.headers["Set-Cookie"]
            ).group(1)
            self.auth = True
    @property
    def user(self):
        self.user = YourUser(self._get_user_json(self.username), self)
        return YourUser(self._get_user_json(self.username), self)
    def get_topics_from_category(self, category: str, removed_topics=False, page: int = 1):
        r = requests.get(
            f"https://scratchdb.lefty.one/v3/forum/category/topics/{category}/{page}?detail=1&filter={str(int(removed_topics))}")
        jsn = r.json()
        out = list()
        try:
            jsn["error"]
        except:
            pass
        else:
            raise ScratchForumException(jsn["error"]+": "+jsn["message"])
        for i in jsn:
            out.append(ForumTopic(i, self))
        return out

    def change_password(self, new_password: str):
        URL = 'https://scratch.mit.edu/accounts/password_change/'
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchlanguage=en;permissions=%7B%7D;scratchsessionsid=" + self.session_id + ";" + "scratchcsrftoken=" + '"' + self.csrf_token + '"' + ";",
            "referer": URL,

        }
        data = {"old_password": self.password,
                "new_password1": new_password,
                "new_password2": new_password,
                "csrfmiddlewaretoken": self.csrf_token}
        r = requests.post(URL, data=data, headers=headers)

    def change_country(self, country: str):
        URL = 'https://scratch.mit.edu/accounts/settings/'
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchlanguage=en;permissions=%7B%7D;scratchsessionsid=" + self.session_id + ";" + "scratchcsrftoken=" + '"' + self.csrf_token + '"' + ";",
            "referer": URL,

        }
        data = {"country": country,
                "csrfmiddlewaretoken": self.csrf_token}
        r = requests.post(URL, data=data, headers=headers)

    def change_email(self, email: str):
        URL = 'https://scratch.mit.edu/accounts/email_change/'
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchlanguage=en;permissions=%7B%7D;scratchsessionsid=" + self.session_id + ";" + "scratchcsrftoken=" + '"' + self.csrf_token + '"' + ";",
            "referer": URL,

        }
        data = {"email": email,
                "password": self.password,
                "csrfmiddlewaretoken": self.csrf_token}

        r = requests.post(URL, data=data, headers=headers)

    def get_forum_post(self, post_id: int):
        r = requests.get(f"https://scratchdb.lefty.one/v3/forum/post/info/{post_id}")
        js = r.json()
        try:
            js["error"]
        except:
            return ForumPost(js, self)
        else:
            raise ScratchForumException(js["error"])

    def get_posts_list(self, topic_id: int, page: int = 0, order: str = "newest"):
        """
        :param topic_id: Topic id
        :param page: Each page has 50 posts, default is page 0
        :param order: Order to sort posts by, defaults to "newest", possible options include "oldest"
        :return: Return list of ForumPost from this forum
        """
        url = f"https://scratchdb.lefty.one/v3/forum/topic/posts/{topic_id}/{page}?o={order}"
        jsn = requests.get(url).json()
        try:
            jsn["error"]
        except:
            return [ForumPost(i, self) for i in jsn]
        else:
            raise ScratchForumException(jsn["error"])

    def get_topic(self, topic_id: str):
        r = requests.get(f"https://scratchdb.lefty.one/v3/forum/topic/info/{topic_id}")
        if "[]" == r.text:
            raise ScratchForumException("Unknown error, or topic not found")
        js = r.json()

        try:
            js["error"]
        except:
            return ForumTopic(js, self)
        else:
            raise ScratchForumException(js["error"])

    def _get_user_json(self, username):
        return requests.get("https://api.scratch.mit.edu/users/" + username + "/").json()

    def get_user(self, username):
        i = self._get_user_json(username)
        try:
            return YourUser(i, self) if self.username == i["username"] else AnotherUser(i, self)
        except:
            raise UserNotExits(f"User {username} is not found")

    def _get_project_json(self, id):
        return requests.get(
            "https://api.scratch.mit.edu/projects/" + str(id) + "/"
        ).json()

    def get_project(self, id):
        i = self._get_project_json(id)
        return YourProject(i, self) if self.username == i["username"] else AnotherProject(i, self)

    def _get_studio_json(self, id):
        return requests.get("https://api.scratch.mit.edu/studios/" + str(id) + "/").json()

    def get_studio(self, id):
        i = self._get_studio_json(id)
        return Studio(i, self)

    def _explore_projects_json(self, mode):
        return requests.get(
            "https://api.scratch.mit.edu/explore/projects/?mode="
            + mode
            + "&q=*"
        ).json()

    def explore_projects(self, mode="trending"):
        i = self._explore_projects_json(mode)
        return [
            YourProject(project, self) if project["author"]["username"] == self.username else AnotherProject(project,
                                                                                                             self)
            for project in i]

    def _search_projects_json(self, mode, query):
        return requests.get(
            "https://api.scratch.mit.edu/explore/projects/?mode="
            + mode
            + "&q="
            + query
        ).json()

    def search_projects(self, mode="popular", query='*'):
        i = self._search_projects_json(mode, query)
        return [
            YourProject(project, self) if project["author"]["username"] == self.username else AnotherProject(project,
                                                                                                             self)
            for project in i]

    def find_comments(self, query=""):
        comments = requests.get(f"https://sd.sly-little-fox.ru/api/v1/search?q={query}").json()
        return [ScratchDataComment(i, self) for i in comments]
