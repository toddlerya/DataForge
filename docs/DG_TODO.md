# DG 对接待办事项

## AI 生成的任务规则经人工修改后的派生任务记录回调录入

### 场景

比如 AI 推荐创建了一个 DG 任务 A，用户发现 A 任务的第 5 个字段不合适，在 DG 页面修改了，然后点创建，这时候 DG 新建了一个任务 B，我们需要记录 A-->B 的这种派生关系

### 逻辑

AI 创建的任务，然后用户对这个任务进行了修改，新建了任务，回调一下服务接口。
给我这些信息：

1. parent_task_id, parent_rule_name
2. child_task_id, child_rule_name, new_dg_rule, modified_filed_rule

## 规则数据预览接口需要改造

http://172.17.55.30/genius/get-preview/ 现在是个 form 表单，改成 json/application 请求

## 仅在 DG 新建任务记录同步

DG 创建的任务信息没有统计到这里

## 支持类似 PG、MYSQL 这种库的字段长度 比如 varchar(30)生成的数据符合长度要求
