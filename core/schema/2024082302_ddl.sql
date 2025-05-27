-- ----------------------------
-- Table structure for weibo_creator
-- ----------------------------
DROP TABLE IF EXISTS `weibo_creator`;
CREATE TABLE `weibo_creator`
(
    `id`             int         NOT NULL AUTO_INCREMENT COMMENT '自增ID',
    `user_id`        varchar(64) NOT NULL COMMENT '用户ID',
    `nickname`       varchar(64)  DEFAULT NULL COMMENT '用户昵称',
    `avatar`         varchar(255) DEFAULT NULL COMMENT '用户头像地址',
    `ip_location`    varchar(255) DEFAULT NULL COMMENT '评论时的IP地址',
    `add_ts`         bigint      NOT NULL COMMENT '记录添加时间戳',
    `last_modify_ts` bigint      NOT NULL COMMENT '记录最后修改时间戳',
    `desc`           longtext COMMENT '用户描述',
    `gender`         varchar(1)   DEFAULT NULL COMMENT '性别',
    `follows`        varchar(16)  DEFAULT NULL COMMENT '关注数',
    `fans`           varchar(16)  DEFAULT NULL COMMENT '粉丝数',
    `tag_list`       longtext COMMENT '标签列表',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='微博博主';
