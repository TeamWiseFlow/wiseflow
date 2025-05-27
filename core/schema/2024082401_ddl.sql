DROP TABLE IF EXISTS `tieba_creator`;
CREATE TABLE `tieba_creator`
(
    `id`                    int         NOT NULL AUTO_INCREMENT COMMENT '自增ID',
    `user_id`               varchar(64) NOT NULL COMMENT '用户ID',
    `user_name`             varchar(64) NOT NULL COMMENT '用户名',
    `nickname`              varchar(64)  DEFAULT NULL COMMENT '用户昵称',
    `avatar`                varchar(255) DEFAULT NULL COMMENT '用户头像地址',
    `ip_location`           varchar(255) DEFAULT NULL COMMENT '评论时的IP地址',
    `add_ts`                bigint      NOT NULL COMMENT '记录添加时间戳',
    `last_modify_ts`        bigint      NOT NULL COMMENT '记录最后修改时间戳',
    `gender`                varchar(2)   DEFAULT NULL COMMENT '性别',
    `follows`               varchar(16)  DEFAULT NULL COMMENT '关注数',
    `fans`                  varchar(16)  DEFAULT NULL COMMENT '粉丝数',
    `registration_duration` varchar(16)  DEFAULT NULL COMMENT '吧龄',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='贴吧创作者';