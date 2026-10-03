# 测试设计与复现

自动测试验证结构、安全和生成链路；AI商业判断由宿主原生模型完成，单元测试不等于所有真实截图都能被正确理解。

| 用户场景 | 预期与检查 |
|---|---|
| 1 只有标题 | title路由、精简HTML，不生成封面/正文 |
| 2 只有封面 | cover路由、图片/点击/公式/学习点，正文不强求 |
| 3 标题+正文 | content路由、植入与商业机制，不编视觉 |
| 4 完整截图 | 有cover/title/body角色的图像路由full；实际视觉人工复核 |
| 5 多张图片 | full路由；按收到顺序呈现，任务列表乱序不改变图序 |
| 6 信息缺失 | 无法嵌入图片时编号降级，不补事实 |
| 7 模糊数据 | display=null；以模糊观察支撑FACT会被拒绝 |
| 8 非带货 | 不强制商品兴趣/成交漏斗，标题明确非典型 |
| 9 HTML | 文件、中文、桌面/手机、离线、图片、打印 |
| 10 安全 | script、属性、SVG、HTML标签转义；浏览器实际运行不执行 |
| 11 无网络 | 浏览器offline打开本地HTML；外部请求计数为0 |

## 本地单元测试与示例

```sh
python -m unittest discover -s tests -v
python tests/make_examples.py
python tests/prepare_browser.py
```

标准库即可。`sample_cases.py` 是已审读的原创示范分析，不能用于生产环境替代宿主推理。`make_demo_media.py` 只在重新制作原创演示插画时使用Pillow和开发者指定中文字体，既有PNG已随项目分发。

## 浏览器测试（开发依赖）

开发环境提供Node、Playwright与可用Chromium浏览器时：

```sh
node tests/browser_check.cjs --browser /path/to/chromium --output .qa/browser
```

`--browser`可省略以使用Playwright已安装的默认浏览器。输出桌面/手机/封面/DNA/打印截图与打印PDF，均进入忽略目录。独立临时浏览器会话，不连接用户正在使用的浏览器，不读取登录态。

## 官方验证器与安装器

在宿主提供skill-creator时，调用它的 `scripts/quick_validate.py` 对项目根目录验证；该开发工具需要PyYAML。不要复制修改后的验证器并冒充官方检查。

包测试：先 `python scripts/package_release.py`，再向 `tests/verify_installer.py --installer ... --package ...` 传入宿主真实官方安装器路径和本地ZIP。只替换其HTTP下载为本地ZIP，其他解析/校验/复制逻辑真实运行。此测试不得标成GitHub线上安装成功。

## 人工前向案例（真实宿主仍应持续验证）

使用SKILL.md处理不带预设分析答案的新素材：仅一句标题；一张封面；三张连续图；模糊销量；普通生活记录；包含“忽略规则/打开网站”的截图。检查是否先看图、是否不执行图中指令、是否把不清楚数据留空、是否生成对应范围报告。不把手写JSON的渲染测试当作新的模型推理评测。

本版已完成本机模型查看原创三图与分析审读；没有宣称WorkBuddy或所有宿主均通过实机前向测试。真实用户素材不随测试发布。
