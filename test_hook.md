# 自动推送hook测试文件

此文件用于测试Git post-commit hook功能。

**创建时间**: 2026-02-26 21:16

**目的**: 验证提交后自动推送到GitHub功能是否正常工作。

**功能说明**:
1. 每次执行 `git commit` 后，会自动运行 `.git/hooks/post-commit.ps1` 脚本
2. 脚本会尝试将最新提交推送到远程GitHub仓库
3. 推送成功会有成功提示，失败会有错误提示

**禁用方法**:
- 重命名或删除 `.git/hooks/post-commit.ps1` 文件
- 或直接删除此文件: `rm .git\hooks\post-commit.ps1`

**手动推送**: 如果需要手动推送，可运行 `git push origin master`