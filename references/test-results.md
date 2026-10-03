# V1.0.0 验收记录

发布补充（2026-10-03）：真实GitHub下载安装 **PASS**。官方安装器从 RZ866/xhs-note-breakdown-skill 下载根目录并安装到隔离测试目录；不替换下载响应。下载版本的51项测试和六种报告生成均通过。GitHub Actions的Ubuntu/Windows × Python3.10/3.12四组测试全部通过：[运行记录](https://github.com/RZ866/xhs-note-breakdown-skill/actions/runs/37123555778)。下表保留开发验收当日记录。

日期：2026-10-02。下列结果来自实际执行；没有将未执行项目写成PASS。

| 检查 | 结果 | 证据与边界 |
|---|---|---|
| 官方Skill validator | PASS | 本机原版quick_validate.py输出Skill is valid |
| 单元与回归测试 | PASS | unittest共51项；范围、schema、证据、缺失、指标口径、转义、图片与发布检查 |
| 六种报告生成 | PASS | title、cover、text、full、noncommerce、blurred均生成HTML与聊天摘要 |
| 原生视觉示例审读 | PASS | 实际查看三张原创演示图；审读对应分析，未使用真实用户材料 |
| 桌面 | PASS | Edge92.0.902.67，1440×1000，图片加载，无横向溢出；视觉检查封面/DNA/概览 |
| 手机布局 | PASS | 同引擎390×844视口，无横向溢出；不等于手机实机测试 |
| 离线 | PASS | 隔离浏览器offline=true打开file HTML，无HTTP请求、无页面错误 |
| 中文 | PASS | 文本断言及实际截图检查 |
| 打印 | PASS | print媒体与实际A4 PDF生成，修复卡片断裂后检查第一页；未验收所有打印机 |
| 安全转义 | PASS | script/属性/SVG/路径逃逸等测试；恶意文字实际浏览器加载不执行 |
| 图片自包含 | PASS | data URI与原始字节一致；无需联网或配套目录 |
| 官方安装器离线包 | PASS | 真实安装器URL解析、根目录解压、复制、已有目录保护；仅HTTP响应替换为本地ZIP |
| 发布树检查 | PASS | 允许清单打包，密钥/个人路径模式扫描无命中；原创图片人工核查 |
| 新仓库真实GitHub下载 | NOT RUN | 尚未发布新仓库，不宣称已在线安装 |
| Codex GUI自动发现/WorkBuddy实机 | NOT RUN | 尚未将本项目安装进宿主并完成独立新对话验收 |
| GitHub Actions云端矩阵 | NOT RUN | 已提供工作流，尚未远端运行 |

没有未解决的已执行测试FAIL。最初检查发现封面公式被总DNA覆盖、打印卡片断开、审计规则匹配自身正则，均已修复；对应范围重新验证。

结构验证不能证明商业因果或模型永不误判。完整截图的自动化用例验证角色路由；没有把它包装为大量真实长截图视觉准确率评测。无真实曝光、停留或成交数据，不认证演示材料为爆款。

复现方法见[测试设计](../tests/test-cases.md)。本地浏览器截图、PDF、依赖和详细运行输出只放忽略目录，不进入发布包。公开示例为原创合成内容。
