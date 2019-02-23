from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from myblog.forms import CategoryForm,PostForm,LinkForm
from myblog.models import Category,Post,Link,Comment
from flask_login import login_required
from myblog.extensions import db


admin_bp = Blueprint('admin', __name__)


# 视图保护功能：未登录的用户不能访问
@admin_bp.before_request
@login_required
def login_protect():
    pass


# 新建功能  ################################################
@admin_bp.route('/category/new',methods=['GET','POST'])
def new_category():
    """
    新建分类
    :return:
    """
    form=CategoryForm()
    if form.validate_on_submit():
        name=form.name.data
        category=Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category created.','sucess')
        return redirect(url_for('.manage_category'))  # 重定向到admin.manage_category,注意路径
    return render_template('admin/new_category.html',form=form)


@admin_bp.route('/post/new',methods=['GET','POST'])
def new_post():
    """
    新建文章
    :return:
    """
    form=PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data

        category_id = form.category.data  # 获取分类id
        post = Post(title=title, body=body, category_id=category_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))  # 重定向到文章详情页

    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/link/new',methods=['GET','POST'])
def new_link():
    """
    新建外链
    :return:
    """
    form=LinkForm()
    if form.validate_on_submit():
        name=form.name.data
        url=form.url.data
        link=Link(name=name,url=url)
        db.session.add(link)
        db.session.commit()
        flash('Link created.', 'success')
        return redirect(url_for('.manage_link'))
    return render_template('admin/new_link.html',form=form)


# 管理功能  ##############################################
@admin_bp.route('/post/manage')
def manage_post():
    """
    管理文章
    :return:
    """
    page=request.args.get('page',1,type=int)
    per_page=current_app.config['BLOG_MANAGE_POST_PER_PAGE']
    pagination=Post.query.order_by(Post.timestamp.desc()).paginate(page,per_page=per_page)
    posts =pagination.items
    return render_template('admin/manage_post.html',posts=posts,pagination=pagination,page=page)


@admin_bp.route('/category/manage')
def manage_category():
    """
    管理分类
    :return:
    """
    categories=Category.query.order_by(Category.name).all()

    return render_template('admin/manage_category.html',categories=categories)


@admin_bp.route('/link/manage')
def manage_link():
    """
    管理外链
    :return:
    """
    return render_template('admin/manage_link.html')


@admin_bp.route('/comment/manage')
def manage_comment():
    """
    管理评论
    :return:
    """
    filter_rule = request.args.get('filter', 'all')  # 'all', 'unread', 'admin'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        # 未审核的评论
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        # 管理员评论
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


# 编辑功能 ##########################################
@admin_bp.route('/post/edit')
def edit_post():
    """
    编辑文章
    :return:
    """
    return 'edit post'


@admin_bp.route('/category/edit')
def edit_category():
    """
    编辑分类
    :return:
    """
    return 'edit category'


@admin_bp.route('/link/edit')
def edit_link():
    """
    编辑外链
    :return:
    """
    return 'edit link'


# 删除功能　　####################################

@admin_bp.route('/delete_category/<int:category_id>',methods=['POST'])
def delete_category(category_id):
    """
    删除某条分类，但是该分类下的文章不会被删除，转为Default分类下
    :return:
    """
    return 'delete_category:%d' %category_id


@admin_bp.route('/delete_comment/<int:comment_id>',methods=['POST'])
def delete_comment(comment_id):
    """
    删除某条评论
    :return:
    """
    return 'delete_comment:%d' %comment_id


@admin_bp.route('/delete_post/<int:post_id>',methods=['POST'])
def delete_post(post_id):
    """
    删除某篇文章
    :return:
    """
    return 'delete_post:%d' %post_id


@admin_bp.route('/delete_link/<int:link_id>',methods=['POST'])
def delete_link(link_id):
    """
    删除某篇文章
    :return:
    """
    return 'delete_link:%d' %link_id


# 修改权限
@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
def set_comment(post_id):
    """
    修改文章能否被评论
    :return:
    """
    return "set_comment"


@admin_bp.route('/comment/<int:comment_id>/approve_comment', methods=['POST'])
def approve_comment(comment_id):
    """
    修改评论是否通过审核
    :return:
    """
    return "approve_comment"
