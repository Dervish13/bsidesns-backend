from typing import List

from fastapi import Depends, HTTPException
from freenit.api.router import route
from freenit.auth import current_user
from freenit.config import getConfig
from ormar import exceptions

from ..models.blog import Blog, BlogOptional

config = getConfig()
User = config.get_user()


@route("/blogs", tags=["blog"], many=True)
class BlogListApi:
    @staticmethod
    async def get() -> List[Blog]:
        return await Blog.objects.all()

    @staticmethod
    async def post(blog: Blog, user: User = Depends(current_user.active_verified)) -> Blog:
        await blog.save()
        return blog


@route("/blogs/{id}", tags=["blog"])
class BlogDetailAPI:
    @staticmethod
    async def get(id: int) -> Blog:
        try:
            blog = await Blog.objects.get(pk=id)
        except exceptions.NoMatch:
            raise HTTPException(status_code=404, detail="No such blog")
        return blog

    @staticmethod
    async def patch(
        id: int,
        blog_data: BlogOptional,
        user: User = Depends(current_user.active_verified),
    ) -> Blog:
        try:
            blog = await Blog.objects.get(pk=id)
            await blog.patch(blog_data)
        except exceptions.NoMatch:
            raise HTTPException(status_code=404, detail="No such blog")
        return blog

    @staticmethod
    async def delete(
        id: int, user: User = Depends(current_user.active_verified)
    ) -> Blog:
        try:
            blog = await Blog.objects.get(pk=id)
        except exceptions.NoMatch:
            raise HTTPException(status_code=404, detail="No such blog")
        await blog.delete()
        return blog
