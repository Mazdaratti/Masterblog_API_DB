from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.storage.post import Base, Post  # The SQLAlchemy models


class BlogManager:
    """
    BlogManager class to manage blog posts using a database.
    """

    def __init__(self, database_url: str):
        """
        Initialize the BlogManager with a database connection.

        Args:
            database_url (str): Database connection string.
        """
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)  # Ensure the database schema is created
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def get_all_posts(self, sort: str = None, direction: str = 'asc') -> list[dict] | dict:
        """
        Retrieve all posts with optional sorting.

        Args:
            sort (str, optional): Field to sort by. Options are columns of the Post model.
            direction (str): Sort direction ('asc' or 'desc').

        Returns:
            list[Post]: List of posts or error message if validation fails.
        """
        valid_sort_fields = [col.name for col in Post.__table__.columns]
        valid_directions = ['asc', 'desc']

        if sort and sort not in valid_sort_fields:
            return {"error": f"Invalid sort field. Valid options are: {', '.join(valid_sort_fields)}."}
        if direction not in valid_directions:
            return {"error": "Invalid direction. Valid options are 'asc' or 'desc'."}

        query = self.session.query(Post)

        if sort:
            if direction == 'desc':
                query = query.order_by(getattr(Post, sort).desc())
            else:
                query = query.order_by(getattr(Post, sort))

        posts = query.all()
        return [post.Post.to_dict() for post in posts]

    def add_post(self, data: dict) -> dict:
        """
        Add a new post dynamically based on the Post model.

        Args:
            data (dict): Post data.

        Returns:
            dict: The newly created post data.
        """
        new_post_data = {col.name: data[col.name] for col in Post.__table__.columns if col.name in data}
        new_post = Post(**new_post_data)

        self.session.add(new_post)
        self.session.commit()
        return new_post.Post.to_dict()

    def get_post_by_id(self, post_id: int) -> Post | None:
        """
        Retrieve a post by its ID.

        Args:
            post_id (int): ID of the post.

        Returns:
            Post or None: The Post object if found, otherwise None.
        """
        post = self.session.query(Post).get(post_id)
        return post

    def update_post(self, post_id: int, data: dict) -> dict | None:
        """
        Update an existing post.

        Args:
            post_id (int): ID of the post.
            data (dict): Data to update the post with.

        Returns:
            dict or None: Updated post data if successful, otherwise None.
        """
        post = self.get_post_by_id(post_id)  # Use the helper to fetch the post
        if not post:
            return None
        post.Post.update(data)
        self.session.commit()
        return post.Post.to_dict()  # Convert to dictionary for returning to client

    def delete_post(self, post_id: int) -> bool:
        """
        Delete a post by ID.

        Args:
            post_id (int): ID of the post to delete.

        Returns:
            bool: True if deleted, False otherwise.
        """
        post = self.get_post_by_id(post_id)
        if not post:
            return False
        self.session.delete(post)
        self.session.commit()
        return True

    def search_posts(self, query: dict) -> list[dict]:
        """
        Search posts based on query parameters.

        Args:
            query (dict): Search criteria.

        Returns:
            list[dict]: List of matching posts.
        """
        filters = []
        for field, value in query.items():
            filters.append(getattr(Post, field).ilike(f"%{value}%"))
        results = self.session.query(Post).filter(*filters).all()
        return [post.Post.to_dict() for post in results]

    @staticmethod
    def validate_data(data: dict) -> dict | None:
        """
        Validate the data for a new post dynamically based on the Post model.

        Args:
            data (dict): The post data to validate.

        Returns:
            dict or None: A dictionary with error message if invalid, None if valid.
        """
        for column in Post.__table__.columns:
            # Skip auto-generated or optional fields
            if column.primary_key or column.default or column.nullable:
                continue

            # Check for missing required fields
            if column.name not in data or not data[column.name]:
                return {"error": f"{column.name.capitalize()} is required."}

        return None
