import re
import requests
import json
from .Exceptions import ScratchLoginException
from .Users import YourUser, AnotherUser
from .Project import YourProject, AnotherProject
from .Studios import Studio


class Session:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self._login()
        self.studio = Studio

    def _login(self, language="en"):
        if self.username is not None and self.password is not None:
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
            self.user = YourUser(self._get_user_json(self.username), self)
            self.auth = True
        else:
            self.session_id = "NoLogged"
            self.token = None
            self.csrf_token = "NoLogged"
            self.user = None
            self.auth = False

    def _get_user_json(self, username):
        return requests.get("https://api.scratch.mit.edu/users/" + username + "/").json()

    def get_user(self, username):
        i = self._get_user_json(username)
        print(i)
        return YourUser(i, self) if self.username == i["username"] else AnotherUser(i, self)

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
