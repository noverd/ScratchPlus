import requests
import json

from .Comments import ProjectComment


class AnotherProject:
    def __init__(self, data, client):
        self.id = data["id"]
        self.title = data["title"]
        self.description = data["description"]
        self.instructions = data["instructions"]
        self.visible = data["visibility"] == "visible"
        self.public = data["public"]
        self.comments_allowed = data["comments_allowed"]
        self.is_published = data["is_published"]
        self.author = (data["author"])
        self.thumbnail_URL = data["image"]

        self.created_timestamp = data["history"]["created"]
        self.last_modified_timestamp = data["history"]["modified"]
        self.shared_timestamp = data["history"]["shared"]

        self.view_count = data["stats"]["views"]
        self.love_count = data["stats"]["loves"]
        self.favorite_count = data["stats"]["favorites"]
        self.remix_count = data["stats"]["remixes"]

        self.parent = data["remix"].get("parent")
        self.root = data["remix"]["root"]
        self.is_remix = bool(self.parent)

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
            "referer": f"https://scratch.mit.edu/projects/{str(self.id)}/",
        }

        self._json_headers = {
            "x-csrftoken": self._client.csrf_token,
            "X-Token": self._client.token,
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchcsrftoken="
            + self._client.csrf_token
            + ";scratchlanguage=en;scratchsessionsid="
            + self._client.session_id
            + ";",
            "referer": f"https://scratch.mit.edu/projects/{str(self.id)}/",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_comment(self, comment_id):
        data = requests.get(
            "https://api.scratch.mit.edu/users/"
            + self.author.username
            + "/projects/"
            + str(self.id)
            + "/comments/"
            + str(comment_id)
            + "/"
        ).json()
        return ProjectComment(self, data, self._client)

    def love(self):
        return requests.post(
            "https://api.scratch.mit.edu/proxy/projects/"
            + str(self.id)
            + "/loves/user/"
            + self._client.username,
            headers=self._headers,
        ).json()["userLove"]

    def unlove(self):
        return requests.delete(
            "https://api.scratch.mit.edu/proxy/projects/"
            + str(self.id)
            + "/loves/user/"
            + self._client.username,
            headers=self._headers,
        ).json()["userLove"]

    def favorite(self):
        return requests.post(
            "https://api.scratch.mit.edu/proxy/projects/"
            + str(self.id)
            + "/favorites/user/"
            + self._client.username,
            headers=self._headers,
        ).json()["userFavorite"]

    def unfavorite(self):
        return requests.delete(
            "https://api.scratch.mit.edu/proxy/projects/"
            + str(self.id)
            + "/favorites/user/"
            + self._client.username,
            headers=self._headers,
        ).json()["userFavorite"]

    def get_scripts(self):
        return requests.get(f"https://projects.scratch.mit.edu/{str(self.id)}/").json()

    def get_remixes(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            projects = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/projects/{str(self.id)}/remixes/?limit=40&offset={str(offset)}"
                ).json()

                projects += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            projects = requests.get(
                "https://api.scratch.mit.edu/projects/"
                + str(self.id)
                + "/remixes/"
                + "?limit="
                + str(limit)
                + "&offset="
                + str(offset)
            ).json()

        return [
            YourProject(i, self._client) if i["author"]["username"] == self._client.username else AnotherProject(i,
                                                                                                                 self._client)
            for i in projects]

    def get_studios(self, all=False, limit=20, offset=0):
        if not all:
            return list(
                map(
                    self._client.studio,
                    requests.get(
                        f"https://api.scratch.mit.edu/projects/{str(self.id)}/studios/?limit={str(limit)}&offset={str(offset)}"
                    ).json(),
                )
            )

        offset = 0
        studios = []
        while True:
            res = requests.get(
                f"https://api.scratch.mit.edu/projects/{str(self.id)}/studios/?limit=40&offset={str(offset)}"
            ).json()

            studios += res
            if len(res) != 40:
                break
            offset += 40
        return []

    def post_comment(self, content, parent_id="", commentee_id=""):
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/project/{str(self.id)}/",
            headers=self._json_headers,
            data=json.dumps(data),
        ).json()

    def get_comments(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            comments = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.author.username}/projects/{str(self.id)}/comments/?limit=40&offset={str(offset)}"
                ).json()

                comments += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            comments = requests.get(
                        "https://api.scratch.mit.edu/users/"
                        + self.author.username
                        + "/projects/"
                        + str(self.id)
                        + "/comments/"
                        + "?limit="
                        + str(limit)
                        + "&offset="
                        + str(offset)
                    ).json()

        return [ProjectComment(self, i, self._client) for i in comments]
    def report(self, category, reason, image=None):
        if not image:
            image = self.thumbnail_URL
        data = {"notes": reason, "report_category": category, "thumbnail": image}
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/project/{str(self.id)}/",
            data=json.dumps(data),
            headers=self._json_headers,
        ).text

    def view(self):
        requests.post(
            "https://api.scratch.mit.edu/users/"
            + self.author.username
            + "/projects/"
            + str(self.id)
            + "/views/",
            headers=self._headers,
        )


class YourProject:
    def __init__(self, data, client):
        self.id = data["id"]
        self.title = data["title"]
        self.description = data["description"]
        self.instructions = data["instructions"]
        self.visible = data["visibility"] == "visible"
        self.public = data["public"]
        self.comments_allowed = data["comments_allowed"]
        self.is_published = data["is_published"]
        self.author = data["author"]
        self.thumbnail_URL = data["image"]

        self.created_timestamp = data["history"]["created"]
        self.last_modified_timestamp = data["history"]["modified"]
        self.shared_timestamp = data["history"]["shared"]

        self.view_count = data["stats"]["views"]
        self.love_count = data["stats"]["loves"]
        self.favorite_count = data["stats"]["favorites"]
        self.remix_count = data["stats"]["remixes"]

        self.parent = data["remix"].get("parent")
        self.root = data["remix"]["root"]
        self.is_remix = bool(self.parent)

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
            "referer": f"https://scratch.mit.edu/projects/{str(self.id)}/",
        }

        self._json_headers = {
            "x-csrftoken": self._client.csrf_token,
            "X-Token": self._client.token,
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchcsrftoken="
            + self._client.csrf_token
            + ";scratchlanguage=en;scratchsessionsid="
            + self._client.session_id
            + ";",
            "referer": f"https://scratch.mit.edu/projects/{str(self.id)}/",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_comment(self, comment_id):
        data = requests.get(
            "https://api.scratch.mit.edu/users/"
            + self.author.username
            + "/projects/"
            + str(self.id)
            + "/comments/"
            + str(comment_id)
            + "/"
        ).json()
        return ProjectComment(self, data, self._client)

    def love(self):
        return requests.post(
            "https://api.scratch.mit.edu/proxy/projects/"
            + str(self.id)
            + "/loves/user/"
            + self._client.username,
            headers=self._headers,
        ).json()["userLove"]

    def unlove(self):
        return requests.delete(
            "https://api.scratch.mit.edu/proxy/projects/"
            + str(self.id)
            + "/loves/user/"
            + self._client.username,
            headers=self._headers,
        ).json()["userLove"]

    def favorite(self):
        return requests.post(
            "https://api.scratch.mit.edu/proxy/projects/"
            + str(self.id)
            + "/favorites/user/"
            + self._client.username,
            headers=self._headers,
        ).json()["userFavorite"]

    def unfavorite(self):
        return requests.delete(
            "https://api.scratch.mit.edu/proxy/projects/"
            + str(self.id)
            + "/favorites/user/"
            + self._client.username,
            headers=self._headers,
        ).json()["userFavorite"]

    def get_scripts(self):
        return requests.get(f"https://projects.scratch.mit.edu/{str(self.id)}/").json()

    def get_remixes(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            projects = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/projects/{str(self.id)}/remixes/?limit=40&offset={str(offset)}"
                ).json()

                projects += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            projects = requests.get(
                "https://api.scratch.mit.edu/projects/"
                + str(self.id)
                + "/remixes/"
                + "?limit="
                + str(limit)
                + "&offset="
                + str(offset)
            ).json()

        return [
            YourProject(i, self._client) if i["author"]["username"] == self._client.username else AnotherProject(i,
                                                                                                                 self._client)
            for i in projects]

    def get_studios(self, all=False, limit=20, offset=0):
        if not all:
            return list(
                map(
                    self._client.studio,
                    requests.get(
                        f"https://api.scratch.mit.edu/projects/{str(self.id)}/studios/?limit={str(limit)}&offset={str(offset)}"
                    ).json(),
                )
            )

        offset = 0
        studios = []
        while True:
            res = requests.get(
                f"https://api.scratch.mit.edu/projects/{str(self.id)}/studios/?limit=40&offset={str(offset)}"
            ).json()

            studios += res
            if len(res) != 40:
                break
            offset += 40
        return list(map(self._client.studio, studios))

    def post_comment(self, content, parent_id="", commentee_id=""):
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/project/{str(self.id)}/",
            headers=self._json_headers,
            data=json.dumps(data),
        ).json()

    def get_comments(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            comments = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.author.username}/projects/{str(self.id)}/comments/?limit=40&offset={str(offset)}"
                ).json()

                comments += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            comments = requests.get(
                        "https://api.scratch.mit.edu/users/"
                        + self.author.username
                        + "/projects/"
                        + str(self.id)
                        + "/comments/"
                        + "?limit="
                        + str(limit)
                        + "&offset="
                        + str(offset)
                    ).json()

        return [ProjectComment(self, i, self._client) for i in comments]

    def toggle_commenting(self):
        data = {"comments_allowed": not self.comments_allowed}
        self.comments_allowed = not self.comments_allowed
        return self._client._to_project(
            requests.put(
                f"https://api.scratch.mit.edu/projects/{str(self.id)}/",
                data=json.dumps(data),
                headers=self._json_headers,
            ).json()
        )

    def turn_on_commenting(self):
        data = {"comments_allowed": True}
        self.comments_allowed = True
        return self._client._to_project(
            requests.put(
                f"https://api.scratch.mit.edu/projects/{str(self.id)}/",
                data=json.dumps(data),
                headers=self._json_headers,
            ).json()
        )

    def turn_off_commenting(self):
        data = {"comments_allowed": False}
        self.comments_allowed = False
        return self._client._to_project(
            requests.put(
                f"https://api.scratch.mit.edu/projects/{str(self.id)}/",
                data=json.dumps(data),
                headers=self._json_headers,
            ).json()
        )

    def report(self, category, reason, image=None):
        if not image:
            image = self.thumbnail_URL
        data = {"notes": reason, "report_category": category, "thumbnail": image}
        return requests.post(
            f"https://api.scratch.mit.edu/proxy/comments/project/{str(self.id)}/",
            data=json.dumps(data),
            headers=self._json_headers,
        ).text

    def unshare(self):

        requests.put(
            f"https://api.scratch.mit.edu/proxy/projects/{str(self.id)}/unshare/",
            headers=self._json_headers,
        )

    def share(self):
        requests.put(
            f"https://api.scratch.mit.edu/proxy/projects/{str(self.id)}/share/",
            headers=self._json_headers,
        )

    def view(self):
        requests.post(
            "https://api.scratch.mit.edu/users/"
            + self.author.username
            + "/projects/"
            + str(self.id)
            + "/views/",
            headers=self._headers,
        )

    def set_thumbnail(self, file):
        image = open(file, "rb")
        requests.post(
            "https://scratch.mit.edu/internalapi/project/thumbnail/"
            + str(self.id)
            + "/set/",
            data=image.read(),
            headers=self._headers,
        )

    def set_title(self, title):
        data = {"title": title}
        requests.put(
            "https://api.scratch.mit.edu/projects/"
            + str(self.id),
            data=json.dumps(data),
            headers=self._json_headers,
        )
