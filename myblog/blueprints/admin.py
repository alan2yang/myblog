from flask import Blueprint
from flask import request

admin_bp = Blueprint('admin', __name__)


# 新建功能
@admin_bp.route('/new_category')
def new_category():
    """
    新建分类
    :return:
    """

    return 'new_category page'


@admin_bp.route('/new_post')
def new_post():
    """
    新建文章
    :return:
    """
    return 'new_post page'


@admin_bp.route('/new_link')
def new_link():
    """
    新建外链
    :return:
    """
    return 'new_link'


# 管理功能
@admin_bp.route('/manage_post')
def manage_post():
    """
    管理文章
    :return:
    """
    return 'new_link'


@admin_bp.route('/manage_category')
def manage_category():
    """
    管理分类
    :return:
    """
    return 'new_link'


@admin_bp.route('/manage_link')
def manage_link():
    """
    管理外链
    :return:
    """
    return 'new_link'


@admin_bp.route('/manage_comment')
def manage_comment():
    """
    管理评论
    :return:
    """
    return 'new_link'


@admin_bp.route('/delete_comment/<int:comment_id>',methods=['POST'])
def delete_comment(comment_id):
    """
    删除某条评论
    :return:
    """
    return 'delete_comment:%d' %comment_id