# GitHub 协作仓库设置

当前本地仓库路径：`D:\softwareCup`

## 创建远程仓库

在 GitHub 页面创建仓库：

- Owner：`QQisDebugging`
- Repository name：`softwareCup`
- Visibility：建议先选 `Private`
- 不要勾选自动创建 README、`.gitignore` 或 License，因为本地仓库已经有首个提交。

创建完成后，在本地执行：

```powershell
cd D:\softwareCup
git remote add origin https://github.com/QQisDebugging/softwareCup.git
git push -u origin main
```

如果仓库名改了，把上面 URL 里的 `softwareCup` 换成实际仓库名。

## 邀请队友

进入 GitHub 仓库页面：

`Settings -> Collaborators and teams -> Add people`

建议先给队友 `Write` 权限，等项目稳定后再决定是否提升权限。

## 分支建议

- `main`：稳定可演示版本。
- `backend/*`：后端功能分支。
- `frontend/*`：前端功能分支。
- `agent/*`：Python 智能体和模型调用分支。
- `docs/*`：PPT、视频脚本、参赛文档分支。
