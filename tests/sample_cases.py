"""Original, host-reviewed demonstration analyses. Not a production inference engine."""
from copy import deepcopy

def base():
    return {'schema_version':'1.0','date':'2026-10-02','example':True,'commerce':'present',
        'subject':'先呈现具体困扰，再让商品作为解决工具出现',
        'materials':[],'evidence':[],'claims':{},'summary':{},'sections':[],'funnel':[],
        'dna':{},'learning':[],'image_tasks':[],'metrics':[],
        'limitations':['全部内容为原创合成演示，没有真实点击、阅读时长或成交数据。'],
        'do_not_copy':['不要照搬原作者的独有文案、图片、身份或生活故事。','没有亲自验证的使用效果、承重、销量和耐用性，不得写成自己的体验。']}

def material(d, mid, roles, content=None, image=None):
    m={'id':mid,'label':{'M1':'图1：封面插画','M2':'图2：使用条件','M3':'图3：边界说明','T1':'用户提供的标题','T2':'用户提供的正文'}.get(mid,mid),'kind':'image' if image else 'text','roles':roles}
    if image:m.update(file=image,inspected=True)
    else:m['content']=content
    d['materials'].append(m)

def evidence(d, eid, mid, observation, quote=None, location='材料可见区域', clear=True):
    kind='quote' if quote is not None else 'visual'
    e={'id':eid,'material_id':mid,'kind':kind,'location':location,'observation':observation,'clear':clear}
    if quote is not None:e['quote']=quote
    d['evidence'].append(e)

def c(d,cid,statement,ids,kind='ANALYSIS'):
    d['claims'][cid]={'text':statement,'type':kind,'evidence_ids':ids}
    return cid

def learn(d, name, what, why, transfer, ids):
    d['learning'].append({'what':c(d,name+'a',what,ids,'RECOMMENDATION'),'why':c(d,name+'b',why,ids),'transfer':c(d,name+'c',transfer,ids,'RECOMMENDATION')})

def title_case():
    d=base();d['subject']='用具体空间困扰引出一个可继续了解的方案'
    title='租房台面总是挤？19.9元的折叠杯架，先看看尺寸再决定'
    material(d,'T1',['title'],title)
    evidence(d,'E1','T1','标题包含租房台面拥挤、价格、折叠杯架及量尺寸条件。',title,'完整标题')
    c(d,'product','标题明确提及折叠杯架。',['E1'],'FACT')
    c(d,'price','标题标注19.9元；不是当前成交价验证。',['E1'],'FACT')
    c(d,'audience','可能面向台面空间紧张、需要摆放杯具的租房人群。',['E1'])
    c(d,'pain','具体困扰是台面拥挤，而不是笼统地追求精致生活。',['E1'])
    c(d,'click','问句先让读者判断是否遇到同一困扰，低价信息降低继续了解的心理门槛，尺寸提醒又留下适配判断任务。',['E1'])
    c(d,'keywords','原文关键词：租房、台面、折叠杯架。潜在搜索词可研究“小厨房杯子收纳”；尚无搜索量依据。',['E1'])
    c(d,'formula','具体人群与空间困扰 → 明确工具与价格 → 适配条件提醒。',['E1'])
    d['summary']={'product':'product','price':'price','audience':'audience','pain':'pain','click':'click','dna':'formula'}
    d['sections']=[{'id':'title','heading':'标题从哪里建立点击理由','claim_ids':['keywords','click','formula']}]
    d['funnel']=[{'stage':'click','claim_id':'click'}];d['dna']={'traffic':'click','formula':'formula'}
    learn(d,'L1','把宽泛需求写成一个可识别的生活困扰。','“台面挤”比“好物分享”更容易让特定读者辨认相关性。','迁移场景与困扰的关系，使用自己商品真实能解决的问题。',['E1'])
    learn(d,'L2','让价格与具体工具一起出现。','读者可以同时判断商品类别与继续了解的成本，而不是被孤立低价吸引。','只使用真实且口径清楚的价格，不复制未核验优惠。',['E1'])
    learn(d,'L3','标题留出适配判断，而不是承诺人人适用。','尺寸条件可能减少夸大感，也为后续内容设置需要回答的问题。','后文实际提供适配条件；如果无法兑现，就不要设置这个承诺。',['E1'])
    return d

def cover_case():
    d=base();d['subject']='场景问题、大字层级与工具露出，共同建立点击理由'
    material(d,'M1',['cover'],'', 'image-01.png')
    evidence(d,'E1','M1','上方深绿色两行大字：“租房台面总是挤？”“先把杯子立起来”。',location='图1上方')
    evidence(d,'E2','M1','中下部是绿色杯架与三个浅色杯子的平面插画，背景以米色台面块面表示；没有人物。',location='图1中下部')
    evidence(d,'E3','M1','底部独立深绿色价格块写“示例价19.9元”，下方标明折叠杯架、插画演示不代表实拍。',location='图1底部')
    c(d,'product','封面文字标注“折叠杯架”；图中为示意插画。',['E2','E3'],'FACT')
    c(d,'price','封面标注“示例价19.9元”，不能作为真实售价。',['E3'],'FACT')
    c(d,'audience','可能面向在意台面收纳、希望改善空间利用的租房人群。',['E1'])
    c(d,'pain','封面用“台面总是挤”提出具体空间困扰。',['E1'],'FACT')
    c(d,'focus','深色大字位于上方浅底留白区，文字对比与字号可能先吸引扫读；中部绿色杯架是第二个较大的视觉单元。没有眼动数据验证阅读顺序。',['E1','E2'])
    c(d,'composition','图文上下分区：上方提出问题，中部让工具可见，底部补价格。产品占据中部插画的重要面积，但这里不声称精确占比。',['E1','E2','E3'])
    c(d,'style','画面是扁平插画，不是真人家庭实拍；它能解释摆放关系，却不能充当真实使用或效果证据。',['E2','E3'])
    c(d,'click','场景问句建立相关性，“立起来”给出一种解决方向，杯架露出让方向可理解；价格块补充进一步了解的门槛提示。',['E1','E2','E3'])
    c(d,'cover_formula','明确空间困扰的大字 → 可辨认的解决工具 → 独立价格补充。',['E1','E2','E3'])
    d['summary']={'product':'product','price':'price','audience':'audience','pain':'pain','click':'click','dna':'cover_formula'}
    d['sections']=[{'id':'cover','heading':'封面如何安排第一眼的信息','claim_ids':['focus','composition','style','cover_formula']}]
    d['funnel']=[{'stage':'click','claim_id':'click'}];d['dna']={'traffic':'click','formula':'cover_formula'}
    learn(d,'L1','先让读者读到具体场景的问题。','上方大字与浅底对比，降低扫读时的识别负担；对相关人群才可能有效。','学习主信息的层级，不照搬这句文案或假装拥有同一生活场景。',['E1'])
    learn(d,'L2','让商品与它处理的问题出现在同一画面关系中。','杯子和架子的组合比孤立产品图更容易解释用途。','用自己商品的真实使用方式表达关系，插画不要冒充效果实拍。',['E2'])
    learn(d,'L3','把价格放在次级信息位。','价格可以补充判断，但不必抢占场景和用途的首要解释位置。','只展示可核验价格与条件，避免用假低价制造冲动。',['E3'])
    return d

BODY='租房厨房的杯子一多，台面就挤。先量台面和杯子高度，再考虑这个折叠杯架。使用步骤是量尺寸、放架子、摆杯子。商品介绍写它可以折叠，示例标价19.9元。摆放示意看起来更整齐，但这里没有承重与耐用测试。先量尺寸，再判断适不适合；不合适就别买。'

def full_case():
    d=cover_case();d['subject']='先解决“是否适合”，再讨论“是否值得买”'
    material(d,'M2',['gallery'],'','image-02.png');material(d,'M3',['gallery'],'','image-03.png')
    material(d,'T1',['title'],'租房台面总是挤？先把杯子立起来')
    material(d,'T2',['body'],BODY)
    evidence(d,'E4','M2','图中写先量台面、别挡住水槽操作区，以及量尺寸→放架→摆杯；明确注明未进行承重测试。',location='图2上方与底部')
    evidence(d,'E5','M3','图中写“看得见的变化，不是效果保证”，并提示只展示摆放、不证明耐用性。',location='图3标题及下方')
    evidence(d,'E6','T1','标题以台面拥挤的问题和把杯子立起来的方向相连。','租房台面总是挤？先把杯子立起来','标题')
    evidence(d,'E7','T2','正文先说明杯子多导致台面挤，再提出量尺寸和考虑折叠杯架。','租房厨房的杯子一多，台面就挤。先量台面和杯子高度，再考虑这个折叠杯架。','正文开头')
    evidence(d,'E8','T2','正文介绍使用顺序、可折叠卖点和示例价格。','使用步骤是量尺寸、放架子、摆杯子。商品介绍写它可以折叠，示例标价19.9元。','正文中段')
    evidence(d,'E9','T2','正文明确没有承重与耐用测试，结尾建议按适用性决定。','摆放示意看起来更整齐，但这里没有承重与耐用测试。先量尺寸，再判断适不适合；不合适就别买。','正文末段')
    c(d,'scene','主要情境是租房厨房的杯具收纳与台面空间分配。',['E1','E7'])
    c(d,'type','主类型倾向场景问题解决，辅助类型是使用步骤说明；不是完整产品性能测评。',['E4','E7','E8'])
    c(d,'title','标题将“台面挤”与“立起来”连接，先给出改善方向，再让读者从画面与正文理解采用什么工具。',['E6'])
    c(d,'body','正文按“具象困扰→适配条件→工具出现→使用顺序→卖点与价格→测试缺口→自主判断”推进。它让商品承担解决任务，而非只重复推荐。',['E7','E8','E9'])
    c(d,'placement','折叠杯架首次在正文第二句出现，之前铺垫杯子多和台面挤；同时给出量尺寸条件。商品以待判断的解决工具出现，广告感相对克制，但这不是商业合作状态判定。',['E7','E9'])
    c(d,'retention','“杯子立起来”留下怎样摆、是否放得下的问题，尺寸检查和操作顺序提供继续阅读的具体信息。没有阅读时长数据，不能验证实际停留。',['E4','E7','E8'])
    c(d,'trust','承认没有承重、耐用测试，并说明不适合就别买，可能降低单向夸赞带来的疑虑；这些诚实边界仍不是性能证明。',['E5','E9'])
    c(d,'interest','用途与摆放步骤使读者更容易判断商品是否解决自己的空间问题；兴趣机制依赖实际尺寸与使用条件匹配。',['E4','E7','E8'])
    c(d,'conversion','潜在购买理由是明确用途加较低标示价格；主要阻力是尺寸、承重和耐用信息不足。承担购买考虑任务的是适配判断与价格组合，而非已经得到验证的效果。',['E7','E8','E9'])
    c(d,'trafficDNA','让读者在具体生活困扰中识别自己，再给出可见的解决方向。',['E1','E6'])
    c(d,'retentionDNA','把解决方向拆成读者需要核对的条件与动作，让继续阅读有任务。',['E4','E8'])
    c(d,'trustDNA','展示能说明的使用过程，同时说清不能证明的性能边界。',['E4','E5','E9'])
    c(d,'conversionDNA','具体用途 × 适配检查 × 明确价格口径；缺少性能证据时保留购买阻力。',['E7','E8','E9'])
    c(d,'formula','具象场景困扰 → 工具化解决方向 → 可检查的使用条件 → 明示证据边界 → 自主购买判断。',['E1','E4','E7','E8','E9'])
    c(d,'task1','图1可能承担点击与初步识别任务：大字提出问题，插画让工具出现，价格提供补充判断。',['E1','E2','E3'])
    c(d,'task2','图2把注意力转向“是否放得下、如何摆放”，可能连接兴趣与适用性判断；没有实际测量结果。',['E4'])
    c(d,'task3','图3收束效果预期并提示局限，可能降低夸大感；未展示真实前后对比，不能称为效果证明。',['E5'])
    d['summary'].update(scene='scene',content_type='type',retention='retention',trust='trust',conversion='conversion',learn='placement',dna='formula')
    d['sections'] += [{'id':'title','heading':'标题承诺与正文承接','claim_ids':['title']},{'id':'body','heading':'正文按什么功能推进','claim_ids':['body']},{'id':'placement','heading':'产品如何成为解决工具','claim_ids':['placement']},{'id':'trust','heading':'信任线索与证明缺口','claim_ids':['trust']},{'id':'conversion','heading':'购买理由与购买阻力','claim_ids':['conversion']}]
    d['funnel']=[{'stage':s,'claim_id':cid} for s,cid in [('click','click'),('retention','retention'),('trust','trust'),('interest','interest'),('conversion','conversion')]]
    d['dna']={'traffic':'trafficDNA','retention':'retentionDNA','trust':'trustDNA','conversion':'conversionDNA','formula':'formula'}
    d['image_tasks']=[{'material_id':mid,'claim_ids':[cid]} for mid,cid in [('M1','task1'),('M2','task2'),('M3','task3')]]
    d['sequence_note']='三张原创演示图按设计顺序展示；不是对真实平台笔记顺序的还原。'
    d['learning']=[]
    learn(d,'F1','先提出适用性条件，再推荐工具。','量尺寸让读者参与判断，可能降低不合适购买与过度推销感。','为自己的商品找到真实限制，并提供可执行的核对方式。',['E7','E9'])
    learn(d,'F2','用后续内容兑现封面留下的问题。','封面说“立起来”，后续解释摆放顺序；承诺与信息承接相连才有继续看的理由。','迁移“问题→操作信息”的连接，不只模仿问句。',['E1','E4','E8'])
    learn(d,'F3','把证据边界写进内容。','承认未测试项可能降低夸大感，但能否建立信任仍需验证。','展示自己实际完成的测试及条件；未做过的性能测试明确留白。',['E5','E9'])
    learn(d,'F4','让价格服务于用途判断。','读者先知道能做什么，再判断标价是否值得考虑；价格不是独立的成交证明。','保留真实价格口径与适配条件，不复制示例数值。',['E7','E8'])
    return d

def text_case():
    source=full_case();d=base();d['subject']='正文如何把商品放进一个有条件的解决过程'
    d['materials']=[m for m in source['materials'] if m['kind']=='text']
    d['evidence']=[e for e in source['evidence'] if e['material_id'].startswith('T')]
    c(d,'product','用户提供的正文提及折叠杯架。',['E7'],'FACT')
    c(d,'price','正文写“示例标价19.9元”，未核验实际售价。',['E8'],'FACT')
    c(d,'click','标题把台面困扰和立体收纳方向相连，可能吸引遇到同类问题的人继续了解。',['E6'])
    for key in ['scene','type','title','body','placement','retention','conversion','retentionDNA','conversionDNA']:
        if all(i in {e['id'] for e in d['evidence']} for i in source['claims'][key]['evidence_ids']):d['claims'][key]=deepcopy(source['claims'][key])
    c(d,'retention','正文逐步给出量尺寸、放架和摆杯信息，让继续阅读有明确的信息收益。',['E7','E8'])
    c(d,'trust','明确未进行性能测试，可能降低单向夸赞感，但不证明实际使用效果。',['E9'])
    c(d,'scene','正文把问题放在租房厨房的杯具收纳场景中。',['E7'])
    c(d,'formula','困扰 → 适配条件 → 产品工具 → 使用过程 → 局限与判断。',['E7','E8','E9'])
    d['summary']={'product':'product','price':'price','scene':'scene','click':'click','retention':'retention','trust':'trust','conversion':'conversion','dna':'formula'}
    d['sections']=[{'id':sid,'heading':heading,'claim_ids':[cid]} for sid,heading,cid in [('title','标题逻辑','title'),('body','正文功能结构','body'),('placement','产品植入','placement'),('conversion','成交假设与阻力','conversion')]]
    d['dna']={'traffic':'click','retention':'retention','trust':'trust','conversion':'conversion','formula':'formula'}
    d['funnel']=[{'stage':s,'claim_id':s} for s in ['click','retention','trust','conversion']]
    learn(d,'X1','先说明适用条件。','条件信息让消费者有机会排除不适合的情境。','用自己产品可核验的规格承接，而非照搬尺寸或故事。',['E7'])
    learn(d,'X2','把使用方式写成动作。','量、放、摆比抽象“好用”更容易被理解。','记录真实步骤与限制，不虚构使用过程。',['E8'])
    learn(d,'X3','保留性能信息的空白。','承认没测过比将外观变化当作耐用性证明更可靠。','自己的测试做了多少就说多少。',['E9'])
    return d

def noncommerce_case():
    d=base();d['commerce']='absent';d['subject']='一段散步记录，不强行解释为卖货'
    material(d,'T2',['body'],'今天散步看到了晚霞，想记录这一刻。')
    evidence(d,'E1','T2','内容记录散步与晚霞，没有可见商品或购买提示。','今天散步看到了晚霞，想记录这一刻。','完整文字')
    c(d,'kind','当前文字是生活记录，不是典型带货内容；没有可识别的销售对象。',['E1'])
    c(d,'mechanism','具体时刻与景象可能唤起相似体验，但仅凭一句话无法判断传播表现。',['E1'])
    c(d,'formula','具体生活时刻 → 可共感的情绪入口。',['E1'])
    d['summary']={'content_type':'kind','click':'mechanism','dna':'formula'}
    d['sections']=[{'id':'body','heading':'表达方式','claim_ids':['kind','mechanism']}];d['dna']={'traffic':'mechanism','formula':'formula'}
    return d

def blurred_case():
    d=base();d['commerce']='uncertain';d['subject']='模糊数据不补数，先明确研究边界'
    material(d,'T2',['metrics'],'用户补充：这张图的销量看不清。')
    evidence(d,'E1','T2','用户说明销量看不清。','销量看不清','用户补充',False)
    d['evidence'][0]['kind']='user_statement'
    c(d,'unknown','目前无法辨认销量，不能据此判断商品销售表现或笔记贡献。',['E1'])
    d['sections']=[{'id':'metrics','heading':'当前能判断什么','claim_ids':['unknown']}]
    d['metrics']=[{'label':'销量','display':None,'clear':False,'scope':'对象与统计时间未确定','evidence_id':'E1'}]
    return d

CASES={'title':title_case,'cover':cover_case,'text':text_case,'full':full_case,'noncommerce':noncommerce_case,'blurred':blurred_case}
