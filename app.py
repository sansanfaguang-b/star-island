from __future__ import annotations
from datetime import date, datetime, time
from html import escape
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import plotly.graph_objects as go
import streamlit as st
import swisseph as swe

st.set_page_config(page_title="星屿 · 星盘与 MBTI 探索", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

SIGNS = [
    {"name":"白羊座","glyph":"♈","element":"火","mode":"开创","core":"先行动，再在真实反馈里校准方向。你需要挑战感、选择权和清楚的目标，遇到卡点时往往愿意成为第一个动起来的人。","gift":"敢于启动、直率、有恢复力，能把犹豫变成尝试。","edge":"节奏太快时，可能把“马上解决”放在“先理解完整”之前。","bond":"关系里重视坦诚、活力和彼此保有主动性。"},
    {"name":"金牛座","glyph":"♉","element":"土","mode":"固定","core":"重视稳定、感官经验和可持续的价值。你倾向于让事情落地，确认它值得之后，再持续投入时间与心力。","gift":"可靠、耐心、审美稳定，擅长把资源积累成真正可用的成果。","edge":"面对变化时，可能需要更长时间确认安全感，也容易守住已经熟悉的办法。","bond":"关系里看重踏实的陪伴、可信的承诺和细水长流的照料。"},
    {"name":"双子座","glyph":"♊","element":"风","mode":"变动","core":"通过信息、交流和比较来认识世界。你很容易发现同一件事的多个侧面，也常在提问与连接中获得灵感。","gift":"好奇、反应快、表达灵活，擅长把不同领域的线索串起来。","edge":"信息太多时，注意力可能分散；把“知道很多”推进到“完成一件”会更有力量。","bond":"关系里重视交流、轻松感和持续的新鲜话题。"},
    {"name":"巨蟹座","glyph":"♋","element":"水","mode":"开创","core":"先感知情境中的安全与情绪，再决定如何投入。你容易记住关系里的细节，也会本能地保护自己珍惜的人和空间。","gift":"共情敏锐、照顾周到，对群体氛围和隐性需求有很强的感受力。","edge":"情绪受到触动时，可能先退回壳里；把感受说清楚比等待别人猜中更有效。","bond":"关系里需要信任、情感回应和可以安心回去的共同空间。"},
    {"name":"狮子座","glyph":"♌","element":"火","mode":"固定","core":"希望把心力投入到有创造感、值得骄傲的事情里。你需要真诚的认可，也愿意把热情与慷慨带到团队之中。","gift":"有感染力、表达大方，能鼓励他人并为作品注入个人风格。","edge":"被忽视时可能把认可看得过重；让价值感不只依赖外界掌声，会更自在。","bond":"关系里欣赏坦荡、热情和明确的珍视，也乐于回馈关注。"},
    {"name":"处女座","glyph":"♍","element":"土","mode":"变动","core":"通过观察、拆解和改进来建立秩序。你关注细节并希望事情更有效、更准确；服务与专业能力常是你表达在乎的方式。","gift":"细致、善于诊断问题、能把复杂任务整理成可执行步骤。","edge":"标准过高时，可能迟迟不肯交付；允许“足够好”先进入现实，才能继续迭代。","bond":"关系里重视可靠的小事、实际帮助和彼此认真对待生活。"},
    {"name":"天秤座","glyph":"♎","element":"风","mode":"开创","core":"通过比较、协商和审美判断寻找更合适的平衡。你会留意互动是否公平，也擅长让不同立场的人重新进入对话。","gift":"有分寸、懂合作、能看见双边需求并营造舒服的交流氛围。","edge":"过度考虑每个人的感受时，自己的选择可能被推迟；明确偏好也是一种公平。","bond":"关系里需要尊重、对等沟通与共同做决定的空间。"},
    {"name":"天蝎座","glyph":"♏","element":"水","mode":"固定","core":"关注表层之下的动机、信任与真实变化。你倾向于深度投入，不太满足于只维持表面的热闹，也有面对复杂议题的韧性。","gift":"洞察力强、忠诚、能在压力中集中力量完成深层转变。","edge":"谨慎自保时可能把试探当作保护；逐步表达边界和需要，能减少误解。","bond":"关系里看重诚实、深度、信任以及彼此承担真实的能力。"},
    {"name":"射手座","glyph":"♐","element":"火","mode":"变动","core":"通过探索、学习和更大的视野寻找意义。你需要成长空间，喜欢把零散经验放进一个更开阔的故事里。","gift":"乐观、有远见、敢于跨出舒适区，也擅长传递信念与热情。","edge":"追逐下一种可能时，可能低估眼前细节和长期承诺的重要性。","bond":"关系里需要诚实、共同成长和足够的自由呼吸空间。"},
    {"name":"摩羯座","glyph":"♑","element":"土","mode":"开创","core":"通过目标、责任和时间积累建立可靠结构。你重视能力与结果，也愿意为长远发展承受阶段性的辛苦。","gift":"有责任感、能规划长期路线，遇到困难时通常愿意继续把事情做好。","edge":"过度自我要求时，可能把休息和情感表达看成次要任务。","bond":"关系里重视可信赖、共同承担和经得起时间检验的行动。"},
    {"name":"水瓶座","glyph":"♒","element":"风","mode":"固定","core":"习惯从系统和群体角度观察问题，珍视独立思考，也愿意尝试不一样的规则。你常在距离感中看清结构。","gift":"有原创想法、尊重差异，能看到未来趋势和群体层面的改进机会。","edge":"保持客观时可能显得疏离；让别人知道你在乎什么，会让连接更具体。","bond":"关系里需要精神交流、平等和不被控制的个人空间。"},
    {"name":"双鱼座","glyph":"♓","element":"水","mode":"变动","core":"对情绪、想象与环境氛围有很强的接收力。你会从艺术、直觉和共情中理解人，也需要独处整理吸收来的感受。","gift":"富有想象力、共情细腻，能理解复杂而矛盾的人类经验。","edge":"边界不清时容易替别人承担过多；把善意与责任区分开，会保护你的能量。","bond":"关系里重视温柔、理解、浪漫想象和情绪上的被接住。"},
]

PLANETS = [
    ("太阳",swe.SUN,"☉","核心身份、生命意志与持续投入的方向"),
    ("月亮",swe.MOON,"☽","情绪安全感、习惯反应与内在照料需求"),
    ("水星",swe.MERCURY,"☿","思考、学习、表达与信息处理方式"),
    ("金星",swe.VENUS,"♀","关系吸引力、审美偏好与价值感"),
    ("火星",swe.MARS,"♂","行动动力、边界表达与冲突处理"),
    ("木星",swe.JUPITER,"♃","扩展机会、信念与成长方式"),
    ("土星",swe.SATURN,"♄","责任课题、结构感与长期练习"),
    ("天王星",swe.URANUS,"♅","独立性、革新冲动与非典型路径"),
    ("海王星",swe.NEPTUNE,"♆","想象力、理想投射与敏感边界"),
    ("冥王星",swe.PLUTO,"♇","深层转化、权力感与重建能力"),
]

PLANET_ROLES = {
    "太阳":"你愿意逐渐成为怎样的人，以及最有生命力的投入方向",
    "月亮":"你在何种情境下更容易感到安全，以及压力时会回到的习惯",
    "水星":"你如何收集信息、形成判断、学习并把想法传递给别人",
    "金星":"你如何感受吸引、表达喜欢、建立价值判断和享受美感",
    "火星":"你如何发起行动、争取资源、处理阻力和表达个人边界",
    "木星":"你在哪些经验中容易打开视野，以及什么信念能支持成长",
    "土星":"你需要通过时间建立的能力，以及把焦虑转化为结构的方式",
    "天王星":"你渴望保持独立、打破惯例和探索不同做法的领域",
    "海王星":"你的想象、理想与共情如何工作，也提醒你留意模糊边界",
    "冥王星":"你可能经历深层重组、重新获得主动权和恢复力量的领域",
    "上升点":"你进入新环境时的第一反应、外在节奏与探索世界的入口",
}

HOUSES = [
    "自我呈现、身体感受、个人开端与面对世界的方式",
    "资源、金钱观、自我价值与建立稳定感的方式",
    "学习、表达、日常交流、信息环境与近距离联结",
    "家庭、私密生活、根源记忆与内在安顿",
    "创造、兴趣、游戏感、浪漫表达与个人作品",
    "工作习惯、健康管理、技能练习与日常服务",
    "一对一关系、合作契约、伴侣关系与公开协商",
    "共享资源、深度信任、危机应对与心理转化",
    "高等学习、远行、哲学信念与拓展视野",
    "事业方向、公共角色、长期目标与社会责任",
    "社群、朋友、共同理想与面向未来的计划",
    "独处、休息、潜意识素材、幕后工作与放下过程",
]

ASPECTS = [
    (0,7,"合相","两种驱动力紧密相连，通常更容易一起被体验。它能带来集中感，也需要留意不要把两种不同需求混成同一种反应。"),
    (60,5,"六分相","两种能力之间存在可被主动调动的配合空间。机会通常需要通过练习、合作或具体选择才能显现。"),
    (90,6,"四分相","两种需求会互相施压，促使你调整策略。它不等于坏结果，更像提醒你建立边界、节奏与新的解题方式。"),
    (120,6,"三分相","两种能力较容易自然协作，常形成熟悉的优势。也可以有意识地使用它，避免只停留在“我本来就会”。"),
    (180,7,"对分相","两种主题需要在关系或选择中找到动态平衡。看见两边各自的价值，往往比把其中一边压下去更有帮助。"),
]

CITY_COORDS = {
    "江门":(22.5787,113.0815),"广州":(23.1291,113.2644),"深圳":(22.5431,114.0579),
    "北京":(39.9042,116.4074),"上海":(31.2304,121.4737),"成都":(30.5728,104.0668),
    "武汉":(30.5928,114.3055),"杭州":(30.2741,120.1551),"香港":(22.3193,114.1694),
    "自定义经纬度":(22.5787,113.0815),
}

TIMEZONES = {
    "中国标准时间 · UTC+8":"Asia/Shanghai","日本标准时间 · UTC+9":"Asia/Tokyo",
    "协调世界时 · UTC":"UTC","英国时间":"Europe/London","中欧时间":"Europe/Paris",
    "美国东部时间":"America/New_York","美国太平洋时间":"America/Los_Angeles",
}

QUESTIONS = {
    "能量来源":("E","I",[
        ("在多人讨论中，我通常愿意主动加入并贡献想法。","E"),("和熟悉的人深入交谈，通常比参加大型聚会更让我放松。","I"),
        ("我常常一边说一边整理自己的思路。","E"),("重要发言前，我更喜欢先独自想清楚再表达。","I"),
        ("连续一段时间独处后，我会主动寻找互动和新鲜交流。","E"),("连续社交后，我通常需要安静独处来恢复精力。","I"),
        ("在陌生场合，我往往能较快开启一段对话。","E"),("我更愿意先观察环境，再决定是否加入谈话。","I"),
        ("我喜欢把新认识的人逐渐带入自己的社交圈。","E"),("我更珍视少数深入、稳定的关系，而不是广泛认识很多人。","I"),
        ("集体活动常让我感觉自己参与到了正在发生的事情里。","E"),("我需要有自己的空间，才能稳定地听见内心想法。","I"),
    ]),
    "信息偏好":("S","N",[
        ("理解新事物时，我会先关注它有哪些具体事实和细节。","S"),("我很容易从眼前信息联想到未来可能出现的多种情形。","N"),
        ("我更信任经过验证、步骤清楚的做法。","S"),("相比操作步骤，我通常更想先理解背后的概念和原理。","N"),
        ("描述经历时，我倾向于讲清楚发生了什么、先后顺序是什么。","S"),("我常从不同事件之间发现重复出现的模式或象征。","N"),
        ("制定计划时，我会优先考虑现有资源和可执行条件。","S"),("遇到新任务时，我会先想它可能发展成什么、有哪些创新空间。","N"),
        ("我希望说明尽量明确、具体，并能对应到现实例子。","S"),("比起标准答案，我更喜欢开放问题和可以继续探索的观点。","N"),
        ("我擅长记住实际发生过的细节和可观察到的变化。","S"),("我常关注一个决定背后的趋势、象征意义或长远影响。","N"),
    ]),
    "决策依据":("T","F",[
        ("做决定时，我会优先检查逻辑是否一致、标准是否公平。","T"),("做决定时，我会认真考虑它会怎样影响相关的人。","F"),
        ("给出反馈时，我宁愿清楚直接，也不想让重点变得模糊。","T"),("给出反馈时，我会特别注意对方是否有能力接住这些话。","F"),
        ("遇到争议，我通常先把事实、论点和个人情绪分开看。","T"),("遇到争议，我通常先了解每个人在意的价值和处境。","F"),
        ("我欣赏基于原则、一视同仁的处理方式。","T"),("我认为好的决定也应照顾到具体的人和现实关系。","F"),
        ("解决问题时，我更关注哪种方案有效、可复核。","T"),("解决问题时，我更关注方案是否尊重人的需要与感受。","F"),
        ("面对需要取舍的情况，我愿意承认有些决定必须不讨好所有人。","T"),("面对需要取舍的情况，我会努力寻找能被各方理解的表达方式。","F"),
    ]),
    "生活节奏":("J","P",[
        ("开始一项重要任务前，我通常会先拆解步骤并安排时间。","J"),("我喜欢保留几个选择，等更多信息出现后再定下来。","P"),
        ("清楚的日程和截止时间会让我更安心。","J"),("太早把计划锁死，会让我觉得缺少根据情况调整的空间。","P"),
        ("我更喜欢尽早完成决定，再把精力转向下一件事。","J"),("我常在临近交付时进入状态，快速整合此前收集的材料。","P"),
        ("清单、分类和明确的收尾能帮助我保持掌控感。","J"),("我更习惯根据现场状况灵活安排，不完全依赖预先计划。","P"),
        ("我通常希望重要事项不要悬而未决太久。","J"),("同时探索几种可能性，会让我更容易发现合适方向。","P"),
        ("我会提前准备，以免最后一刻被突发状况打乱。","J"),("临时出现的新机会常让我愿意重新调整原来的安排。","P"),
    ]),
}

TYPE_TITLES = {
    "ISTJ":"稳健的执行者","ISFJ":"细致的守护者","INFJ":"洞察的引路者","INTJ":"系统的设计者",
    "ISTP":"冷静的解题者","ISFP":"敏锐的创造者","INFP":"价值的追寻者","INTP":"概念的探索者",
    "ESTP":"灵活的行动者","ESFP":"鲜活的体验者","ENFP":"灵感的连接者","ENTP":"可能性的挑战者",
    "ESTJ":"目标的组织者","ESFJ":"关系的协调者","ENFJ":"成长的推动者","ENTJ":"方向的推进者",
}

SIDE_READINGS = {
    "E":{"base":"你较容易在互动、讨论和外部反馈中整理能量。先把想法放进对话里，常能帮助你发现它真正的形状。","strength":"主动连接、快速进入场景、带动讨论并在团队中建立动能。","growth":"为自己留出不被打断的思考时段；重要决定可先写下来，再听取外部意见。","stress":"压力大时可能不断寻找回应或马上展开行动，安静独处有时更能帮助你复位。"},
    "I":{"base":"你较容易通过独处、观察和内部整理恢复能量。先消化信息再表达，通常能让你的判断更稳定。","strength":"深度倾听、独立推进、长期专注，以及在复杂情境中保留自己的判断。","growth":"不必等到想法完全成熟才开口；阶段性表达能让别人更早理解并支持你。","stress":"压力大时可能把自己收得太紧；找一位可信任的人进行具体、有限的交流会有帮助。"},
    "S":{"base":"你更信任具体事实、可观察的细节和已经验证的经验。清楚的现实信息能帮助你建立判断。","strength":"稳定执行、关注质量、记录细节，并把抽象计划转成一步步可落实的行动。","growth":"在确认事实之后，也给长期趋势和新路径留出一点探索空间。","stress":"压力大时可能只盯着眼前问题；暂时拉远视角有助于看见更合适的路径。"},
    "N":{"base":"你更容易关注模式、联系和未来可能性。抽象概念与开放问题常能激发你的好奇心。","strength":"提出新视角、跨领域联想、看见趋势，并为团队指出还没有被试过的方向。","growth":"把灵感写成下一步、期限和验证标准，能让想法真正抵达现实。","stress":"压力大时可能越想越远、跳过当下细节；回到可确认的信息能帮助重新落地。"},
    "T":{"base":"你更习惯先检查逻辑、原则与结果的一致性。清楚的标准能让决定更可解释。","strength":"客观分析、识别矛盾、直接处理问题，并在复杂选择里保持判断标准。","growth":"把人的处境纳入分析并不会削弱逻辑，反而能让方案更完整、更能被执行。","stress":"压力大时可能显得过于尖锐或只谈解决方案；先确认对方听懂你的善意再提出建议。"},
    "F":{"base":"你较自然地把人的感受、价值和关系影响纳入决定。对情境的体察能帮助你选择更有人味的做法。","strength":"共情、协调、发现未被说出的需求，并把方案调整得更适合真实的人。","growth":"在照顾关系的同时也说出自己的优先级；清楚边界能让关心更持久。","stress":"压力大时可能为了维持和气而延迟表达；先说事实和需要，再讨论彼此感受。"},
    "J":{"base":"你更喜欢先建立计划和阶段性结论。明确的进度、责任和收尾能带来稳定感。","strength":"组织资源、按计划推进、设定重点，并让团队知道下一步要做什么。","growth":"在必要时为新信息预留调整空间；计划服务于目标，不需要变成自我束缚。","stress":"压力大时可能把每个细节都排得很满；优先级排序和留白能保护执行质量。"},
    "P":{"base":"你更喜欢保留弹性，根据新情况调整行动。开放选择能帮助你在变化中发现机会。","strength":"适应变化、临场整合信息、迅速应对突发状况，并在不确定环境里保持灵活。","growth":"为重要任务设一个最小可交付版本和检查点，能让弹性不被误解为拖延。","stress":"压力大时可能同时打开太多可能性；先选一个低风险的小步骤，往往能重新启动。"},
}

def add_styles() -> None:
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        html, body, [data-testid="stAppViewContainer"] { background:#080b18; color:#f5f6ff; overflow-x:hidden; }
        [data-testid="stAppViewContainer"] {
          background:radial-gradient(ellipse at 8% 3%,rgba(102,77,203,.20),transparent 35%),
          radial-gradient(ellipse at 92% 18%,rgba(26,164,190,.13),transparent 30%),
          radial-gradient(ellipse at 55% 88%,rgba(110,57,153,.13),transparent 34%),
          linear-gradient(145deg,#080b18 0%,#0c1023 48%,#090d1b 100%);
        }
        [data-testid="stAppViewContainer"]::before {
          content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.65;
          background-image:radial-gradient(1px 1px at 7% 17%,#fff 99%,transparent),
          radial-gradient(1px 1px at 24% 73%,#b9c7ff 99%,transparent),
          radial-gradient(1px 1px at 41% 31%,#fff 99%,transparent),
          radial-gradient(1.5px 1.5px at 61% 82%,#d7c8ff 99%,transparent),
          radial-gradient(1px 1px at 79% 24%,#fff 99%,transparent),
          radial-gradient(1px 1px at 92% 61%,#9ceeff 99%,transparent);
          background-size:360px 310px;animation:starDrift 75s linear infinite;
        }
        @keyframes starDrift { from{transform:translateY(0)} to{transform:translateY(-170px)} }
        [data-testid="stHeader"]{background:transparent}
        [data-testid="stMainBlockContainer"]{max-width:1220px;padding-top:1.3rem;padding-bottom:4rem;position:relative;z-index:1}
        .hero{position:relative;overflow:hidden;padding:2rem 2.2rem;border:1px solid rgba(190,198,255,.20);border-radius:26px;
          background:linear-gradient(120deg,rgba(37,43,83,.78),rgba(17,26,50,.63) 56%,rgba(23,43,62,.54));
          box-shadow:0 20px 70px rgba(0,0,0,.30),inset 0 1px 0 rgba(255,255,255,.08);margin-bottom:1.25rem}
        .hero:after{content:"";position:absolute;width:390px;height:390px;right:-70px;top:-210px;border-radius:50%;
          background:radial-gradient(circle,rgba(133,127,255,.28),transparent 68%);filter:blur(2px);pointer-events:none}
        .eyebrow{color:#aeb7ff;letter-spacing:.22em;font-size:.72rem;font-weight:700}
        .hero h1{color:#fff;font-size:clamp(2rem,5vw,3.7rem);letter-spacing:.035em;margin:.55rem 0}
        .hero p{color:#d7dcf7;max-width:760px;font-size:1.02rem;line-height:1.85;margin:0}
        .glass{border:1px solid rgba(189,198,255,.16);border-radius:20px;background:linear-gradient(145deg,rgba(25,31,59,.78),rgba(15,22,42,.78));
          box-shadow:0 14px 48px rgba(0,0,0,.22),inset 0 1px 0 rgba(255,255,255,.04);padding:1.1rem 1.25rem;margin:.45rem 0 1rem}
        .tag{display:inline-block;padding:.25rem .65rem;margin:.15rem .3rem .15rem 0;border:1px solid rgba(175,181,255,.23);
          border-radius:999px;color:#dfe1ff;background:rgba(118,105,226,.12);font-size:.78rem}
        .planet-card{min-height:160px;padding:1rem 1.05rem;margin:.3rem 0;border-radius:18px;border:1px solid rgba(190,198,255,.15);
          background:linear-gradient(150deg,rgba(31,38,72,.72),rgba(14,22,42,.76))}
        .planet-card .glyph{color:#c8baff;font-size:1.35rem}.planet-name{color:#fff;font-weight:700;margin-left:.45rem}
        .planet-sign{color:#cbd3ff;margin-top:.55rem;font-size:1.02rem}.planet-meta{color:#aab4d8;font-size:.79rem;margin-top:.3rem}
        .type-big{font-size:clamp(2.5rem,8vw,5.4rem);font-weight:800;letter-spacing:.14em;color:#fff;line-height:1.1}
        .type-title{color:#c4b8ff;font-size:1.2rem;margin-top:.35rem}
        .meter-row{margin:.75rem 0 1.05rem}.meter-head{display:flex;justify-content:space-between;color:#e7eaff;font-size:.86rem;margin-bottom:.3rem}
        .meter-track{height:9px;border-radius:99px;background:rgba(149,161,211,.18);overflow:hidden}
        .meter-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#6ee7e2,#8b8cff 60%,#d197ff);box-shadow:0 0 16px rgba(143,137,255,.7)}
        .small-note{color:#adb7d5;font-size:.84rem;line-height:1.7}.report-text{color:#e9ebff;line-height:1.92;font-size:.98rem}
        div[data-testid="stExpander"]{border:1px solid rgba(189,198,255,.15);border-radius:16px;background:rgba(17,24,45,.72)}
        div[data-testid="stTabs"] button{color:#cbd3f5} div[data-testid="stTabs"] button[aria-selected="true"]{color:#fff}
        div[data-testid="stForm"]{border:1px solid rgba(189,198,255,.15);border-radius:18px;padding:1.1rem;background:rgba(15,22,42,.74)}
        .stButton>button,.stFormSubmitButton>button{border-radius:12px;border:1px solid rgba(194,185,255,.36);
          background:linear-gradient(105deg,#6960c8,#477eaa);color:white;font-weight:700;box-shadow:0 8px 24px rgba(85,91,189,.20)}
        .stButton>button:hover,.stFormSubmitButton>button:hover{border-color:#d3caff;color:white}
        label,p,li,[data-testid="stMarkdownContainer"]{color:#eff1ff}
        .stCaption,[data-testid="stCaptionContainer"]{color:#aeb8d9!important}

        /* --- 终极暴力修复云端组件白底白字 Bug --- */
        /* 1. 修复输入框 (数字、文本、日期、时间) */
        div[data-baseweb="input"] {
            background-color: #11182d !important;
            border: 1px solid rgba(186, 195, 241, 0.25) !important;
            border-radius: 8px !important;
        }
        div[data-baseweb="input"] > input {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        
        /* 2. 修复下拉框 (出生地点、时区) */
        div[data-baseweb="select"] > div {
            background-color: #11182d !important;
            border: 1px solid rgba(186, 195, 241, 0.25) !important;
            border-radius: 8px !important;
            color: #ffffff !important;
        }
        div[data-baseweb="select"] span {
            color: #ffffff !important;
        }
        
        /* 3. 修复数字输入框旁边的 加减 按钮 */
        button[data-testid="stNumberInputStepDown"], 
        button[data-testid="stNumberInputStepUp"] {
            background-color: #11182d !important;
            color: #ffffff !important;
            border-color: rgba(186, 195, 241, 0.25) !important;
        }

        /* 4. 修复下拉弹出的菜单 */
        div[data-baseweb="popover"] > div {
            background-color: #11182d !important;
        }
        div[data-baseweb="popover"] li {
            color: #ffffff !important;
        }
        /* -------------------------------------- */

        @media(max-width:700px){[data-testid="stMainBlockContainer"]{padding-left:.75rem;padding-right:.75rem}.hero{padding:1.35rem 1.2rem;border-radius:20px}.glass{padding:.9rem}}
        </style>
        """,
        unsafe_allow_html=True,
    )

def sign_for(longitude: float) -> dict:
    return SIGNS[int((longitude % 360) // 30)]

def house_for(longitude: float, cusps: tuple[float, ...]) -> int:
    value = longitude % 360
    for index, start in enumerate(cusps):
        end = cusps[(index + 1) % 12]
        span = (end - start) % 360
        distance = (value - start) % 360
        if distance < span or abs(distance - span) < 1e-7:
            return index + 1
    return 1

def calculate_chart(birth_local: datetime, timezone_name: str, latitude: float, longitude: float, exact_time: bool) -> dict:
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("无法识别这个时区，请选择列表中的时区。") from exc
    local_aware = birth_local.replace(tzinfo=zone)
    utc = local_aware.astimezone(ZoneInfo("UTC"))
    decimal_hour = utc.hour + utc.minute / 60 + utc.second / 3600
    jd = swe.julday(utc.year, utc.month, utc.day, decimal_hour)
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED
    cusps: tuple[float, ...] | None = None
    ascendant: float | None = None
    mc: float | None = None
    if exact_time:
        try:
            cusp_values, angles = swe.houses_ex(jd, latitude, longitude, b"P")
        except Exception:
            cusp_values, angles = swe.houses_ex(jd, latitude, longitude, b"W")
        cusps = tuple(float(x) % 360 for x in cusp_values)
        ascendant, mc = float(angles[0]) % 360, float(angles[1]) % 360
    placements: dict[str, dict] = {}
    for name, body, glyph, _role in PLANETS:
        values, _retflags = swe.calc_ut(jd, body, flags)
        lon = float(values[0]) % 360
        placements[name] = {
            "longitude":lon,"degree":lon%30,"sign":sign_for(lon),"glyph":glyph,
            "house":house_for(lon,cusps) if cusps else None,"speed":float(values[3]),
        }
    if ascendant is not None:
        placements["上升点"]={"longitude":ascendant,"degree":ascendant%30,"sign":sign_for(ascendant),
                             "glyph":"ASC","house":1,"speed":None}
    return {"placements":placements,"cusps":cusps,"ascendant":ascendant,"mc":mc,"utc":utc,
            "local":local_aware,"latitude":latitude,"longitude":longitude,"timezone":timezone_name,
            "exact_time":exact_time}

def get_aspects(placements: dict[str, dict]) -> list[dict]:
    names = [name for name, *_ in PLANETS]
    found = []
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            a, b = placements[first]["longitude"], placements[second]["longitude"]
            separation = abs((a - b + 180) % 360 - 180)
            for target, orb_limit, aspect_name, description in ASPECTS:
                orb = abs(separation - target)
                if orb <= orb_limit:
                    found.append({"first":first,"second":second,"name":aspect_name,"orb":orb,"description":description})
                    break
    return sorted(found, key=lambda item: item["orb"])

def make_wheel(chart: dict) -> go.Figure:
    fig = go.Figure()
    theta = list(range(361))
    for radius, color, width in [(1.0,"rgba(176,183,255,.75)",1.3),(.61,"rgba(176,183,255,.40)",1)]:
        fig.add_trace(go.Scatterpolar(r=[radius]*len(theta),theta=theta,mode="lines",
            line=dict(color=color,width=width),hoverinfo="skip",showlegend=False))
    for index, sign in enumerate(SIGNS):
        angle = index*30
        fig.add_trace(go.Scatterpolar(r=[.61,1.0],theta=[angle,angle],mode="lines",
            line=dict(color="rgba(159,170,222,.35)",width=1),hoverinfo="skip",showlegend=False))
        fig.add_trace(go.Scatterpolar(r=[.82],theta=[angle+15],mode="text",text=[sign["glyph"]],
            textfont=dict(size=22,color="#d4c8ff"),hoverinfo="skip",showlegend=False))
    if chart["cusps"]:
        for cusp in chart["cusps"]:
            fig.add_trace(go.Scatterpolar(r=[0,.58],theta=[cusp,cusp],mode="lines",
                line=dict(color="rgba(113,207,221,.26)",width=1,dash="dot"),hoverinfo="skip",showlegend=False))
    names = [name for name, *_ in PLANETS]
    longitudes = [chart["placements"][name]["longitude"] for name in names]
    radii = [.72+(i%3)*.055 for i in range(len(names))]
    labels = [f"{chart['placements'][name]['glyph']} {name}" for name in names]
    custom = [f"{name} · {chart['placements'][name]['sign']['name']} {chart['placements'][name]['degree']:.1f}°"
              + (f" · 第{chart['placements'][name]['house']}宫" if chart["placements"][name]["house"] else "") for name in names]
    fig.add_trace(go.Scatterpolar(r=radii,theta=longitudes,mode="markers+text",text=labels,textposition="top center",
        customdata=custom,hovertemplate="%{customdata}<extra></extra>",
        marker=dict(size=10,color="#8ee7e3",line=dict(color="#f5fbff",width=1.2),opacity=.96),
        textfont=dict(size=10,color="#f6f5ff"),showlegend=False))
    if chart["ascendant"] is not None:
        fig.add_trace(go.Scatterpolar(r=[0,1.02],theta=[chart["ascendant"]]*2,mode="lines",
            line=dict(color="#f4b5ff",width=2),hovertemplate="上升点<extra></extra>",showlegend=False))
    fig.update_layout(height=490,margin=dict(l=25,r=25,t=20,b=20),paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",polar=dict(bgcolor="rgba(8,12,27,.35)",
        radialaxis=dict(visible=False,range=[0,1.14],showgrid=False),
        angularaxis=dict(visible=False,rotation=90,direction="clockwise",showgrid=False)),font=dict(color="#f3f4ff"))
    return fig

def placement_text(name: str, item: dict, exact_time: bool) -> str:
    sign, house = item["sign"], item["house"]
    role = PLANET_ROLES[name]
    p1 = f"**{name}**在这张象征性地图里指向{role}。它落在**{sign['name']}**，呈现出“{sign['core']}”的表达底色。"
    p2 = f"这股配置的可用资源是：{sign['gift']} 当你需要把它用得更成熟时，可以观察自己是否也会遇到这样的惯性：{sign['edge']}"
    if house:
        p3 = f"它位于**第{house}宫**，主题更容易在“{HOUSES[house-1]}”这些生活场景中被体验。宫位描述的是注意力较常聚集的领域，不代表某件事必然发生。"
    elif name == "上升点":
        p3 = "上升点以准确出生时刻和地点计算；如果出生时间有较大误差，上升星座与宫位也可能改变。"
    else:
        p3 = "由于没有准确出生时间，这个配置暂不标注宫位；月亮靠近星座交界时，也可能需要更精确的时刻确认。"
    p4 = f"在人际关系中，相关需求可以这样表达：{sign['bond']} 这份解读适合用作自我观察的提问起点，而不是对性格或未来的定论。"
    return "\n\n".join((p1,p2,p3,p4))

def chart_report_markdown(chart: dict) -> str:
    placements = chart["placements"]
    sections = ["# 我的出生星盘探索报告",
        f"- 出生时间：{chart['local'].strftime('%Y-%m-%d %H:%M')}（{chart['timezone']}）",
        f"- 出生坐标：{chart['latitude']:.4f}, {chart['longitude']:.4f}",
        f"- 时间精度：{'准确时间' if chart['exact_time'] else '时间未知，按当地正午估算'}",""]
    for name, *_ in PLANETS:
        sections += [f"## {name} · {placements[name]['sign']['name']}",placement_text(name,placements[name],chart["exact_time"]),""] 
    if "上升点" in placements:
        sections += ["## 上升点",placement_text("上升点",placements["上升点"],chart["exact_time"]),""] 
    aspects = get_aspects(placements)
    sections += ["## 主要相位"]
    if aspects:
        sections.extend(f"- **{a['first']} {a['name']} {a['second']}**（容许度 {a['orb']:.1f}°）：{a['description']}" for a in aspects[:10])
    else:
        sections.append("- 在本工具采用的主要相位与容许度范围内，没有找到明显的行星相位。")
    sections += ["","> 本报告是占星传统中的象征性自我探索内容，不是科学预测、诊断或专业心理服务。"]
    return "\n".join(sections)

def mbti_score(answer_values: dict[str, int]) -> dict:
    letters, scores = [], {}
    for axis_name, (first, second, items) in QUESTIONS.items():
        signed = 0
        for index, (_question, pole) in enumerate(items):
            response = answer_values[f"q_{axis_name}_{index}"]
            signed += (response-3) * (1 if pole == first else -1)
        first_percent = max(0,min(100,round(50 + signed*50/24)))
        second_percent = 100-first_percent
        chosen = first if first_percent >= 50 else second
        preference = max(first_percent,second_percent)
        strength = "较均衡" if preference < 58 else ("轻到中等倾向" if preference < 72 else "较鲜明倾向")
        scores[axis_name] = {"first":first,"second":second,"first_percent":first_percent,
            "second_percent":second_percent,"chosen":chosen,"strength":strength,"preference":preference}
        letters.append(chosen)
    code = "".join(letters)
    return {"code":code,"title":TYPE_TITLES[code],"scores":scores}

def build_mbti_summary(report: dict) -> str:
    code = report["code"]
    chosen = [SIDE_READINGS[letter] for letter in code]
    overview = (f"这次结果是 **{code} · {TYPE_TITLES[code]}**。它把四种偏好组合成一张“默认倾向地图”："
        f"你更可能通过{chosen[0]['base'].split('。')[0]}，倾向于{chosen[1]['base'].split('。')[0]}；"
        f"做决定时通常{chosen[2]['base'].split('。')[0]}，安排生活时则{chosen[3]['base'].split('。')[0]}。")
    strengths = " ".join(f"**{letter}：**{SIDE_READINGS[letter]['strength']}" for letter in code)
    growth = " ".join(f"**{letter}：**{SIDE_READINGS[letter]['growth']}" for letter in code)
    relational = ("在人际沟通中，可以先说明自己的信息处理和决策偏好，也主动确认对方需要的是倾听、事实、建议还是一起定计划。"
        "偏好描述不是给人贴标签；不同角色、压力水平和熟悉程度都会影响一个人的表现。")
    return "\n\n".join((overview,f"**可调用的优势：**{strengths}",f"**可练习的平衡：**{growth}",relational))

def mbti_report_markdown(report: dict) -> str:
    lines = [f"# MBTI 自我探索报告：{report['code']} · {report['title']}","","## 四个偏好维度"]
    for axis_name, score in report["scores"].items():
        lines.append(f"- {axis_name}：{score['first']} {score['first_percent']}% / {score['second']} {score['second_percent']}%（{score['strength']}）")
    lines += ["","## 组合画像",build_mbti_summary(report),"","## 四个维度的细读"]
    for axis_name, score in report["scores"].items():
        side = SIDE_READINGS[score["chosen"]]
        lines += [f"### {axis_name} · {score['chosen']}",side["base"],
            f"**优势：**{side['strength']}",f"**成长练习：**{side['growth']}",f"**压力提醒：**{side['stress']}",""]
    lines += ["","> MBTI 是偏好描述框架，不是临床诊断或能力测验；接近均衡的维度可以随情境变化。"]
    return "\n".join(lines)

def render_meter(axis_name: str, score: dict) -> None:
    width = score["first_percent"]
    st.markdown(f'<div class="meter-row"><div class="meter-head"><span>{escape(axis_name)} · {score["first"]} {width}%</span>'
        f'<span>{score["second"]} {score["second_percent"]}% · {escape(score["strength"])}</span></div>'
        f'<div class="meter-track"><div class="meter-fill" style="width:{width}%"></div></div></div>',unsafe_allow_html=True)

def render_chart_result(chart: dict) -> None:
    placements = chart["placements"]
    sun, moon = placements["太阳"]["sign"]["name"], placements["月亮"]["sign"]["name"]
    asc = placements["上升点"]["sign"]["name"] if "上升点" in placements else "需要准确时间"
    st.markdown('<div class="glass"><span class="tag">本命盘 · 热带黄道</span><span class="tag">行星位置与主要相位</span></div>',unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.metric("☉ 太阳",sun); b.metric("☽ 月亮",moon); c.metric("ASC 上升",asc)
    if not chart["exact_time"]:
        st.info("没有填写准确出生时间：行星暂按当地正午估算，不显示上升点、宫位和宫位解读。月亮若临近星座交界，也可能需要准确时刻确认。")
    left,right = st.columns([1.15,.85],gap="large")
    with left:
        st.markdown("### ✦ 你的星盘罗盘")
        st.plotly_chart(make_wheel(chart),use_container_width=True,config={"displayModeBar":False})
        st.caption("星座环按黄道十二宫展示；悬停行星点可查看度数与宫位。")
    with right:
        st.markdown("### 行星落点")
        for name,_body,glyph,_role in PLANETS:
            item=placements[name]
            house_text=f" · 第{item['house']}宫" if item["house"] else ""
            st.markdown('<div class="planet-card"><span class="glyph">'+escape(glyph)+'</span><span class="planet-name">'+escape(name)+
                '</span><div class="planet-sign">'+escape(item["sign"]["name"])+f' · {item["degree"]:.1f}°</div><div class="planet-meta">'+
                escape(item["sign"]["element"])+"象 · "+escape(item["sign"]["mode"])+"宫"+house_text+"</div></div>",unsafe_allow_html=True)
        if "上升点" in placements:
            item=placements["上升点"]
            st.markdown('<div class="planet-card"><span class="glyph">↗</span><span class="planet-name">上升点</span><div class="planet-sign">'+
                escape(item["sign"]["name"])+f' · {item["degree"]:.1f}°</div><div class="planet-meta">出生时刻与地点共同决定</div></div>',unsafe_allow_html=True)
    st.markdown("### ♢ 深度解析")
    for name,*_ in PLANETS:
        item=placements[name]
        with st.expander(f"{item['glyph']} {name} · {item['sign']['name']}"+(f" · 第{item['house']}宫" if item["house"] else ""),
                         expanded=name in ("太阳","月亮")):
            st.markdown(placement_text(name,item,chart["exact_time"]))
    if "上升点" in placements:
        item=placements["上升点"]
        with st.expander(f"↗ 上升点 · {item['sign']['name']}"):
            st.markdown(placement_text("上升点",item,chart["exact_time"]))
    aspects=get_aspects(placements)
    with st.expander("✧ 主要行星相位",expanded=True):
        if aspects:
            for aspect in aspects[:12]:
                st.markdown(f"**{aspect['first']} {aspect['name']} {aspect['second']}**　容许度 {aspect['orb']:.1f}°  \n{aspect['description']}")
        else:
            st.write("在本工具采用的主要相位与容许度范围内，没有找到明显的行星相位。")
    st.download_button("下载星盘报告（Markdown）",chart_report_markdown(chart),"星屿_星盘报告.md",mime="text/markdown")

def render_mbti_result(report: dict) -> None:
    st.markdown(f'<div class="glass"><div class="type-big">{escape(report["code"])}</div><div class="type-title">{escape(report["title"])}</div>'
        '<p class="small-note">这表示问卷中更常出现的偏好，不是对能力、价值或未来的评判。</p></div>',unsafe_allow_html=True)
    st.markdown("### 四个偏好维度")
    cols=st.columns(2)
    for index,(axis_name,score) in enumerate(report["scores"].items()):
        with cols[index%2]: render_meter(axis_name,score)
    st.markdown("### 你的组合画像")
    st.markdown(build_mbti_summary(report))
    st.markdown("### 分维度细读")
    for axis_name,score in report["scores"].items():
        side=SIDE_READINGS[score["chosen"]]
        with st.expander(f"{axis_name}：{score['chosen']} 偏好 · {score['strength']}",expanded=True):
            st.markdown(side["base"]); st.markdown(f"**可调用的优势**　{side['strength']}")
            st.markdown(f"**成长练习**　{side['growth']}"); st.markdown(f"**压力提醒**　{side['stress']}")
    st.download_button("下载 MBTI 报告（Markdown）",mbti_report_markdown(report),"星屿_MBTI报告.md",mime="text/markdown")

def make_chart_prompt(chart: dict | None, mbti: dict | None) -> str:
    lines=[
        "请根据我提供的资料，生成一份具体、结构清晰、避免套话的自我探索报告。",
        "请把占星配置当作象征性叙事工具，把 MBTI 当作偏好描述框架；不要把它们写成科学诊断、能力评判、命运预测或医疗建议。",
        "请区分：我提供的客观输入、框架内的解释、需要我自行验证的假设。不要补造缺失的出生信息或配置。","",
    ]
    if chart:
        lines += ["【出生星盘配置】",f"出生时间：{chart['local'].strftime('%Y-%m-%d %H:%M')}（{chart['timezone']}）",
            f"时间精度：{'准确时间' if chart['exact_time'] else '未知，行星按当地正午估算；不使用上升点和宫位'}"]
        for name,*_ in PLANETS:
            item=chart["placements"][name]; house=f"第{item['house']}宫" if item["house"] else "宫位未计算"
            lines.append(f"{name}：{item['sign']['name']} {item['degree']:.1f}°，{house}")
        if "上升点" in chart["placements"]:
            item=chart["placements"]["上升点"]; lines.append(f"上升点：{item['sign']['name']} {item['degree']:.1f}°")
        aspects=get_aspects(chart["placements"])
        lines.append("主要相位："+("；".join(f"{x['first']}{x['name']}{x['second']}（{x['orb']:.1f}°）" for x in aspects[:10]) if aspects else "无明显主要相位"))
        lines.append("")
    if mbti:
        lines += ["【MBTI自评结果】",f"类型：{mbti['code']} · {mbti['title']}"]
        for axis_name,score in mbti["scores"].items():
            lines.append(f"{axis_name}：{score['first']} {score['first_percent']}% / {score['second']} {score['second_percent']}%（{score['strength']}）")
        lines.append("")
    lines += ["【请按以下结构撰写】",
        "1. 先用 150 字左右概括我的主要张力与可用资源，避免把类型写成标签。",
        "2. 分析沟通和学习方式、情绪与关系需求、行动与决策习惯、工作协作风格。",
        "3. 说明至少三个可能的优势，以及三个容易忽略的盲点；每点都解释形成机制和现实例子。",
        "4. 给出压力状态下可能出现的反应、可观察的预警信号，以及容易执行的复位办法。",
        "5. 提供一份一周内可以尝试的 3 项小行动，并说明怎样判断它们是否适合我。",
        "6. 指出哪些结论只是框架内的假设，最后列出 5 个问题让我用真实经历检验。",
        "语言具体、温和、有边界；不同配置之间若存在张力，请并列呈现，不要强行消成单一性格结论。"]
    return "\n".join(lines)

def main() -> None:
    add_styles()
    st.markdown('<div class="hero"><div class="eyebrow">A QUIET SPACE FOR SELF-DISCOVERY</div><h1>星屿 <span style="color:#b9adff">✦</span></h1>'
        '<p>一张出生星盘，一次 MBTI 自我探索。把星空当作提问的入口，把答案留给真实生活中的你。</p></div>',unsafe_allow_html=True)
    chart_tab,mbti_tab,synthesis_tab=st.tabs(["✦ 出生星盘","✧ MBTI 测评","☾ 综合报告"])
    with chart_tab:
        st.markdown("### 输入出生信息")
        st.markdown('<div class="small-note">出生时间和地点会影响上升点与宫位。经纬度采用东经为正、北纬为正。时间不清楚也可以继续，系统会省略依赖准确时间的内容。</div>',unsafe_allow_html=True)
        city=st.selectbox("出生地点",list(CITY_COORDS.keys()),index=0)
        place_name=st.text_input("地点名称","自定义地点") if city=="自定义经纬度" else city
        preset_lat,preset_lon=CITY_COORDS[city]
        with st.form("birth_form"):
            c1,c2=st.columns(2)
            with c1:
                birth_date=st.date_input("出生日期",value=date(2000,1,1),min_value=date(1800,1,1),max_value=date.today())
                birth_time=st.time_input("出生时间",value=time(12,0),step=60)
                exact_time=st.checkbox("这是准确出生时间",value=True)
            with c2:
                timezone_label=st.selectbox("出生地时区",list(TIMEZONES.keys()),index=0)
                timezone_name=TIMEZONES[timezone_label]
                latitude=st.number_input("纬度",min_value=-90.0,max_value=90.0,value=float(preset_lat),step=.0001,format="%.4f",key=f"lat_{city}")
                longitude=st.number_input("经度",min_value=-180.0,max_value=180.0,value=float(preset_lon),step=.0001,format="%.4f",key=f"lon_{city}")
            submitted=st.form_submit_button("生成我的星盘",use_container_width=True)
        if submitted:
            chosen_time=birth_time if exact_time else time(12,0)
            local_dt=datetime.combine(birth_date,chosen_time)
            try:
                result=calculate_chart(local_dt,timezone_name,latitude,longitude,exact_time)
                result["place_name"]=place_name
                st.session_state["star_chart_result"]=result
                st.success("星盘已经生成。向下滚动查看行星落点和逐项解析。")
            except Exception as exc:
                st.error(f"计算失败：{exc}")
        chart=st.session_state.get("star_chart_result")
        if chart:
            st.markdown("---")
            render_chart_result(chart)
    with mbti_tab:
        st.markdown("### 48 题 · 四个偏好维度")
        st.markdown('<div class="glass"><b>作答方式</b><p class="small-note">按你通常的状态作答，而不是按“理想中的自己”。1 = 非常不符合，2 = 不太符合，3 = 不确定或视情况而定，4 = 比较符合，5 = 非常符合。每题都要选择一个答案。</p></div>',unsafe_allow_html=True)
        with st.form("mbti_form"):
            for axis_name,(first,second,items) in QUESTIONS.items():
                with st.expander(f"{axis_name} · {first} / {second} · 12 题",expanded=axis_name=="能量来源"):
                    for index,(question,_pole) in enumerate(items):
                        st.radio(question,options=[1,2,3,4,5],index=None,horizontal=True,key=f"q_{axis_name}_{index}")
            mbti_submitted=st.form_submit_button("查看我的 MBTI 画像",use_container_width=True)
        if mbti_submitted:
            all_keys=[f"q_{axis}_{i}" for axis,(_first,_second,items) in QUESTIONS.items() for i in range(len(items))]
            missing=[key for key in all_keys if st.session_state.get(key) is None]
            if missing:
                st.error(f"还有 {len(missing)} 题没有作答，请完成所有题目后再查看结果。")
            else:
                answers={key:int(st.session_state[key]) for key in all_keys}
                st.session_state["mbti_result"]=mbti_score(answers)
                st.success("测评完成。以下结果反映本次作答中的偏好倾向。")
        mbti=st.session_state.get("mbti_result")
        if mbti:
            st.markdown("---")
            render_mbti_result(mbti)
    with synthesis_tab:
        st.markdown("### 把两张地图放在一起")
        chart=st.session_state.get("star_chart_result")
        mbti=st.session_state.get("mbti_result")
        if chart:
            p=chart["placements"]
            st.markdown(f'<div class="glass"><span class="tag">太阳 · {escape(p["太阳"]["sign"]["name"])}</span>'
                f'<span class="tag">月亮 · {escape(p["月亮"]["sign"]["name"])}</span>'
                +(f'<span class="tag">上升 · {escape(p["上升点"]["sign"]["name"])}</span>' if "上升点" in p else "")
                +"</div>",unsafe_allow_html=True)
        if mbti:
            st.markdown(f'<div class="glass"><span class="tag">MBTI · {escape(mbti["code"])}</span><span class="tag">{escape(mbti["title"])}</span></div>',unsafe_allow_html=True)
        if not chart and not mbti:
            st.info("先完成出生星盘或 MBTI 测评，这里会自动整理成一份可复制给 AI 的深度报告指令。")
        else:
            st.markdown("这段指令会带上你在本页生成的配置，要求另一个模型区分资料与解释、避免绝对化结论。")
            prompt=make_chart_prompt(chart,mbti)
            st.text_area("可复制的深度报告指令",value=prompt,height=420)
            st.download_button("下载综合报告指令",prompt,"星屿_AI深度报告指令.txt",mime="text/plain")
            if chart and mbti:
                combined=chart_report_markdown(chart)+"\n\n---\n\n"+mbti_report_markdown(mbti)
                st.download_button("下载完整综合档案（Markdown）",combined,"星屿_综合档案.md",mime="text/markdown")
        st.markdown('<div class="glass"><b>隐私与使用说明</b><p class="small-note">本程序在你启动的本机 Streamlit 页面中计算，不连接星盘 API，也不会自动上传出生资料。只有在你主动复制指令并粘贴到其他 AI 服务时，相关内容才会离开本机。占星与 MBTI 内容用于自我观察和娱乐，不构成科学预测、心理诊断或专业建议。</p></div>',unsafe_allow_html=True)

if __name__ == "__main__":
    main()
