alter table bilibili_video_comment add column `like_count` int NOT NULL DEFAULT '0' COMMENT '点赞数';
alter table douyin_aweme_comment add column `like_count` int NOT NULL DEFAULT '0' COMMENT '点赞数';
alter table kuaishou_video_comment add column `like_count` int NOT NULL DEFAULT '0' COMMENT '点赞数';
alter table weibo_note_comment add column `like_count` int NOT NULL DEFAULT '0' COMMENT '点赞数';
alter table xhs_note_comment add column `like_count` int NOT NULL DEFAULT '0' COMMENT '点赞数';