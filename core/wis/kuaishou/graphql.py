# 快手的数据传输是基于GraphQL实现的
# 这个类负责获取一些GraphQL的schema
from typing import Dict
import os


class KuaiShouGraphQL:
    graphql_queries: Dict[str, str] = {}

    def __init__(self):
        self.graphql_dir = os.path.join(os.path.dirname(__file__), "graphql")
        self.load_graphql_queries()

    def load_graphql_queries(self):
        graphql_files = [
            "search_query.graphql",
            "video_detail.graphql",
            "comment_list.graphql",
            "vision_profile.graphql",
            "vision_profile_photo_list.graphql",
            "vision_profile_user_list.graphql",
            "vision_sub_comment_list.graphql",
            "homefeed_videos.graphql",
        ]

        for file in graphql_files:
            with open(os.path.join(self.graphql_dir, file), mode="r") as f:
                query_name = file.split(".")[0]
                self.graphql_queries[query_name] = f.read()

    def get(self, query_name: str) -> str:
        return self.graphql_queries.get(query_name, "Query not found")
