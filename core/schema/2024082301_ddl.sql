-- tables: bilibili_video、douyin_aweme、kuaishou_video、weibo_note、xhs_note、tieba_note

alter table bilibili_video add column `source_keyword` varchar(255) default '' comment '搜索来源关键字';
alter table douyin_aweme add column `source_keyword` varchar(255) default '' comment '搜索来源关键字';
alter table kuaishou_video add column `source_keyword` varchar(255) default '' comment '搜索来源关键字';
alter table weibo_note add column `source_keyword` varchar(255) default '' comment '搜索来源关键字';
alter table xhs_note add column `source_keyword` varchar(255) default '' comment '搜索来源关键字';
alter table tieba_note add column `source_keyword` varchar(255) default '' comment '搜索来源关键字';

