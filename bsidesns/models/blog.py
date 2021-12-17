import datetime
import re

import ormar
from freenit.config import getConfig
from freenit.models.base import BaseModel
from freenit.models.user import UserModel
from freenit.models.metaclass import AllOptional
from unidecode import unidecode

config = getConfig()

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


class Blog(BaseModel):
    class Meta(config.meta):
        pass

    id: int = ormar.Integer(primary_key=True)
    author: UserModel = ormar.ForeignKey(UserModel)
    content: str = ormar.Text()
    published: bool = ormar.Boolean()
    slug: str = ormar.String(max_length=200, nullable=True)
    title: str = ormar.String(max_length=200)
    date: datetime.date = ormar.DateTime(default=datetime.datetime.now)


@ormar.pre_save(Blog)
async def save(sender, *args, **kwargs):
    blog = kwargs.get("instance")
    if blog.slug is None:
        result = []
        for word in _punct_re.split(blog.title.lower()):
            result.extend(unidecode(word).split())
        blog.slug = "-".join(result)


class BlogOptional(Blog, metaclass=AllOptional):
    pass
