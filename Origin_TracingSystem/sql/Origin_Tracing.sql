-- 创建数据库
CREATE DATABASE `Origin_Tracing` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `Origin_Tracing`;

-- 1. 创建家族分支表
CREATE TABLE `Origin_Tracing_Branches` (
    `branch_id` INT NOT NULL AUTO_INCREMENT COMMENT '分支ID',
    `branch_name` VARCHAR(255) NOT NULL COMMENT '分支名称”',
    `surname` VARCHAR(50) DEFAULT '姜' COMMENT '姓氏',
    `ancestral_home` VARCHAR(255) COMMENT '祖源地”',
    `first_ancestor` VARCHAR(255) COMMENT '得姓始祖或开基祖',
    `historical_summary` TEXT COMMENT '历史摘要',
    `source_reference` VARCHAR(500) COMMENT '资料来源',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    PRIMARY KEY (`branch_id`),
    INDEX `idx_branch_name` (`branch_name`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='姜姓家族分支表';

-- 2. 创建地理地点表
CREATE TABLE `Origin_Tracing_Locations` (
    `location_id` INT NOT NULL AUTO_INCREMENT COMMENT '地点ID',
    `historical_name` VARCHAR(255) NOT NULL COMMENT '历史地名”',
    `modern_name` VARCHAR(255) COMMENT '现代地名”',
    `longitude` DECIMAL(11, 8) COMMENT '经度',
    `latitude` DECIMAL(10, 8) COMMENT '纬度',
    `location_type` ENUM('origin', 'settlement', 'node') DEFAULT 'settlement' COMMENT '地点类型：origin起源地，settlement聚居地，node途经地',
    `admin_region` VARCHAR(255) COMMENT '现代行政区划(省-市-县)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    PRIMARY KEY (`location_id`),
    INDEX `idx_historical_name` (`historical_name`(100)),
    INDEX `idx_coordinates` (`longitude`, `latitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='祖籍地与迁徙地点表';

-- 3. 创建迁徙事件表
CREATE TABLE `Origin_Tracing_Migrations` (
    `migration_id` INT NOT NULL AUTO_INCREMENT COMMENT '迁徙ID',
    `branch_id` INT NOT NULL COMMENT '关联的分支ID',
    `from_location_id` INT NOT NULL COMMENT '迁出地ID',
    `to_location_id` INT NOT NULL COMMENT '迁入地ID',
    `migration_period` VARCHAR(100) COMMENT '迁徙年代',
    `estimated_year` INT COMMENT '估算年份',
    `migration_reason` TEXT COMMENT '迁徙原因',
    `key_figure` VARCHAR(255) COMMENT '关键人物',
    `description` TEXT COMMENT '事件详细描述',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    PRIMARY KEY (`migration_id`),
    FOREIGN KEY (`branch_id`) REFERENCES `Origin_Tracing_Branches`(`branch_id`) ON DELETE CASCADE,
    FOREIGN KEY (`from_location_id`) REFERENCES `Origin_Tracing_Locations`(`location_id`),
    FOREIGN KEY (`to_location_id`) REFERENCES `Origin_Tracing_Locations`(`location_id`),
    INDEX `idx_branch` (`branch_id`),
    INDEX `idx_period` (`migration_period`(50)),
    INDEX `idx_year` (`estimated_year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='姜姓家族迁徙事件表';

-- 4. 创建用户表
CREATE TABLE `Origin_Tracing_Users` (
    `user_id` INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `role` ENUM('user', 'admin') DEFAULT 'user' COMMENT '角色: user-普通用户, admin-管理员',
    `real_name` VARCHAR(50) COMMENT '真实姓名',
    `phone` VARCHAR(20) COMMENT '联系电话',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    `last_login` TIMESTAMP NULL COMMENT '最后登录时间',
    PRIMARY KEY (`user_id`),
    INDEX `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

-- 5. 创建用户提交的迁徙口述史表
CREATE TABLE `Origin_Tracing_Migration_Submissions` (
    `submission_id` INT NOT NULL AUTO_INCREMENT COMMENT '提交ID',
    `user_id` INT NOT NULL COMMENT '提交用户ID',
    `branch_name` VARCHAR(255) NOT NULL COMMENT '分支名称',
    `surname` VARCHAR(50) DEFAULT '姜' COMMENT '姓氏',
    `migration_description` TEXT NOT NULL COMMENT '迁徙口述史描述',
    `migration_period` VARCHAR(100) COMMENT '迁徙年代',
    `estimated_year` INT COMMENT '估算年份',
    `migration_route` TEXT COMMENT '迁徙路线描述（JSON格式）',
    `migration_reason` TEXT COMMENT '迁徙原因',
    `key_figures` TEXT COMMENT '关键人物',
    `source_reference` VARCHAR(500) COMMENT '资料来源',
    `status` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '审核状态：pending待审核，approved已批准，rejected已拒绝',
    `reviewer_id` INT NULL COMMENT '审核员ID',
    `review_comment` TEXT COMMENT '审核意见',
    `submitted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    `reviewed_at` TIMESTAMP NULL COMMENT '审核时间',
    PRIMARY KEY (`submission_id`),
    FOREIGN KEY (`user_id`) REFERENCES `Origin_Tracing_Users`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`reviewer_id`) REFERENCES `Origin_Tracing_Users`(`user_id`) ON DELETE SET NULL,
    INDEX `idx_status` (`status`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_submitted_at` (`submitted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户提交的迁徙口述史表';

-- 6. 创建用户提交的私家族谱摘要表
CREATE TABLE `Origin_Tracing_Family_Tree_Submissions` (
    `submission_id` INT NOT NULL AUTO_INCREMENT COMMENT '提交ID',
    `user_id` INT NOT NULL COMMENT '提交用户ID',
    `branch_name` VARCHAR(255) NOT NULL COMMENT '分支名称',
    `surname` VARCHAR(50) DEFAULT '姜' COMMENT '姓氏',
    `family_tree_summary` TEXT NOT NULL COMMENT '族谱摘要',
    `ancestral_home` VARCHAR(255) COMMENT '祖源地',
    `first_ancestor` VARCHAR(255) COMMENT '始祖信息',
    `generation_info` TEXT COMMENT '世代信息（JSON格式）',
    `key_descendants` TEXT COMMENT '关键后裔',
    `source_reference` VARCHAR(500) COMMENT '资料来源',
    `status` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '审核状态：pending待审核，approved已批准，rejected已拒绝',
    `reviewer_id` INT NULL COMMENT '审核员ID',
    `review_comment` TEXT COMMENT '审核意见',
    `submitted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    `reviewed_at` TIMESTAMP NULL COMMENT '审核时间',
    PRIMARY KEY (`submission_id`),
    FOREIGN KEY (`user_id`) REFERENCES `Origin_Tracing_Users`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`reviewer_id`) REFERENCES `Origin_Tracing_Users`(`user_id`) ON DELETE SET NULL,
    INDEX `idx_status` (`status`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_submitted_at` (`submitted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户提交的私家族谱摘要表';