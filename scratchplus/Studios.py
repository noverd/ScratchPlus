import requests
import json
import bs4
from .Users import AnotherUser, YourUser
from .Project import YourProject, AnotherProject


class Studio:
    def __init__(self, data, client):
        self.id = data["id"]
        self.title = data["title"]
        self.host = data["host"]
        self.description = data["description"]
        self.thumbnail_URL = data["image"]
        self.visible = data["visibility"] == "visibile"
        self.open_to_public = data["open_to_all"]

        self.created_timestamp = data["history"]["created"]
        self.last_modified_timestamp = data["history"]["modified"]

        self._client = client
        self._headers = {
            "x-csrftoken": self._client.csrf_token,
            "X-Token": self._client.token,
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchcsrftoken="
                      + self._client.csrf_token
                      + ";scratchlanguage=en;scratchsessionsid="
                      + self._client.session_id
                      + ";",
            "referer": "https://scratch.mit.edu/studios/" + str(self.id) + "/",
        }

    def set_to_public(self, q: bool):
        URL = f'https://scratch.mit.edu/site-api/galleries/{self.id}/mark/' + "open/" if q else "closed/"
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchlanguage=en;permissions=%7B%7D;scratchsessionsid=" + self._client.session_id + ";" + "scratchcsrftoken=" + '"' + self._client.csrf_token + '"' + ";",
            "referer": URL,

        }
        r = requests.put(URL, headers=headers)

    def get_comments(self, page: int = 1):
        url = f"https://scratch.mit.edu/site-api/comments/gallery/{self.id}/?page={page}"
        sp = bs4.BeautifulSoup(requests.get(url).content, "html.parser")
        comments = sp.find_all("li", {"class": "top-level-reply"})
        ret = []
        if len(comments) < 1:
            return []
        for i in comments:
            replies = []
            replies_list = i.find_all("li", {"class": "reply"})
            if len(replies_list) > 0:
                IsReply = True
            else:
                IsReply = False
            for x in replies_list:
                reply = {
                    'CommentID': x.find("div", {"class": "comment"})['data-comment-id'],
                    'Username': x.find("a", {"id": "comment-user"})['data-comment-user'],
                    'Content': str(x.find("div", {"class": "content"}).text).strip(),
                    'Time': x.find("span", {"class": "time"})['title'],
                    "IsReply": True,
                    'replies': []
                }
                replies.append(reply)

            comment = {
                'CommentID': i.find("div", {"class": "comment"})['data-comment-id'],
                'Username': i.find("a", {"id": "comment-user"})['data-comment-user'],
                'Content': str(i.find("div", {"class": "content"}).text).strip(),
                'Time': i.find("span", {"class": "time"})['title'],
                'IsReply': IsReply,
                'replies': replies
            }
            ret.append(comment)
        return ret

    def get_managers(self, limit: int = 20, offset: int = 0, all = False):
        if all:
            URL = f"https://api.scratch.mit.edu/studios/{self.id}/managers/?limit={limit}&offset="
            managers = []
            while True:
                res = requests.get(URL + str(offset)
                                   ).json()
                for i in res:
                    managers.append(i)
                if len(res) != 40:
                    break
                offset += 40
            return [
                YourUser(i, self._client) if i["username"] == self._client.username else AnotherUser(i,
                                                                                                     self._client)
                for i in managers]
        else:
            URL = f"https://api.scratch.mit.edu/studios/{self.id}/managers/?limit={limit}&offset={offset}"
            managers = requests.get(URL).json()
            return [
                YourUser(i, self._client) if i["username"] == self._client.username else AnotherUser(i,
                                                                                                     self._client) for i in managers]

    def add_project(self, project):
        project_id = project.id if isinstance(project, YourProject) or isinstance(project, AnotherProject) else project
        headers = self._headers
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(project_id) + "/"
        requests.post(
            "https://api.scratch.mit.edu/studios/"
            + str(self.id)
            + "/project/"
            + project_id
            + "/",
            headers=headers,
        )

    def remove_project(self, project):
        project_id = project.id if isinstance(project, YourProject) or isinstance(project, AnotherProject) else project
        headers = self._headers
        headers["referer"] = "https://scratch.mit.edu/projects/" + str(project_id) + "/"
        requests.post(
            "https://api.scratch.mit.edu/studios/"
            + str(self.id)
            + "/project/"
            + project_id
            + "/",
            headers=headers,
        )

    def open_to_public(self):
        requests.put(
            "https://scratch.mit.edu/site-api/galleries/"
            + str(self.id)
            + "/mark/open/",
            headers=self._headers,
        )

    def close_to_public(self):
        requests.put(
            "https://scratch.mit.edu/site-api/galleries/"
            + str(self.id)
            + "/mark/closed/",
            headers=self._headers,
        )

    def follow(self):
        return requests.put(
            "https://scratch.mit.edu/site-api/users/bookmarkers/"
            + str(self.id)
            + "/add/?usernames="
            + self._client.username,
            headers=self._headers,
        ).json()

    def unfollow(self):
        return requests.put(
            "https://scratch.mit.edu/site-api/users/bookmarkers/"
            + str(self.id)
            + "/remove/?usernames="
            + self._client.username,
            headers=self._headers,
        ).json()

    def toggle_commenting(self):
        headers = self._headers
        headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.id) + "/comments/"
        )
        requests.post(
            "https://scratch.mit.edu/site-api/comments/gallery/"
            + str(self.id)
            + "/toggle-comments/",
            headers=headers,
        )

    def post_comment(self, content, parent_id="", commentee_id=""):
        headers = self._headers
        headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.id) + "/comments/"
        )
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        requests.post(
            "https://scratch.mit.edu/site-api/comments/gallery/"
            + str(self.id)
            + "/add/",
            headers=headers,
            data=json.dumps(data),
        )

    def delete_comment(self, comment_id, username):
        headers = self._headers
        headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.id) + "/comments/"
        )
        data = {"id": comment_id}
        requests.post(
            "https://scratch.mit.edu/site-api/comments/user/" + username + "/del/",
            headers=headers,
            data=json.dumps(data),
        )

    def report_comment(self, comment_id, username):
        headers = self._headers
        headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.id) + "/comments/"
        )
        data = {"id": comment_id}
        requests.post(
            "https://scratch.mit.edu/site-api/comments/user/" + username + "/rep/",
            headers=headers,
            data=json.dumps(data),
        )

    def invite_curator(self, user):
        username = user.username if isinstance(user, YourUser) or isinstance(user, AnotherUser) else user
        headers = self._headers
        headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.id) + "/curators/"
        )
        requests.put(
            "https://scratch.mit.edu/site-api/users/curators-in/"
            + str(self.id)
            + "/invite_curator/?usernames="
            + username,
            headers=headers,
        )

    def accept_curator(self):
        headers = self._headers
        headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.id) + "/curators/"
        )
        requests.put(
            "https://scratch.mit.edu/site-api/users/curators-in/"
            + str(self.id)
            + "/add/?usernames="
            + self._client.username,
            headers=headers,
        )

    def promote_curator(self, user):
        username = user.username if isinstance(user, YourUser) or isinstance(user, AnotherUser) else user
        headers = self._headers
        headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.id) + "/curators/"
        )
        requests.put(
            "https://scratch.mit.edu/site-api/users/curators-in/"
            + str(self.id)
            + "/promote/?usernames="
            + username,
            headers=headers,
        )

    def set_description(self, content: str):
        data = {"description": content}
        requests.put(
            "https://scratch.mit.edu/site-api/galleries/all/" + str(self.id) + "/",
            headers=self._headers,
            data=json.dumps(data),
        )
        self.description = content

    def set_title(self, content: str):
        data = {"title": content}
        requests.put(
            "https://scratch.mit.edu/site-api/galleries/all/" + str(self.id) + "/",
            headers=self._headers,
            data=json.dumps(data),
        )
        self.title = content
