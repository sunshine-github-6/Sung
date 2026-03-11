from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class OriginTracingBranches(db.Model):
    """家族分支表"""
    __tablename__ = 'Origin_Tracing_Branches'

    branch_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='分支ID')
    branch_name = db.Column(db.String(255), nullable=False, comment='分支名称')
    surname = db.Column(db.String(50), comment='姓氏')
    ancestral_home = db.Column(db.String(255), comment='祖源地')
    first_ancestor = db.Column(db.String(255), comment='得姓始祖或开基祖')
    historical_summary = db.Column(db.Text, comment='历史摘要')
    source_reference = db.Column(db.String(500), comment='资料来源')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='记录创建时间')

    # 关系定义
    migrations = db.relationship('OriginTracingMigrations', backref='branch', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Branch {self.branch_name}>'


class OriginTracingLocations(db.Model):
    """地理地点表"""
    __tablename__ = 'Origin_Tracing_Locations'

    location_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='地点ID')
    historical_name = db.Column(db.String(255), nullable=False, comment='历史地名')
    modern_name = db.Column(db.String(255), comment='现代地名')
    longitude = db.Column(db.Numeric(11, 8), comment='经度')
    latitude = db.Column(db.Numeric(10, 8), comment='纬度')
    location_type = db.Column(db.Enum('origin', 'settlement', 'node'), default='settlement', comment='地点类型')
    admin_region = db.Column(db.String(255), comment='现代行政区划')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='记录创建时间')

    # 关系定义
    migrations_from = db.relationship('OriginTracingMigrations',
                                      foreign_keys='OriginTracingMigrations.from_location_id', backref='from_location',
                                      lazy=True)
    migrations_to = db.relationship('OriginTracingMigrations', foreign_keys='OriginTracingMigrations.to_location_id',
                                    backref='to_location', lazy=True)

    def __repr__(self):
        return f'<Location {self.historical_name}>'


class OriginTracingMigrations(db.Model):
    """迁徙事件表"""
    __tablename__ = 'Origin_Tracing_Migrations'

    migration_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='迁徙ID')
    branch_id = db.Column(db.Integer, db.ForeignKey('Origin_Tracing_Branches.branch_id', ondelete='CASCADE'),
                          nullable=False, comment='关联的分支ID')
    from_location_id = db.Column(db.Integer, db.ForeignKey('Origin_Tracing_Locations.location_id'), nullable=False,
                                 comment='迁出地ID')
    to_location_id = db.Column(db.Integer, db.ForeignKey('Origin_Tracing_Locations.location_id'), nullable=False,
                               comment='迁入地ID')
    migration_period = db.Column(db.String(100), comment='迁徙年代')
    estimated_year = db.Column(db.Integer, comment='估算年份')
    migration_reason = db.Column(db.Text, comment='迁徙原因')
    key_figure = db.Column(db.String(255), comment='关键人物')
    description = db.Column(db.Text, comment='事件详细描述')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='记录创建时间')


class User(db.Model):
    """用户表"""
    __tablename__ = 'Origin_Tracing_Users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    role = db.Column(db.Enum('user', 'admin'), default='user', comment='角色: user-普通用户, admin-管理员')
    real_name = db.Column(db.String(50), comment='真实姓名')
    phone = db.Column(db.String(20), comment='联系电话')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='注册时间')
    last_login = db.Column(db.DateTime, comment='最后登录时间')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class MigrationSubmission(db.Model):
    """用户提交的迁徙口述史表"""
    __tablename__ = 'Origin_Tracing_Migration_Submissions'

    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='提交ID')
    user_id = db.Column(db.Integer, db.ForeignKey('Origin_Tracing_Users.user_id', ondelete='CASCADE'),
                        nullable=False, comment='提交用户ID')
    branch_name = db.Column(db.String(255), nullable=False, comment='分支名称')
    surname = db.Column(db.String(50), default='姜', comment='姓氏')
    migration_description = db.Column(db.Text, nullable=False, comment='迁徙口述史描述')
    migration_period = db.Column(db.String(100), comment='迁徙年代')
    estimated_year = db.Column(db.Integer, comment='估算年份')
    migration_route = db.Column(db.Text, comment='迁徙路线描述（JSON格式）')
    migration_reason = db.Column(db.Text, comment='迁徙原因')
    key_figures = db.Column(db.Text, comment='关键人物')
    source_reference = db.Column(db.String(500), comment='资料来源')
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending',
                       comment='审核状态：pending待审核，approved已批准，rejected已拒绝')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('Origin_Tracing_Users.user_id', ondelete='SET NULL'),
                            nullable=True, comment='审核员ID')
    review_comment = db.Column(db.Text, comment='审核意见')
    submitted_at = db.Column(db.DateTime, default=datetime.now, comment='提交时间')
    reviewed_at = db.Column(db.DateTime, nullable=True, comment='审核时间')

    # 关系定义
    user = db.relationship('User', foreign_keys=[user_id], backref='migration_submissions')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_migration_submissions')

    def __repr__(self):
        return f'<MigrationSubmission {self.branch_name} - {self.status}>'


class FamilyTreeSubmission(db.Model):
    """用户提交的私家族谱摘要表"""
    __tablename__ = 'Origin_Tracing_Family_Tree_Submissions'

    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='提交ID')
    user_id = db.Column(db.Integer, db.ForeignKey('Origin_Tracing_Users.user_id', ondelete='CASCADE'),
                        nullable=False, comment='提交用户ID')
    branch_name = db.Column(db.String(255), nullable=False, comment='分支名称')
    surname = db.Column(db.String(50), default='姜', comment='姓氏')
    family_tree_summary = db.Column(db.Text, nullable=False, comment='族谱摘要')
    ancestral_home = db.Column(db.String(255), comment='祖源地')
    first_ancestor = db.Column(db.String(255), comment='始祖信息')
    generation_info = db.Column(db.Text, comment='世代信息（JSON格式）')
    key_descendants = db.Column(db.Text, comment='关键后裔')
    source_reference = db.Column(db.String(500), comment='资料来源')
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending',
                       comment='审核状态：pending待审核，approved已批准，rejected已拒绝')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('Origin_Tracing_Users.user_id', ondelete='SET NULL'),
                            nullable=True, comment='审核员ID')
    review_comment = db.Column(db.Text, comment='审核意见')
    submitted_at = db.Column(db.DateTime, default=datetime.now, comment='提交时间')
    reviewed_at = db.Column(db.DateTime, nullable=True, comment='审核时间')

    # 关系定义
    user = db.relationship('User', foreign_keys=[user_id], backref='family_tree_submissions')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_family_tree_submissions')

    def __repr__(self):
        return f'<FamilyTreeSubmission {self.branch_name} - {self.status}>'