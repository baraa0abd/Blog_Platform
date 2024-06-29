from ninja_extra import NinjaExtraAPI, api_controller, route
from ninja_jwt.authentication import JWTAuth
from .Schema import *
from .models import *
from typing import List
from ninja.security import HttpBearer
from ninja.errors import HttpError
from datetime import datetime, timedelta
import jwt

# Define your secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

class BearerAuth(HttpBearer):
    def authenticate(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            user = Login.objects.get(id=user_id)
            if user:
                return user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Login.DoesNotExist):
            return None

api = NinjaExtraAPI()

@api_controller("/auth", tags=["Auth"])
class AuthAPI:
    @route.post("/login", response={201: LoginSchema, 409: str})
    def create_login(self, request, login: LoginSchema):
        if Login.objects.filter(username=login.username).exists():
            return 409, "User already exists"
        login_instance = Login(**login.dict())
        login_instance.save()
        return 201, login_instance

    @route.post("/signin", response={200: str, 404: str})
    def signin(self, request, signin: SigninSchema):
        users = Login.objects.filter(username=signin.username, password1=signin.password)
        if users.exists():
            user = users.first()
            token = jwt.encode({
                "user_id": user.id,
                "exp": datetime.utcnow() + timedelta(hours=24)  # Token expiry time
            }, SECRET_KEY, algorithm=ALGORITHM)
            return 200, token
        else:
            return 404, "Create an account first"

    @route.post("/logout", response={200: str})
    def logout(self, request):
        # Implement logout logic if needed (e.g., token blacklist)
        return 200, "Logout Successful"

@api_controller("/users", tags=["User"], auth=BearerAuth())
class UserAPI:
    @route.get("/", response=List[UserSchema])
    def get_users(self, request):
        users = Login.objects.all()
        return list(users)

    @route.get("/profile/{username}", response={200: UserPro, 404: str})
    def get_profile(self, request, username: str):
        user = Login.objects.filter(username=username).first()
        if user is not None:
            return 200, UserPro.from_orm(user)
        else:
            return 404, "User not found"

@api_controller("/posts", tags=["Posts"], auth=BearerAuth())
class PostAPI:
    @route.post("/", response={201: PostSchema, 409: str})
    def create_post(self, request, post: PostSchema):
        post_instance = Post(**post.dict())
        post_instance.save()
        return 201, post_instance

    @route.get("/", response=List[PostSchema])
    def get_posts(self, request):
        posts = Post.objects.all()
        return list(posts)

    @route.get("/{post_id}", response={200: PostSchema, 404: str})
    def get_post(self, request, post_id: int):
        post = Post.objects.filter(id=post_id).first()
        if post is not None:
            return 200, post
        else:
            return 404, "Post not found"

    @route.put("/{post_id}", response={200: PostSchema, 404: str})
    def update_post(self, request, post_id: int, data: PostSchema):
        post = Post.objects.filter(id=post_id).first()
        if post:
            for key, value in data.dict().items():
                setattr(post, key, value)
            post.save()
            return 200, post
        return 404, "Post not found"

    @route.delete("/{post_id}", response={200: str, 404: str})
    def delete_post(self, request, post_id: int):
        post = Post.objects.filter(id=post_id).first()
        if post:
            post.delete()
            return 200, "Post deleted successfully"
        return 404, "Post not found"

@api_controller("/comments", tags=["Comments"], auth=BearerAuth())
class CommentAPI:
    @route.post("/posts/{id}/comments", response={201: CommentSchema, 404: str})
    def add_comment(self, request, id: int, comment: CommentSchema):
        post = Post.objects.filter(id=id).first()
        if post is not None:
            comment_instance = Comment(post=post, **comment.dict())
            comment_instance.save()
            return 201, comment_instance
        else:
            return 404, "Post not found"

    @route.get("/posts/{id}/comments", response=List[CommentSchema])
    def get_comments(self, request, id: int):
        comments = Comment.objects.filter(post_id=id)
        return list(comments)

    @route.delete("/comments/{id}", response={200: str, 404: str})
    def delete_comment(self, request, id: int):
        comment = Comment.objects.filter(id=id).first()
        if comment is not None:
            comment.delete()
            return 200, "Comment deleted successfully"
        else:
            return 404, "Comment not found"

@api_controller("/tags", tags=["Tags"], auth=BearerAuth())
class TagAPI:
    @route.get("/", response=List[TagSchema])
    def get_tags(self, request):
        tags = Tag.objects.all()
        return list(tags)

    @route.post("/", response={201: TagSchema, 409: str})
    def create_tag(self, request, tag: TagSchema):
        if Tag.objects.filter(name=tag.name).exists():
            return 409, "Tag already exists"
        tag_instance = Tag(**tag.dict())
        tag_instance.save()
        return 201, tag_instance

@api_controller("/categories", tags=["Categories"], auth=BearerAuth())
class CategoryAPI:
    @route.get("/", response=List[CategorySchema])
    def get_categories(self, request):
        categories = Category.objects.all()
        return list(categories)

    @route.post("/", response={201: CategorySchema, 409: str})
    def create_category(self, request, category: CategorySchema):
        if Category.objects.filter(name=category.name).exists():
            return 409, "Category already exists"
        category_instance = Category(**category.dict())
        category_instance.save()
        return 201, category_instance

@api_controller("/likes", tags=["Likes"], auth=BearerAuth())
class LikeAPI:
    @route.post("/posts/{id}/like", response={200: str, 404: str})
    def like_post(self, request, id: int):
        post = Post.objects.filter(id=id).first()
        if post is not None:
            post.likes += 1
            post.save()
            return 200, "Post liked"
        else:
            return 404, "Post not found"

# Register controllers with the API
api.register_controllers(AuthAPI, UserAPI, PostAPI, CommentAPI, TagAPI, CategoryAPI, LikeAPI)
