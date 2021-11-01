from typing import List

from freenit.api.router import route

from ..models.blog import Blog


@route("/blogs", tags=["blog"])
class BlogListApi:
    @staticmethod
    async def get() -> List[Blog]:
        return await Blog.objects.all()

    @staticmethod
    async def post(blog: Blog) -> Blog:
        await blog.save()
        return blog
