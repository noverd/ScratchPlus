

class ForumTopic:
    def __init__(self, data, client):
        self.id = data["id"]
        self.title = data["title"]
        self.category = data["category"]
        self.closed = bool(data["closed"])
        self.deleted = bool(data["deleted"])
        self.first_checked = data["time"]["first_checked"]
        self.last_checked = data["time"]["last_checked"]
        self.post_count = data["post_count"]
        self._client = client

    def get_posts_list(self, page: int = 0, order: str = "newest"):
        """
        :param page: Each page has 50 posts, default is page 0
        :param order: Order to sort posts by, defaults to "newest", possible options include "oldest"
        :return: Return list of ForumPost from this forum
        """
        return self._client.get_posts_list(self.id, page, order)


class ForumPost:
    def __init__(self, data, client):
        self._client = client
        self.id = data["id"]
        self.creator = data["username"]
        self.editor = data["editor"]
        self.deleted = bool(data["deleted"])
        self.posted_time = data["time"]["posted"]
        self.first_checked = data["time"]["first_checked"]
        self.html_last_checked = data["time"]["html_last_checked"]
        self.bbcode_last_checked = data["time"]["posted"]
        self.edited_time = data["time"]["posted"]
        self.bbcode_content = data["content"]["bb"]
        self.html_content = data["content"]["html"]
        self.topic_id = data["topic"]["id"]
        self.topic_title = data["topic"]["title"]
        self.topic_category = data["topic"]["category"]
        self.topic_closed = bool(data["topic"]["closed"])
        self.topic_deleted = bool(data["topic"]["deleted"])
        self.topic_first_checked = data["topic"]["time"]["first_checked"]
        self.topic_last_checked = data["topic"]["time"]["last_checked"]

    def get_topic(self):
        self._client.get_topic(self.topic_id)
