# 规范与环境核查

检查日期：2026-10-02；在创建项目文件前完成规范、样例与本机安装器源码检查。

## 已查看的真实规范

- [OpenAI Build skills](https://developers.openai.com/plugins/build/skills)：每个Skill以SKILL.md为入口，name/description决定发现与触发，按需配置references/scripts等。
- [Codex / Build skills](https://learn.chatgpt.com/docs/build-skills)：Skill编写与使用说明。
- 本机官方 `skill-creator/SKILL.md`、`references/openai_yaml.md`、`scripts/init_skill.py` 与 `scripts/quick_validate.py`。
- 本机官方 `skill-installer/SKILL.md` 与 `install-skill-from-github.py`：仓库URL、path、name与目标目录的真实处理方式。
- 官方文档骰子Skill示例与本机bundled documents Skill：查看frontmatter、脚本调用和渐进披露用法；未复制它们的分析指令或代码。

本项目保留name/description/license frontmatter，名称46字符以内，符合小写字母短横线命名。UI展示信息单独放agents/openai.yaml，默认允许隐式触发，不把产品特有字段塞进通用frontmatter。

## 对需求的具体调整

1. **Skill不是独立推理程序。** 宿主模型完成视觉与商业分析，标准库脚本负责验证和生成；没有假装用规则模拟AI视觉。
2. **GitHub根目录安装需要明确路径和名称。** 本机官方安装器支持仓库URL，但仅给根URL在脚本层会缺path。README要求宿主内部传path=.及项目名；普通用户仍只给仓库地址，不需要命令。
3. **安装器不覆盖旧目录。** 更新必须由宿主处理旧版本替换，不宣称安装命令会自动覆盖。
4. **安装即用有宿主能力前提。** 需要看图与写文件；脚本方式还需已有Python3.10+。没有执行权限时允许宿主按模板直接生成，但不能伪造经过脚本校验或不存在的HTML文件。
5. **用户信息优先不是无条件事实认证。** 用户补充帮助解释研究对象，冲突保留双方。报告“原笔记事实”仅指素材呈现，不宣称独立核验。
6. **有图才显示原图。** 只嵌入用户提供、已获授权的本地栅格图；无法读取时编号降级。没有把本地路径写进发布文件或报告。
7. **GitHub发布准备与远端发布分开。** 本任务要求适合后续发布，未授权创建新的远端仓库；因此交付本地源码与ZIP，不伪造在线安装成功。

## 验证边界

官方validator已经实际运行，不只是自写正则。它检查入口语法，不证明模型判断准确。官方安装器的本地包下载替身测试检查URL解析、根目录解压和真实复制流程；它不等于新仓库已在线发布。

本机实际支持生成HTML文件，并使用独立浏览器引擎读取新报告完成测试。没有调用或控制用户已有浏览器会话，也没有访问用户Cookie。本机GUI平台的自动发现、WorkBuddy不同版本安装行为未做实机认证。
