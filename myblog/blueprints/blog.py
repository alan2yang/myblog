from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from myblog.models import Post,Category,Comment
from myblog.forms import CommentForm, AdminCommentForm
from flask_login import current_user


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
    # page = request.args.get('page', 1, type=int)
    # per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    # pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(
    #     page, per_page)
    # comments = pagination.items

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

    # 表单验证
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, post=post, reviewed=reviewed)

        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()

        if current_user.is_authenticated:  # send message based on authentication status
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            send_new_comment_email(post)  # send notification email to admin

        return redirect(url_for('.show_post', post_id=post_id))

    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)



@blog_bp.route('/category/<int:category_id>',methods=['GET'])
def show_category(category_id):
    """
    分类详情页：该分类下的所有文章列表
    :param post_id:
    :return:
    """
    return "category detail:%d" % category_id
    # return render_template('blog/category.html')


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    """
    修改主题
    :param theme_name:
    :return:
    """
    pass