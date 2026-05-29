from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class OriginTracingBranches(db.Model):
    """家族分支表"""
    __tablename__ = 'branches'

    branch_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    branch_name = db.Column('name', db.String(255), nullable=False)
    surname = db.Column(db.String(50), default='姜')
    ancestral_home = db.Column(db.String(255))
    first_ancestor = db.Column(db.String(255))
    historical_summary = db.Column(db.Text)
    source_reference = db.Column(db.String(500))
    celebrity_info = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    migrations = db.relationship('OriginTracingMigrations', backref='branch', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Branch {self.branch_name}>'


class OriginTracingLocations(db.Model):
    """地理地点表"""
    __tablename__ = 'locations'

    location_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    historical_name = db.Column(db.String(255), nullable=False)
    modern_name = db.Column(db.String(255))
    longitude = db.Column(db.Numeric(11, 8))
    latitude = db.Column(db.Numeric(10, 8))
    location_type = db.Column('type', db.Enum('origin', 'settlement', 'node'), default='settlement')
    admin_region = db.Column(db.String(255))
    population_estimate = db.Column(db.Integer)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    migrations_from = db.relationship('OriginTracingMigrations', foreign_keys='OriginTracingMigrations.from_location_id',
                                      backref='from_location', lazy=True)
    migrations_to = db.relationship('OriginTracingMigrations', foreign_keys='OriginTracingMigrations.to_location_id',
                                    backref='to_location', lazy=True)

    def __repr__(self):
        return f'<Location {self.historical_name}>'


class OriginTracingMigrations(db.Model):
    """迁徙事件表"""
    __tablename__ = 'migrations'

    migration_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='CASCADE'),
                          nullable=False)
    from_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    to_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    migration_period = db.Column('period', db.String(100))
    estimated_year = db.Column(db.Integer)
    reason = db.Column('reason', db.String(255))
    reason_detail = db.Column(db.Text)
    key_figure = db.Column(db.String(255))
    description = db.Column(db.Text)
    route_points = db.Column(db.JSON)
    distance_km = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Migration {self.migration_id}>'


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'

    user_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    role = db.Column(db.Enum('user', 'admin'), default='user')
    real_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class MigrationSubmission(db.Model):
    """用户提交表（合并迁徙口述史和族谱摘要）"""
    __tablename__ = 'submissions'

    submission_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    submission_type = db.Column('type', db.Enum('migration', 'family_tree'), nullable=False)
    branch_name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(50), default='姜')
    content = db.Column(db.Text, nullable=False)
    ancestral_home = db.Column(db.String(255))
    first_ancestor = db.Column(db.String(255))
    period = db.Column(db.String(100))
    estimated_year = db.Column(db.Integer)
    from_location = db.Column(db.String(255))
    to_location = db.Column(db.String(255))
    route_data = db.Column(db.JSON)
    reason = db.Column('reason', db.String(255))
    key_figures = db.Column(db.Text)
    source_reference = db.Column(db.String(500))
    contact_info = db.Column(db.String(255))
    attachments = db.Column(db.JSON)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                            nullable=True)
    review_comment = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='submissions')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_submissions')

    def __repr__(self):
        return f'<Submission {self.branch_name} - {self.submission_type} - {self.status}>'


class PasswordResetRequest(db.Model):
    """密码重置请求表"""
    __tablename__ = 'password_reset_requests'

    request_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                            nullable=True)
    review_comment = db.Column(db.Text)
    new_password = db.Column(db.String(255))
    requested_at = db.Column(db.DateTime, default=datetime.now)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='password_reset_requests')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_password_requests')

    def __repr__(self):
        return f'<PasswordResetRequest {self.user.username} - {self.status}>'


class UserBranchFavorite(db.Model):
    """用户收藏分支表"""
    __tablename__ = 'user_favorites'

    favorite_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='CASCADE'),
                          nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='favorite_branches')
    branch = db.relationship('OriginTracingBranches', backref='favorited_by_users')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'branch_id', name='unique_user_branch'),
    )

    def __repr__(self):
        return f'<UserBranchFavorite user={self.user_id} branch={self.branch_id}>'


class SystemMeta(db.Model):
    """系统元数据表（合并配置、日志、备份信息）"""
    __tablename__ = 'system_meta'

    meta_id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    meta_type = db.Column('type', db.Enum('config', 'log', 'backup'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.JSON)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='system_operations')

    def __repr__(self):
        return f'<SystemMeta {self.meta_type}:{self.key}>'

    @staticmethod
    def get_config(key, default=None):
        """获取配置值"""
        config = SystemMeta.query.filter_by(meta_type='config', key=key).first()
        return config.value if config else default

    @staticmethod
    def set_config(key, value):
        """设置配置值"""
        config = SystemMeta.query.filter_by(meta_type='config', key=key).first()
        if config:
            config.value = value
        else:
            config = SystemMeta(meta_type='config', key=key, value=value)
            db.session.add(config)
        db.session.commit()

    @staticmethod
    def add_log(operation_type, content, user_id=None, ip_address=None):
        """添加操作日志"""
        log = SystemMeta(
            meta_type='log',
            key=operation_type,
            content=content,
            user_id=user_id,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
