from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user

bp_search = Blueprint("search", __name__, url_prefix="/search")


@bp_search.route("/param_search", methods=["POST"])
def param_search():
    # title=None, author=None, tags=None, store_id=None
    title = request.json.get("title", "")
    author = request.json.get("author", "")
    tags = request.json.get("tags", "")
    store_id = request.json.get("store_id", "")
    u = user.User()
    code, message = u.params_search(title=title, author=author, tags=tags,  store_id=store_id)
    return jsonify({"message": message}), code


@bp_search.route("/content_search", methods=["POST"])
def content_search():
    sub_content: str = request.json.get("sub_content")
    store_id = request.headers.get("store_id")
    u = user.User()
    code, message = u.whole_content_search(sub_content=sub_content, store_id=store_id)
    return jsonify({"message": message}), code