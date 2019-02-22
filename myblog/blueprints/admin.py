from flask import Blueprint
from flask import request

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def index():

    return 'admin page'


@admin_bp.route('/new_post')
def new_post():
    """
    新建文章
    :return:
    """
    return 'new_post page'


@admin_bp.route('/delete_comment/<int:comment_id>',methods=['POST'])
def delete_comment(comment_id):
    """
    删除某条评论
    :return:
    """
    return 'delete_comment:%d' %comment_id