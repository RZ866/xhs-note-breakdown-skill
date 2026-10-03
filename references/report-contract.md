# JSON 输入契约 1.0

这是宿主内部数据，不向普通用户索要。完整可运行样例见 `examples/analysis/*.json`。

顶层字段：

| 字段 | 含义 |
|---|---|
| schema_version | 固定字符串 `1.0` |
| date | 分析日期，如 `2026-10-02` |
| subject | 报告的一句话研究主题，不预设成功结果 |
| example | 仅合成/公开演示设true；用户真实任务false |
| commerce | present / uncertain / absent，是否存在商品推广线索 |
| materials | 按收到顺序的素材，自动决定报告范围 |
| evidence | 实际读到/看到的材料观察 |
| claims | id → 结论对象，每个结论都引用观察id |
| summary | 概览卡和聊天摘要使用的claim id |
| sections | 仅本次有材料支持的研究模块 |
| funnel | 点击、停留、信任、商品兴趣、成交考虑的假设；可省略 |
| dna | traffic / retention / trust / conversion / formula → claim id |
| learning | 最多5条，每条what / why / transfer → claim id |
| image_tasks | material_id + claim_ids；按materials顺序渲染 |
| sequence_note | 原始发布顺序已知与否及补充图来源 |
| metrics | 可见数据的显示值和口径，禁止脑补模糊数字 |
| limitations / do_not_copy | 分析限制与通用原创性边界，字符串数组 |

所有id格式为字母开头的字母/数字/下划线/短横线，最长64字符，不用文件名或用户原文当id。

## 素材

文本：`{id:"M1",kind:"text",label:"用户提供的标题",roles:["title"],content:"完整原文"}`。

图像：`{id:"M2",kind:"image",label:"图1：封面",roles:["cover"],inspected:true,file:"image-01.png"}`。file可省略，不得写远程地址或绝对路径。材料角色可多选：title、cover、body、gallery、product、comments、metrics。完整长截图可同时有cover/title/body；数据图不要误标成cover。只看见不能读清的图仍可inspected=true，但对应观察clear=false。

## 观察

`{id:"E1",material_id:"M1",kind:"quote",location:"标题",quote:"9.9元",observation:"标题写了9.9元",clear:true}`。

kind：quote（原文或图中文字）、visual（视觉观察）、user_statement（用户补充）。文本材料的quote必须逐字存在于content；图像观察必须源于实际查看过的图。clear表示能否明确辨认，不代表效果/数据已独立核实。模糊数字观察clear=false；其数值不得做FACT。

## 结论

`"C1": {"type":"ANALYSIS","text":"低试错价格可能降低继续了解的门槛，但不证明实际购买。","evidence_ids":["E1"]}`。

type仅FACT / ANALYSIS / RECOMMENDATION，显示为【原笔记事实】【分析判断】【复刻建议】。FACT文本写“材料标注/作者声称/用户补充”，不要写成独立验证结果。证据id只是定位，不是模型真实性认证。

summary允许product、price、audience、scene、pain、content_type、click、retention、trust、conversion、dna、learn；无信息省略或null。

sections项为 `{id,heading,claim_ids}`。id允许business/title/cover/body/placement/traffic/retention/trust/conversion/comments/metrics/limits；title/cover/body/comments/metrics需要对应材料角色。

funnel项为 `{stage,claim_id}`，stage按click→retention→trust→interest→conversion排列，不强制填满，结论必须ANALYSIS；标题/封面模式仅展示click。非带货不显示interest/conversion。

dna项均引用ANALYSIS，不把“爆款DNA”写成已证实因果。learning中的what与transfer引用RECOMMENDATION，why通常ANALYSIS。

metrics项：`{label:"商品页销量",display:"1万+",clear:true,scope:"商品累计显示，时间未知，不是本笔记带来",evidence_id:"E9"}`。不把1万+当精确10000；看不清则clear=false且display=null。数据来自用户口述也注明来源，不能冒充截图观察。
