from flask import Blueprint
from flask import abort
from flask import current_app
from flask import flash
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from myblog.extensions import db
from myblog.models import Post,Category,Comment
from myblog.forms import CommentForm, AdminCommentForm
from flask_login import current_user
from myblog.utils import redirect_back


blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    """
    首页：文章列表＋外链＋分类列表
    :return:
    """
    page=request.args.get('page',1,type=int)  # 对获取的查询参数进行类型转换，如果报错则返回默认值
    per_page=current_app.config['BLOG_POST_PER_PAGE']
    pagination=Post.query.order_by(Post.timestamp.desc()).paginate(page,per_page=per_page)
    posts=pagination.items

    return render_template('blog/index.html',pagination=pagination,posts=posts)


@blog_bp.route('/about')
def about():
    """
    渲染about页面
    :return:
    """
    return render_template('blog/about.html')


@blog_bp.route('/post/<int:post_id>',methods=['GET','POST'])
def show_post(post_id):
    """
    文章详情页:文章内容＋评论＋评论表单
    :param post_id:
    :return:
    """
    # 获取文章详情
    post = Post.query.get_or_404(post_id)
    # 评论信息
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.desc()).paginate(
        page, per_page)
    comments = pagination.items

    # 验证用户是否登录，
    # 如果登录则将相关数据填入表单
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True  # 直接通过审核
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    # 表单验证通过后写入数据库
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed)

        # 对于评论的回复
        # 试图获取是否为回复：如果是回复，则添加对应的字段
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment  # 为回复建立与评论的关系
            # todo 邮件发送功能
            # send_new_reply_email(replied_comment)

        db.session.add(comment)
        db.session.commit()

        # 如果管理员登录则显示发布成功，如果不是则发送邮件通知管理员
        if current_user.is_authenticated:
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            # todo 邮件发送功能
            # send_new_comment_email(post)

        return redirect(url_for('.show_post', post_id=post_id))

    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog_bp.route('/reply_comment/<int:comment_id>')
def reply_comment(comment_id):
    """
    回复评论：点击回复评论按钮，跳到评论输入表单，带回对应评论的id和作者
    :return:
    """
    comment=Comment.query.get_or_404(comment_id)

    return redirect(url_for('.show_post',post_id=comment.post_id,reply=comment_id,author=comment.author)+"#comment-form")


@blog_bp.route('/category/<int:category_id>',methods=['GET'])
def show_category(category_id):
    """
    分类详情页：该分类下的所有文章列表
    :param post_id:
    :return:
    """
    # todo 有个bug:通过分类详情页看到的文章评论数有误差，显示的是总评论数（包括没有通过管理员审核的评论）
    category=Category.query.get_or_404(category_id)
    page_now=request.args.get('page',1,type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    pagination=Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page_now,per_page=per_page)
    posts=pagination.items

    return render_template('blog/category.html',category=category,pagination=pagination,posts=posts)


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    """
    修改主题
    :param theme_name:
    :return:
    """
    if theme_name not in current_app.config['BLOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())  # 重定向到上一个请求页面
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)  # 将主题名保存在cookie中
    return response