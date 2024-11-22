"""
This module defines the SQLAlchemy model for the blog application.

It includes the `Post` class, which represents a blog post, with fields for:
- `id`: The primary key, automatically incremented.
- `title`: The title of the post, a non-nullable string.
- `content`: The content of the post, a non-nullable string.
- `author`: The author's name, a non-nullable string.
- `created`: The date the post was created, defaults to the current date.
- `updated`: The date the post was last updated, nullable.

The `Post` class includes methods for converting a post to a dictionary and
updating post data dynamically.
"""
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

Base = declarative_base()


class Post(Base):
    """
    SQLAlchemy model for blog posts.
    """

    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author = Column(String, nullable=False)
    created = Column(Date, default=date.today, nullable=False)
    updated = Column(Date, nullable=True)

    def to_dict(self):
        """
        Convert the Post object to a dictionary dynamically.
        Handles all columns in the model.
        Dates are converted to the ISO-format.

        Returns:
            dict: Dictionary representation of the post, with ISO 8601 date format for dates.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert dates to ISO format
            if isinstance(value, date):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    def update(self, data: dict):
        """
        Update the post with new data dynamically.
        Only updates columns that exist in the model.
        The updated timestamp is automatically set to the current date.

        Args:
            data (dict): Data to update the post with.
        """
        for column in self.__table__.columns:
            if column.name in data:
                setattr(self, column.name, data[column.name])
        self.updated = date.today()
