import requests
import json


class UserComment:
    def __init__(self, json_data, _client, _headers):
        self.author = json_data["Username"]
        self._client = _client
        self._headers = _headers
        self.content = json_data["Content"]
        self.post_time = json_data["Time"]
        self.is_reply = json_data["IsReply"]
        self.id = json_data["CommentID"]
        self.replies = [UserComment(i, self._client, self._headers) for i in json_data["Replies"]]

    def get_user(self):
        return self._client.get_user(self.author)
    def reply(self, content, commentee_id=""):
        data = {
            "commentee_id": commentee_id,
            "content": content,
            "parent_id": self.id,
        }
        requests.post(
            "https://scratch.mit.edu/site-api/comments/user/" + self.author + "/add/",
            headers=self._headers,
            data=json.dumps(data),
        )


class ProjectComment:
    def __init__(self, project, data, client):
        self.id = data["id"]
        self.parent_id = data["parent_id"]
        self.commentee_id = data["commentee_id"]
        self.content = data["content"]
        self.reply_count = data["reply_count"]

        self.author = data["author"]["username"]
        self.author_id = data["author"]["id"]

        self.created_timestamp = data["datetime_created"]
        self.last_modified_timestamp = data["datetime_modified"]

        self.visible = data["visibility"] == "visible"

        self.project = project
        self._client = client

    def delete(self):
        requests.delete(
            "https://api.scratch.mit.edu/proxy/comments/project/"
            + str(self.project.id)
            + "/comment/"
            + str(self.id),
            headers=self.project._headers,
        )

    def report(self):
        requests.post(
            "https://api.scratch.mit.edu/proxy/comments/project/"
            + str(self.project.id)
            + "/comment/"
            + str(self.id)
            + "/report",
            headers=self.project._headers,
        )

    def reply(self, content):
        self.project.post_comment(content, self.id, self.author_id)

    def get_user(self):
        return self._client.get_user(self.author)
