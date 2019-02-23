from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from myblog.forms import CategoryForm,PostForm,LinkForm, SettingForm
from myblog.models import Category,Post,Link,Comment
from flask_login import login_required,current_user
from myblog.extensions import db
from myblog.utils import redirect_back

admin_bp = Blueprint('admin', __name__)


# 视图保护功能：未登录的用户不能访问
@admin_bp.before_request
@login_required
def login_protect():
    pass


# 管理员信息设置
@admin_bp.route('/setting',methods=['GET','POST'])
def settings():
    form=SettingForm()

    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.blog_title=form.blog_title.data
        current_user.blog_sub_title=form.blog_sub_title.data
        current_user.about=form.about.data

        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about

    return render_template('admin/settings.html',form=form)


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
@admin_bp.route('/post/edit/<int:post_id>',methods=['GET','POST'])
def edit_post(post_id):
    """
    编辑文章
    :return:
    """
    post=Post.query.get_or_404(post_id)
    form=PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.category = Category.query.get(form.category.data)
        post.body = form.body.data

        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('blog.show_post',post_id=post_id))

    form.title.data=post.title
    form.category.data=post.category_id
    form.body.data=post.body

    return render_template('admin/edit_post.html',form=form)


@admin_bp.route('/category/edit/<int:category_id>',methods=['GET','POST'])
def edit_category(category_id):
    """
    编辑分类
    :return:
    """
    form=CategoryForm()
    category=Category.query.get_or_404(category_id)

    # 默认分类不可修改
    if category.id == 1:
        flash('You can not edit the default category.', 'warning')
        return redirect(url_for('blog.index'))

    if form.validate_on_submit():
        category.name=form.name.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('.manage_category'))

    form.name.data=category.name
    return render_template('admin/edit_post.html',form=form)


@admin_bp.route('/link/edit/<int:link_id>',methods=['GET','POST'])
def edit_link(link_id):
    """
    编辑外链
    :return:
    """
    form = LinkForm()
    link = Link.query.get_or_404(link_id)

    if form.validate_on_submit():
        link.name = form.name.data
        link.url=form.url.data
        db.session.commit()
        flash('Link updated.', 'success')
        return redirect(url_for('.manage_link'))

    form.name.data = link.name
    form.url.data=link.url
    return render_template('admin/edit_post.html', form=form)


# 删除功能　　####################################

@admin_bp.route('/delete_category/<int:category_id>',methods=['POST'])
def delete_category(category_id):
    """
    删除某条分类，但是该分类下的文章不会被删除，转为Default分类下
    :return:
    """
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('blog.index'))
    category.delete()  # 自定义方法
    flash('Category deleted.', 'success')
    return redirect(url_for('.manage_category'))


@admin_bp.route('/delete_comment/<int:comment_id>',methods=['POST'])
def delete_comment(comment_id):
    """
    删除某条评论
    :return:
    """
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@admin_bp.route('/delete_post/<int:post_id>',methods=['POST'])
def delete_post(post_id):
    """
    删除某篇文章
    :return:
    """
    post=Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    flash('Post deleted.', 'success')
    return redirect_back()


@admin_bp.route('/delete_link/<int:link_id>',methods=['POST'])
def delete_link(link_id):
    """
    删除某条外链
    :return:
    """
    link=Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted.', 'success')
    return redirect(url_for('.manage_link'))


# 修改权限
@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
def set_comment(post_id):
    """
    修改文章能否被评论
    :return:
    """
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/approve_comment', methods=['POST'])
def approve_comment(comment_id):
    """
    修改评论通过审核
    :return:
    """
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('Comment published.', 'success')
    return redirect_back()
