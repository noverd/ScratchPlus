import requests
import json
from .UserProfiles import YourUserProfile, AnotherUserProfile
from .Project import YourProject, AnotherProject
from bs4 import BeautifulSoup
from .Comments import UserComment
import re


class YourUser:
    def __init__(self, data, client):
        self.id = data["id"]
        self.username = data["username"]
        self.joined_timestamp = data["history"]["joined"]
        self.scratchteam = data["scratchteam"]
        self.profile = YourUserProfile(data["profile"], self)
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
            "referer": f"https://scratch.mit.edu/users/{self.username}/",
        }

    def get_activity_html(self, limit=10):
        r = requests.get(f"https://scratch.mit.edu/messages/ajax/user-activity/?user={self.username}&max={limit}")
        return r.text

    def get_projects(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            projects = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/projects/?limit=40&offset={str(offset)}"
                ).json()

                projects += res
                if len(res) != 40:
                    break
                offset += 40
        else:

            projects = requests.get(
                "https://api.scratch.mit.edu/users/"
                + self.username
                + "/projects/"
                + "?limit="
                + str(limit)
                + "&offset="
                + str(offset)
            ).json(),

        for x, i in enumerate(projects):
            projects[x].update({
                "author": self.username
            })
        return [
            YourProject(i, self._client) if i["author"]["username"] == self._client.username else AnotherProject(i,
                                                                                                                 self._client)
            for i in projects]

    def get_curating(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            studios = []
            while True:
                res = list(
                    requests.get(
                        f"https://api.scratch.mit.edu/users/{self.username}/studios/curate?limit=40&offset={str(offset)}"
                    ).json()
                )

                studios += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            res = list(requests.get(
                "https://api.scratch.mit.edu/users/"
                + self.username
                + "/studios/curate/"
                + "?limit="
                + str(limit)
                + "&offset="
                + str(offset)
            ).json()
                       )

        return [self._client.studio(i, self._client) for i in res]

    def get_favorites(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            projects = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/favorites/?limit=40&offset={str(offset)}"
                ).json()

                projects += res
                if len(res) != 40:
                    break
                offset += 40
            for x, i in enumerate(projects):
                projects[x]["author"] = self.username
            return [
                YourProject(i, self._client) if i["author"]["username"] == self._client.username else AnotherProject(i,
                                                                                                                     self._client)
                for i in projects]

        else:
            projects = list(
                {
                    **requests.get(
                        "https://api.scratch.mit.edu/users/"
                        + self.username
                        + "/favorites/"
                        + "?limit="
                        + str(limit)
                        + "&offset="
                        + str(offset)
                    ).json(),
                    **{
                        "author": self.username
                    }}
            )
            [
                YourProject(i, self._client) if i["author"]["username"] == self._client.username else AnotherProject(i,
                                                                                                                     self._client)
                for i in projects]

    def get_followers(self, all=False, limit=20, offset=0, get_nick=False):
        if all:
            offset = 0
            users = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/followers/?limit=40&offset={str(offset)}"
                ).json()

                users += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            users = list(
                requests.get(
                    "https://api.scratch.mit.edu/users/"
                    + self.username
                    + "/followers/"
                    + "?limit="
                    + str(limit)
                    + "&offset="
                    + str(offset)
                ).json(),
            )

        if get_nicks:
            return [i["username"] for i in users]
        return [
            YourUser(i, self._client) if i["username"] == self._client.username else AnotherUser(i,
                                                                                                 self._client)
            for i in users]

    def get_following(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            users = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/following/?limit=40&offset={str(offset)}"
                ).json()

                users += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            users = list(
                requests.get(
                    "https://api.scratch.mit.edu/users/"
                    + self.username
                    + "/following/"
                    + "?limit="
                    + str(limit)
                    + "&offset="
                    + str(offset)
                ).json(),
            )

        return [
            YourUser(i, self._client) if i["username"] == self._client.username else AnotherUser(i,
                                                                                                 self._client)
            for i in users]

    def get_message_count(self):
        return requests.get(
            f"https://api.scratch.mit.edu/users/{self.username}/messages/count/"
        ).json()["count"]

    def get_comments(self, page=1):
        comments = []
        soup = BeautifulSoup(
            requests.get(f"https://scratch.mit.edu/site-api/comments/user/{self.username}/?page={page}").content,
            "html.parser")
        result = soup.find_all("li", class_="top-level-reply")

        def get_replies(count):
            '''
            Retrieve replies to comment thread.
            '''
            # Extract reply list
            replies = result[count].find("ul", class_="replies")
            if replies.text == "":
                # Detect empty reply chain
                return None
            # Get DOM node containing user data for comment
            user = replies.find_all("div", class_="info")
            # print(user)
            # Initialize array with name "all_replies"
            all_replies = []
                # Iterate through reply list and extract username
            for i in range(len(user)):
                # Get username section. Probably does it like this to save memory.
                username = user[i].find("div", class_="name")
                # Redefine username as the actual username element
                username = username.find("a").text
                # Get post content
                content = user[i].find("div", class_="content").text
                # Trim username newlines
                username = username.strip().replace("\n", "")
                # Trim post content newlines
                content = content.strip().replace("\n", "")
                # Get comment IDs
                search = re.search("data-comment-id=", str(result[i]))
                # Get post position in reply list
                index = search.span()[1]
                data = str(result[i])[index + 1:]
                i = 0
                id = ""
                while data[i] != '"':
                    id += data[i]
                    i += 1
                id = int(id)
                # Get post numbers (I think)
                search = re.search("title=", str(result[i]))
                index = search.span()[1]
                data = str(result[i])[index + 1:]
                i = 0
                comment_time = ""
                while data[i] != '"':
                    comment_time += data[i]
                    i += 1
                reply = {"id": id, "username": username, "comment": content.replace("                   ", ""),
                         "timestamp": comment_time}
                all_replies.append(reply)
            return all_replies

        for i in range(len(result)):
            user = result[i].find("div", class_="comment")
            replies = get_replies(i)
            user = user.find("div", class_="info")
            user = user.find("div", class_="name")
            user = user.find("a")
            user = user.text

            content = result[i].find("div", class_="comment")
            content = content.find("div", class_="info")
            content = content.find("div", class_="content")
            content = content.text.strip()

            search = re.search("data-comment-id=", str(result[i]))
            index = search.span()[1]
            data = str(result[i])[index + 1:]
            i = 0
            id = ""
            while data[i] != '"':
                id += data[i]
                i += 1
            id = int(id)

            search = re.search("title=", str(result[i]))
            index = search.span()[1]
            data = str(result[i])[index + 1:]
            i = 0
            comment_time = ""
            while data[i] != '"':
                comment_time += data[i]
                i += 1
            parent = len(replies) == 0
            comment = {
                "Username": user,
                "Content": content,
                "Time": comment_time,
                "IsReply": parent,
                "Replies": replies,
                "CommentID": id
            }
            comments.append(comment)
        # Return a list of comments
        return map(lambda data: UserComment(data, self._client, self._headers), comments)

    def post_comment(self, content, parent_id="", commentee_id=""):
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/add/",
            headers=self._headers,
            data=json.dumps(data),
        )

    def report(self, field):

        data = {"selected_field": field}
        requests.post(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/report/",
            headers=self._headers,
            data=json.dumps(data),
        )

    def toggle_commenting(self):

        requests.post(
            "https://scratch.mit.edu/site-api/comments/user/"
            + self.username
            + "/toggle-comments/",
            headers=self._headers,
        )

    def follow(self):
        return requests.put(
            "https://scratch.mit.edu/site-api/users/followers/"
            + self.username
            + "/add/?usernames="
            + self._client.username,
            headers=self._headers,
        ).json()

    def unfollow(self):
        return requests.put(
            "https://scratch.mit.edu/site-api/users/followers/"
            + self.username
            + "/remove/?usernames="
            + self._client.username,
            headers=self._headers,
        ).json()


class AnotherUser:
    def __init__(self, data, client):
        self.id = data["id"]
        self.username = data["username"]
        self.joined_timestamp = data["history"]["joined"]
        self.deleted = False
        self.scratchteam = data["scratchteam"]
        try:
            self.scrather = requests.get(
                f"https://isscratcher.9pfs.repl.co/api/{self.username}"
            ).json()["isScratcher"]

        except:
            self.deleted = True
        self.profile = AnotherUserProfile(data["profile"], self)
        self._client = client
        self._headers = {
            "x-csrftoken": self._client.csrf_token,
            "X-Token": self._client.token,
            "x-requested-with": "XMLHttpRequest",
            "Cookie": f"scratchcsrftoken={self._client.csrf_token};scratchlanguage=en;scratchsessionsid={self._client.session_id};",
            "referer": f"https://scratch.mit.edu/users/{self.username}/",
        }

    def get_projects(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            projects = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/projects/?limit=40&offset={str(offset)}"
                ).json()

                projects += res
                if len(res) != 40:
                    break
                offset += 40
        else:

            projects = requests.get(
                "https://api.scratch.mit.edu/users/"
                + self.username
                + "/projects/"
                + "?limit="
                + str(limit)
                + "&offset="
                + str(offset)
            ).json(),

        for x, i in enumerate(projects):
            projects[x].update({
                "author": self.username
            })
        return [
            YourProject(i, self._client) if i["author"]["username"] == self._client.username else AnotherProject(i,
                                                                                                                 self._client)
            for i in projects]

    def get_curating(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            studios = []
            while True:
                res = list(
                    requests.get(
                        f"https://api.scratch.mit.edu/users/{self.username}/studios/curate?limit=40&offset={str(offset)}"
                    ).json()
                )

                studios += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            res = list(requests.get(
                "https://api.scratch.mit.edu/users/"
                + self.username
                + "/studios/curate/"
                + "?limit="
                + str(limit)
                + "&offset="
                + str(offset)
            ).json()
                       )

        return [self._client.studio(i, self._client) for i in res]

    def get_favorites(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            projects = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/favorites/?limit=40&offset={str(offset)}"
                ).json()

                projects += res
                if len(res) != 40:
                    break
                offset += 40
            for x, i in enumerate(projects):
                projects[x]["author"] = self.username
            return [
                YourProject(i, self._client) if i["author"]["username"] == self._client.username else AnotherProject(i,
                                                                                                                     self._client)
                for i in projects]

        else:
            projects = list(
                {
                    **requests.get(
                        "https://api.scratch.mit.edu/users/"
                        + self.username
                        + "/favorites/"
                        + "?limit="
                        + str(limit)
                        + "&offset="
                        + str(offset)
                    ).json(),
                    **{
                        "author": self.username
                    }}
            )
            [
                YourProject(i, self._client) if i["author"]["username"] == self._client.username else AnotherProject(i,
                                                                                                                     self._client)
                for i in projects]

    def get_activity_html(self, limit=10):
        r = requests.get(f"https://scratch.mit.edu/messages/ajax/user-activity/?user={self.username}&max={limit}")
        return r.text

    def get_followers(self, all=False, limit=20, offset=0, get_nicks=False):
        if all:
            offset = 0
            users = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/followers/?limit=40&offset={str(offset)}"
                ).json()

                users += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            users = list(
                requests.get(
                    "https://api.scratch.mit.edu/users/"
                    + self.username
                    + "/followers/"
                    + "?limit="
                    + str(limit)
                    + "&offset="
                    + str(offset)
                ).json(),
            )

        if get_nicks:
            return [i["username"] for i in users]
        return [
            YourUser(i, self._client) if i["username"] == self._client.username else AnotherUser(i,
                                                                                                 self._client)
            for i in users]

    def get_following(self, all=False, limit=20, offset=0):
        if all:
            offset = 0
            users = []
            while True:
                res = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/following/?limit=40&offset={str(offset)}"
                ).json()

                users += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            users = list(
                requests.get(
                    "https://api.scratch.mit.edu/users/"
                    + self.username
                    + "/following/"
                    + "?limit="
                    + str(limit)
                    + "&offset="
                    + str(offset)
                ).json(),
            )

        return [
            YourUser(i, self._client) if i["username"] == self._client.username else AnotherUser(i,
                                                                                                 self._client)
            for i in users]

    def get_message_count(self):
        return requests.get(
            f"https://api.scratch.mit.edu/users/{self.username}/messages/count/"
        ).json()["count"]

    def get_comments(self, page=1):
        comments = []
        soup = BeautifulSoup(
            requests.get(f"https://scratch.mit.edu/site-api/comments/user/{self.username}/?page={page}").content,
            "html.parser")
        result = soup.find_all("li", class_="top-level-reply")

        def get_replies(count):
            '''
            Retrieve replies to comment thread.
            '''
            # Extract reply list
            replies = result[count].find("ul", class_="replies")
            if replies.text == "":
                # Detect empty reply chain
                return None
            # Get DOM node containing user data for comment
            user = replies.find_all("div", class_="info")
            # print(user)
            # Initialize array with name "all_replies"
            all_replies = []
                # Iterate through reply list and extract username
            for i in range(len(user)):
                # Get username section. Probably does it like this to save memory.
                username = user[i].find("div", class_="name")
                # Redefine username as the actual username element
                username = username.find("a").text
                # Get post content
                content = user[i].find("div", class_="content").text
                # Trim username newlines
                username = username.strip().replace("\n", "")
                # Trim post content newlines
                content = content.strip().replace("\n", "")
                # Get comment IDs
                search = re.search("data-comment-id=", str(result[i]))
                # Get post position in reply list
                index = search.span()[1]
                data = str(result[i])[index + 1:]
                i = 0
                id = ""
                while data[i] != '"':
                    id += data[i]
                    i += 1
                id = int(id)
                # Get post numbers (I think)
                search = re.search("title=", str(result[i]))
                index = search.span()[1]
                data = str(result[i])[index + 1:]
                i = 0
                comment_time = ""
                while data[i] != '"':
                    comment_time += data[i]
                    i += 1
                reply = {"id": id, "username": username, "comment": content.replace("                   ", ""),
                         "timestamp": comment_time}
                all_replies.append(reply)
            return all_replies

        for i in range(len(result)):
            user = result[i].find("div", class_="comment")
            replies = get_replies(i)
            user = user.find("div", class_="info")
            user = user.find("div", class_="name")
            user = user.find("a")
            user = user.text

            content = result[i].find("div", class_="comment")
            content = content.find("div", class_="info")
            content = content.find("div", class_="content")
            content = content.text.strip()

            search = re.search("data-comment-id=", str(result[i]))
            index = search.span()[1]
            data = str(result[i])[index + 1:]
            i = 0
            id = ""
            while data[i] != '"':
                id += data[i]
                i += 1
            id = int(id)

            search = re.search("title=", str(result[i]))
            index = search.span()[1]
            data = str(result[i])[index + 1:]
            i = 0
            comment_time = ""
            while data[i] != '"':
                comment_time += data[i]
                i += 1
            parent = len(replies) == 0
            comment = {
                "Username": user,
                "Content": content,
                "Time": comment_time,
                "IsReply": parent,
                "Replies": replies,
                "CommentID": id
            }
            comments.append(comment)
        # Return a list of comments
        return map(lambda data: UserComment(data, self._client, self._headers), comments)

    def post_comment(self, content, parent_id="", commentee_id=""):
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": parent_id,
        }
        requests.post(
            f"https://scratch.mit.edu/site-api/comments/user/{self.username}/add/",
            headers=self._headers,
            data=json.dumps(data),
        )

    def report(self, field):

        data = {"selected_field": field}
        requests.post(
            f"https://scratch.mit.edu/site-api/users/all/{self.username}/report/",
            headers=self._headers,
            data=json.dumps(data),
        )

    def follow(self):
        return requests.put(
            "https://scratch.mit.edu/site-api/users/followers/"
            + self.username
            + "/add/?usernames="
            + self._client.username,
            headers=self._headers,
        ).json()

    def unfollow(self):
        return requests.put(
            "https://scratch.mit.edu/site-api/users/followers/"
            + self.username
            + "/remove/?usernames="
            + self._client.username,
            headers=self._headers,
        ).json()
