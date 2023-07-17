''' Working Track '''
from module.track import Track

# content = '''
# <p></p>
# '''
# Track(pid='2023').save_track_description(
#    track_id='5a203', lang='zh-tw', content=content.strip())
#
# content = '''
# <p></p>
# '''
# Track(pid='2023').save_track_description(
#    track_id='5a203', lang='en', content=content.strip())

# ------

content = '''
<p>Blockchain enpowers a decentralized and trustless world. It is a combination of several fields such as cryptography, consensus algorithm and economic models. Since Satoshi Nakamoto published Bitcoin on 2008, there were countless technology rised and developed. Among those, the advanced technology such as Ethereum Smart Contract, Proof of Stake, Zero-knowledge Proof, and sharding are getting more mature. We would like to sincerely invite submissions from academia, industry and any individual who are intereted in this area. These topics include, but are not limited to:</p>
<ul>
    <li>Sharding</li>
    <li>Performance, Scalability Issues</li>
    <li>Security and Privacy Issues</li>
    <li>Zero Knowledge Proof</li>
    <li>Consensus Algorithms</li>
    <li>Blockchain-based Applications</li>
    <li>Decentralized App Development</li>
    <li>Smart Contracts</li>
    <li>Regulations and Policies in Cryptocurrency</li>
    <li>Token Economy</li>
    <li>Decentralized Internet Infrastructure</li>
</ul>
<p>Taipei Ethereum Meetup is a physical meetup community that focuses on the theory, implementation, and applications of Ethereum technology. Currently, speeches are shared voluntarily by community participants every month. Many of the participants are cryptography and blockchain enthusiasts and developers from different industries. Technical discussions sometimes also happen on Medium.</p>
<p>More information about Taipei Ethereum Meetup can be found on this <a href="https://www.meetup.com/Taipei-Ethereum-Meetup/">website</a></p>
'''
Track(pid='2023').save_track_description(
    track_id='5a203', lang='en', content=content.strip())

# ------

content = '''
<p>COSCUP 2023 再度推出 First-timer Program，來幫助所有想投稿的講者素人，我們將邀請具備豐富經驗的議程顧問，提前檢閱您的稿件，並給予修改建議，讓您能夠在最終投稿期限前修改、調整稿件，並於 CfP 結束後協助您將稿件轉到不同議程軌。</p>
<p>另外，請於投稿前詳閱此份說明：</p>
<ol>
    <li>講者素人定義為「沒有在研討會或是大型公開場合演講過的人」</li>
    <li>參與 First-timer Program 必須投在這裡，不能投在別的軌</li>
    <li>請於 4/14 - 4/21 期間投稿，徵稿系統將於 4/21 關閉</li>
    <li>COSCUP 議程組將於 5/08 把議程顧問回饋寄信給您，並將徵稿系統再次打開</li>
    <li>如有任何疑問或建議，請於 4/19 前來信至 program@coscup.org 詢問，感謝您</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='e1f88', lang='zh-tw', content=content.strip())

content = '''
<p>COSCUP 2023 is once again offering the First-timer Program to help novice speakers who wish to submit a proposal. We will invite experienced program advisors to review your submission in advance and provide editing suggestions. This will allow you to modify and adjust your proposal before the final submission deadline and to transfer it to a different track after the CfP has ended.</p>
<p>Before submitting, please read the following instructions carefully:</p>
<ol>
    <li>A novice speaker is defined as "someone who has not spoken at a conference or large public event before.</li>
    <li>To participate in the First-timer Program, you must submit your proposal here and not to any other track.</li>
    <li>Please submit your proposal between 4/14 and 4/21. The submission system will close on 4/21.</li>
    <li>COSCUP's program team will send feedback from the program advisors by email on 5/08 and reopen the submission system.</li>
    <li>If you have any questions or suggestions, please email program@coscup.org before 4/19. Thank you.</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='e1f88', lang='en', content=content.strip())

# ------

content = '''
<p>邀請身為 Gopher 的你，向大家分享您的經驗與技術，期待您能在演講桌前，與我們一起 have fun with golang。</p>
'''
Track(pid='2023').save_track_description(
    track_id='ffa04', lang='zh-tw', content=content.strip())

content = '''
<p>Inviting you, as a Gopher, to share your experience and expertise with everyone. We look forward to having you speak at the podium and having fun with Golang together.</p>
'''
Track(pid='2023').save_track_description(
    track_id='ffa04', lang='en', content=content.strip())

# ------
content = '''
<p>JVM（Java Virtual Machine）做為一個平台，已經演化成一個完整的生態系。其穩定與跨平台的特性已被各大企業驗證，也蘊育出 Java、Kotlin、Scala、Clojure、Groovy 等語言，可謂百家爭鳴、大放異彩。近年來 Kotlin 漸受重視、GraalVM 帶來更多可能。今年 COSCUP 依照往例，由台灣 JVM 相關社群再次組成聯盟，號召各方好手，匯集了與 JVM 應用有關的主題，包括但不限於前後端、桌面或行動應用、原生與跨平台…等，一起探索 JVM 的無限潛能。</p>
'''
Track(pid='2023').save_track_description(
    track_id='241e5', lang='zh-tw', content=content.strip())

content = '''
<p>JVM as a platform is becoming a mature ecosystem for developers. It’s stable, enterprise-ready, and nurtures the languages such as Java, Kotlin, Scala, Clojure, Groovy, etc. Our goal is to collect all the topics that are related to frontend, backend, desktop, mobile, native and cross-platform, and explore the potential of JVM.</p>
'''
Track(pid='2023').save_track_description(
    track_id='241e5', lang='en', content=content.strip())
# ------
content = '''
<p>Julia 是一個新興的高階、高效動態語言，以高效科學運算為原點，發展成一種通用語言，得力於 LLVM，加上語法本身優雅而精巧的設計，促成了高效的特性。由於易於開發而高效的特性，Julia 非常適合發展人工智慧及機器學習演算法，並且支援分散式運算、平行運算及共時。Julia 支援命令式、物件導向、函數式、泛型等等程式設計典範，讓這個語言更加豐富。本議程歡迎所有 Julia 稿件。</p>
'''
Track(pid='2023').save_track_description(
    track_id='99595', lang='zh-tw', content=content.strip())

content = '''
<p>Julia is a new high-level, high performance dynamic language. It originates from high performance scientific computing, and develops general-purpose programming language. Leveraging the power of LLVM and elegance of language design make high performance computation possible. Since the ease of use and high performance, Julia is suitable for rapid development for artificial intelligence (AI) and machine learning (ML). It support distributed computing, parallelism and concurrency. Julia support imperative programming, object-oriented programming, functional programming and generic programming etc. These programming paradigm enriches the language.</p>
'''
Track(pid='2023').save_track_description(
    track_id='99595', lang='en', content=content.strip())
# ------

content = '''
<p>Kubernetes Community Days (KCD) 是由雲原生計算基金會 (CNCF) 支持與認證的官方社群組織活動，此會議集結來自開源和雲原生社區的使用者及技術人員，以進行教育、協作和分享。</p>
<p>本次 Kubernetes Community Days Taiwan (KCD Taiwan) 是由台灣雲原生使用者社群 (Cloud Native Taiwan User Group, CNTUG) 所主辦的在地 KCD 的社群活動。其目的是透過本土社群的力量，讓更多人參與 Kubernetes 社群互相交流和學習，並以此持續發展和維持社群。</p>
'''
Track(pid='2023').save_track_description(
    track_id='a477c', lang='zh-tw', content=content.strip())

content = '''
<p>Kubernetes Community Days (KCD) is an official community event supported and certified by the Cloud Native Computing Foundation (CNCF). The conference brings together users and technical professionals from the open source and cloud native community for education, collaboration, and sharing.</p>
<p>Kubernetes Community Days Taiwan (KCD Taiwan) is a local KCD community event organized by the Cloud Native Taiwan User Group (CNTUG). Its purpose is to use the power of the local community to encourage more people to participate in the Kubernetes community for mutual exchange and learning, and to sustain and develop the community.</p>
'''
Track(pid='2023').save_track_description(
    track_id='a477c', lang='en', content=content.strip())

# ------

content = '''
<p>我們歡迎所有MySQL的使用者、開發者、以及任何關心MySQL的朋友們來這裡分享您對MySQL的經驗、心得、和點子</p>
'''
Track(pid='2023').save_track_description(
    track_id='318b3', lang='zh-tw', content=content.strip())

content = '''
<p>We welcome all MySQL users, developers, and anyone who cares about MySQL to come here and share your experiences, insights, and ideas about MySQL.</p>
'''
Track(pid='2023').save_track_description(
    track_id='318b3', lang='en', content=content.strip())

# ------

content = '''
<p>很多人以為，只要把資料放出來、公開在網路上、和人協作，就是所謂的「開源」。但其實開源是有定義的，而我們也很有幸可以參考其他人的討論，對開源設計有一個初步的想望。</p>
<p>在這個議程中，我們希望邀請有興趣的同好一起來討論「開源」文化走進設計時，會怎麼發展，會遇到什麼樣的限制。</p>
<h4>FOSDEM 2020 議程：</h4>
<p><a href="https://archive.fosdem.org/2020/schedule/event/what_are_we_talking_about_when_we_say_open_design/">https://archive.fosdem.org/2020/schedule/event/what_are_we_talking_about_when_we_say_open_design/</a>
<h4>參考先前 COSCUP 議程組對於 Open Source Design 討論的文件，設計領域的開源應包含以下至少其一：</h4>
<ol>
    <li>使用開源軟體作為設計工具</li>
    <li>採用他人以自由/開源授權條款發表的素材</li>
    <li>檔案使用開放檔案格式儲存散佈，其定義為至少有一個自由/開源軟體可正確開啟、非由單一廠商私自訂立的格式</li>
    <li>設計成品以開放/自由的授權條款發表，授權大眾使用</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='7932e', lang='zh-tw', content=content.strip())

content = '''
<p>Many people think that just by releasing data, making it public on the Internet, and collaborating with others is what "open source" means. However, open source does have a definition, and we are fortunate to have references to other people's discussions1 that give us a preliminary idea2 of open source design.</p>
<p>In this session, we hope to invite interested peers to discuss how "open source" culture is developing in design, and what limitations it may encounter.</p>
<h4>FOSDEM 2020 議程：</h4>
<p><a href="https://archive.fosdem.org/2020/schedule/event/what_are_we_talking_about_when_we_say_open_design/">https://archive.fosdem.org/2020/schedule/event/what_are_we_talking_about_when_we_say_open_design/</a>
<h4>Referring to the COSCUP program committee's discussion on Open Source Design, open source in the field of design should include at least one of the following:</h4>
<ol>
    <li>Use open source software as a design tool.</li>
    <li>Use materials published under free/open licenses by others.</li>
    <li>Use open file formats for storage and distribution, defined as formats that can be correctly opened by at least one free/open source software and are not created solely by a single vendor.</li>
    <li>Publish design work under an open/free license, authorizing public use.</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='7932e', lang='en', content=content.strip())

# ------

content = '''
<p>近年來隨著軟韌硬體的飛快進步及各項AI算法的到位，各項智能應用如雨後春筍般快速掘起，過去像智慧物聯網(AIoT)等相關應用都還需仰賴雲端來提供AI運算服務，如今在完全離線下亦可以實現，像是語音喚醒、運動偵測、異常偵測、影像分類、物件偵測等應用。此次議程希望召集更多有志一同的伙伴來分享一下關於開源離網邊緣智能（Edge AI）及微型機器學習(TinyML)的成果，期待讓更多人了解這項技術並落地，以便擁有更方便的生活。</p>
'''
Track(pid='2023').save_track_description(
    track_id='11f05', lang='zh-tw', content=content.strip())

content = '''
<p>Recently, with the rapid progress of software, hardware and various AI algorithms, various intelligent applications have sprung up like mushrooms after rain. In the past, related applications such as AIoT still relied on cloud to provide AI computing services. Now it can be achieved completely offline. Applications such as voice wake-up, motion detection, anomaly detection, image classification, object detection and other applications can be realized. This session hopes to gather more like-minded partners to share their achievements in open source Edge AI (Edge intelligence) and TinyML (Tiny Machine Learning & AI). We hope to let more people understand this technology and land it so that they can have a more convenient life.</p>
'''
Track(pid='2023').save_track_description(
    track_id='11f05', lang='en', content=content.strip())

# ------

content = '''
<p>行銷也和寫程式或 open source 有關係？Internet日益發達，世界上已經有很多電商平台及社群媒體利用數位行銷概念賺取龐大收益，加上政府近年積極推動數位轉型，不管是甚麼組織或是團體，都非常需要結合Martech策略，增加自我能見度。讓我們在 Open Source MarTech 議程軌，探討如何運用開放的力量，塑造 MarTech 的未來！</p>
<p>可能契合的議題:</p>
<ol>
    <li>運用 open data 於 MarTech 經驗分享</li>
    <li>open source MarTech stack best practice / 心得分享</li>
    <li>運用 MarTech 技術推廣開源專案</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='4f041', lang='zh-tw', content=content.strip())

content = '''
<p>Marketing can also be open sourced? In a digital era, there are many tech platforms or social media communities utilize digital marketing concept to profit enomously, especially not only within the government, but also among small/medium size cooperations, all promoting digital transformation to enhance the over all competitiveness both at home and abroad with Martech driven strategies.</p>
<p>MarTech=Marketing+ Technology MarTch can be divided into 6 categories:</p>
<ol>
    <li>Advertising& Promotion</li>
    <li>Content& Expereience</li>
    <li>Social& Relationships</li>
    <li>Commerce& Sales</li>
    <li>Data Management</li>
</ol>
<p>Let’s dive in Open Source Martech track to discover how to build the future of Martech with Open Source!</p>
<p>Possible tracks:</p>
<ol>
    <li>Sharing on cases that apply open data onto MarTech</li>
    <li>Open source MarTech stack best practice</li>
    <li>Use Martech to promote open source projects</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='4f041', lang='en', content=content.strip())

# ------

content = '''
<p>韌體是控制硬體設備的低層軟體，是最為基礎的啟動代碼。我們的基本原則是，透過公開並自由提供韌體的源代碼，開發社群可以合作改進和精進韌體，從而打造更安全、穩定和可靠的韌體，造福於所有人。同時，這也提供了更大的自定義和彈性，使用者可以簡便地修改韌體以滿足其特定需求。目前市場上大部分流通的韌體是閉源和專有的，這把它放在了我們通往自由和開源的前沿。</p>
<p>開源韌體專題旨在舉辦探索自由和開源韌體開發現狀和未來方向的分享會。</p>
<p>本專題接受關於多個主題的演講提案，包括：</p>
<ul>
    <li>開源韌體開發概述和入門介紹：開源韌體的歷史和演變，它的工作原理以及使用開源韌體的好處。</li>
    <li>韌體安全性：韌體安全的重要性以及開源韌體如何有助於提高其安全性能。這包括討論閉源韌體可能帶來的潛在安全風險以及開源韌體在緩解這些風險方面的作用。</li>
    <li>案例研究和專案展示：成功的開源韌體項目示例以及如何在自己的設備上運行它們。演講者將分享他們開發和使用開源韌體的經驗，以及對開源韌體項目的貢獻。</li>
    <li>新的發展方向：關於開源韌體的新專案和倡議，無論是技術上的（如軟體）還是組織上的（如本地社區、會議和標準化工作）。</li>
</ul>
<p>無論 CPU 架構或廠商如何，開源韌體專題都將接受 BIOS/UEFI、BMC 和嵌入式設備韌體的演講提案。我們將優先考慮項目和架構的多樣性，以確保涵蓋各種主題並具有吸引力。我們還會優先選擇獨立項目而非商業項目，以實現公平競爭。</p>
<p>我們相信，開源韌體專題將與 COSCUP 的現有系統軟體社區主題緊密結合，擴展到特定設備韌體的世界。</p>
'''
Track(pid='2023').save_track_description(
    track_id='8f762', lang='zh-tw', content=content.strip())

content = '''
<p>This track aims to host talks exploring the current state of the art and future directions of free and open source firmware development. Firmware, the low-level software that controls hardware devices, is often closed-source and proprietary, putting it at the frontier on our way to free and open computing.</p>
<p>The track will accept proposals for talks on a range of topics, including:</p>
<ul>
    <li>Overview of open source firmware development and introductory talks: The history and evolution of open source firmware, how it works, and the benefits of using open source firmware for hardware devices.</li>
    <li>Firmware security: The importance of firmware security and how open source firmware can help improve it. This includes discussing the potential security risks posed by closed-source firmware and the role of open source firmware in mitigating those risks.</li>
    <li>Case studies and project showcases: Examples of successful open source firmware projects and how to run them on your own devices. Speakers will share their experiences with developing and using open source firmware, as well as contributing to open source firmware projects.</li>
    <li>New directions and developments: New projects and initiatives with open source firmware, both technical (like software) and organizational (like local communities, conferences, and standardization efforts).</li>
</ul>
<p>The Open Source Firmware track will accept proposals for BIOS/UEFI, BMC, and embedded device firmware regardless of CPU architecture or vendor. We'll prioritize diversity of projects and architectures to ensure a wide variety of topics and appeal. We will also prefer independent projects over commercial ones to level the playing field.</p>
<p>We believe the Open Source Firmware track will fit well with COSCUP as it touches on the low-level topics of the existing System Software Community but expands into the world of device-specific firmware.</p>
'''
Track(pid='2023').save_track_description(
    track_id='8f762', lang='en', content=content.strip())
# ------

content = '''
<p>With Google Open Silicon project, we have final conquer to last mile of setting hardware free. 2 years ago, we have invited Google, QuickLogic and Efabless to talk about their ambition to set the toolchain and manufacturing "free." Last year, we have invited people who made their own chips/semiconductors. This year, we going to introduce you even more !</p>
'''
Track(pid='2023').save_track_description(
    track_id='38ecd', lang='en', content=content.strip())
# ------

content = '''
<p>我們期待看到有關 OpenStreetMap 或是其他開放內容有關的主題，例如維基媒體運動相關專案，維基百科、維基共享資源等等。</p>
<p>趁著每年台灣最大的開源大會 COSCUP，爭取更多開放資料計畫的曝光，廣邀各路 Wikidata、OpenStreetMap 以及 GIS 好手分享他們做的事情，增加台灣社群的活躍度。</p>
<p>OSM x Wikidata 徵求與開源地理資訊，或是 Wikidata 的議題：</p>
<ul>
    <li>OpenStreetMap 開放街圖，或是群眾參與的地理繪製計畫相關議題</li>
    <li>開源的GIS軟體，如 QGIS 介紹、教學操作、資料視覺化</li>
    <li>Wikidata 的介紹、各式專案應用與學術研討</li>
    <li>維基媒體相關的議題與專案，如維基百科、維基導遊等(但以與 Wikidata 相關從優錄取)</li>
</ul>
'''
Track(pid='2023').save_track_description(
    track_id='44109', lang='zh-tw', content=content.strip())

content = '''
<p>We are looking forward to topics related to OpenStreetMap, Wikidata, or other open content, such as Wikimedia movement projects, Wikipedia, Wiki Commons, etc.</p>
<p>During Taiwan's largest open source conference COSCUP, we hope to increase the exposure of open data projects and invite experts in Wikidata, OpenStreetMap, and GIS to share their experiences and increase the activity of Taiwan's community.</p>
<p>We are seeking talks related to OSM x Wikidata and open source geographic information, or Wikidata topics such as:</p>
<ul>
    <li>OpenStreetMap and related topics on crowd-sourced geographic mapping projects</li>
    <li>Introduction, tutorials, and data visualization of open-source GIS software such as QGIS</li>
    <li>Introduction to Wikidata, various project applications, and academic discussions</li>
    <li>Wikimedia-related topics and projects such as Wikipedia and Wikivoyage (but preference will be given to topics related to Wikidata)</li>
</ul>
'''
Track(pid='2023').save_track_description(
    track_id='44109', lang='en', content=content.strip())
# ------

content = '''
<p>各種有關於 PostgreSQL 的人事物經驗都歡迎分享。與 PostgreSQL 一起成長，和社群一同共好。</p>
'''
Track(pid='2023').save_track_description(
    track_id='11f15', lang='zh-tw', content=content.strip())

content = '''
<p>All kinds of experiences related to PostgreSQL are welcome to be shared. Let's grow together with PostgreSQL and contribute to the community.</p>
'''
Track(pid='2023').save_track_description(
    track_id='11f15', lang='en', content=content.strip())

# ------

content = '''
<p>想知道 PyCon TW 走過十幾個年頭的酸甜苦辣嗎？想聽聽厲害的講者分享 Python 相關的開發經驗嗎？我們即將在 COSCUP 與大家交流研討會舉辦秘辛，並邀請優秀的講者來與我們分享精彩演講！期待在 COSCUP 2023 與您相見！</p>
'''
Track(pid='2023').save_track_description(
    track_id='da80b', lang='zh-tw', content=content.strip())

content = '''
<p>Do you want to know the story of PyCon TW over the past decade? Are you curious about the development experience of Python experts? We’re going to invite speakers to give talks and share the secrets of the conference with everyone at COSCUP. We are looking forward to meeting you at COSCUP 2023!</p>
'''
Track(pid='2023').save_track_description(
    track_id='da80b', lang='en', content=content.strip())

# ------

content = '''
<p>主題包括 Ruby 語言、Rails 框架或任何相關的 framework，社群經營以及職涯經驗分享等。</p>
'''
Track(pid='2023').save_track_description(
    track_id='f951f', lang='zh-tw', content=content.strip())

content = '''
<p>The topic may include Ruby, Rails, related or alternative frameworks, community, diversity, indie-devs, mentorship, and career progression.</p>
<h4>Guidelines</h4>
<ul>
    <li>Topics can be technical or non-technical, from beginner to advanced, but should be aimed toward a Rubyist audience.</li>
    <li>Talks should be 30-35 minutes in length.</li>
    <li>Talks should be delivered in English or Chinese.</li>
</ul>
'''
Track(pid='2023').save_track_description(
    track_id='f951f', lang='en', content=content.strip())
# ------

content = '''
<p>Toolchain, compiler, runtime/library, firmware and operating system itself is the bone of the world. They are not fancy yet they are vital to let people develop and run applications upon them.</p>
'''
Track(pid='2023').save_track_description(
    track_id='b0fb0', lang='en', content=content.strip())

# ------

content = '''
<p>學生社群大亂鬥是由 SITCON 學生計算機年會與 Google Developer Student Clubs Taiwan & Hong Kong (GDSC) 組成的學生社群議程軌。作為學生展現自己的舞台，我們期待以學生為主體的稿件，例如：從學生角度出發的經驗分享、技術分享，專題研究成果、獨立研究甘苦談，或探討學生相關議題等等。</p>
<p>任何與資訊科技、電腦技術相關的講題，或是與 Google 技術、Google Developers 社群相關的投稿，我們都非常歡迎！歡迎您參考 SITCON 歷年的議程，或是 GDSC 去年的議程軌內容。</p>
'''
Track(pid='2023').save_track_description(
    track_id='67b43', lang='zh-tw', content=content.strip())

content = '''
<p>Students will bring a series of interesting adventure-themed presentations, including challenging their own skills, creative thinking and problem-solving abilities, as well as experiencing true teamwork spirit. These presentations will be shared by speakers who will share their experiences and skills, allowing students to enjoy the fun of adventure while learning.</p>
'''
Track(pid='2023').save_track_description(
    track_id='67b43', lang='en', content=content.strip())

# ------

content = '''
<p>原始碼是軟體的核心，藉由閱讀原始碼，我們可以更靠近軟體的靈魂。</p>
<p>「帶您讀源碼」議程軌旨在幫助參與者深入了解開源專案的實作方式，包括各種程式庫、框架和工具等。您將有機會學習開源專案的流程運作、架構組成、迭代歷程、運作原理、關鍵程式碼、關鍵演算法等方面的知識。同時，您還可以了解相關輔助工具的介紹和使用技巧。</p>
<p>在這個議程軌中，您可以聽到開發者們分享他們對程式碼的理解和經驗，看到他們追蹤和分析的過程。他們會與您分享程式碼中的精華部分，解釋如何運作，以及如何改進。</p>
<p>「帶您讀源碼」將帶您進入原始碼的世界，深入挖掘軟體背後的原理，讓您更加了解程式設計的本質。</p>
'''
Track(pid='2023').save_track_description(
    track_id='286e3', lang='zh-tw', content=content.strip())

content = '''
<p>The source code is the core of software, and by reading the source code, we can get closer to the soul of the software.</p>
<p>“Let's Read the Source Code” is a program track designed to help participants delve deeply into the implementation of open-source projects, including various libraries, frameworks, and tools. You will have the opportunity to learn about the process of open-source projects, their architectural components, iterative history, operating principles, key code, and key algorithms. At the same time, you can also learn about the introduction and usage tips of related auxiliary tools.</p>
<p>In this program track, you can listen to developers sharing their understanding and experience with code, as well as the process of tracking and analyzing it. They will share the essence of the code with you, explain how it works, and how to improve it.</p>
<p>“Let's Read the Source Code” will take you into the world of source code, deeply exploring the principles behind the software, allowing you to better understand the essence of programming.</p>
'''
Track(pid='2023').save_track_description(
    track_id='286e3', lang='en', content=content.strip())

# ------

content = '''
<p>一如往常的 COSCUP 一樣，如果您的主題找不到適合的議程軌投稿，您也可以提交 FLOSS 相關的稿件到綜合軌。歡迎分享任何與開放、開源等議題的內容，舉例來說，您想要探討開源合規、開源著作與法律、您所在的環境如何經營開放文化、或是您有開源專案要和大家分享，並希望號召更多投入開源的好朋友因為您的分享而吸引，都歡迎您投稿。</p>
'''
Track(pid='2023').save_track_description(
    track_id='f4231', lang='zh-tw', content=content.strip())

content = '''
<p>As always, you can submit FLOSS-related proposals even if your topic doesn’t fit in the tracks above.</p>
'''
Track(pid='2023').save_track_description(
    track_id='f4231', lang='en', content=content.strip())

# ------

content = '''
<p>本軌歡迎所有與人工智慧與開源的議題。包含且不限於</p>
<ol>
    <li>公開資料集的介紹與分享</li>
    <li>利用開源工具進行的 AI 研究</li>
    <li>您想推廣的 AI 專案</li>
    <li>AI 怎麼進行開源</li>
    <li>AI 開源的過去與未來展望</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='eebb8', lang='zh-tw', content=content.strip())

content = '''
<p>This track welcomes all topics related to artificial intelligence and open source. including but not limited to</p>
<ol>
    <li>Introduction and sharing of public datasets</li>
    <li>AI research using open source tools</li>
    <li>The AI project you want to promote</li>
    <li>How to open source AI</li>
    <li>The past and future of AI open source</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='eebb8', lang='en', content=content.strip())

# ------

content = '''
<p>這個社群議程軌以自由開源授權條款（以下直接簡稱為「條款」）為主軸，向外擴散開來，只要是與自由開源軟體或開放精神相關的授權法律議題都歡迎投稿。</p>
<p>以下列舉一些主題，提供給投稿者參考：</p>
<ol>
    <li>條款內容或焦點議題</li>
    <li>條款在實際應用上發生的問題與應對措施</li>
    <li>新興的焦點條款，例如木蘭系列許可證、開源 AI 相關條款等</li>
    <li>商業應用自由開源軟體所碰到的授權或其他周邊議題，例如 SPDX、Open Chain 等</li>
    <li>開放字型、開放文件等的授權內容或相關議題</li>
    <li>貢獻源碼、文件等內容給自由開源軟體專案所衍的授權議題，例如貢獻者條款 (Contributor License Agreement, CLA) 等</li>
    <li>自由開源軟體專案在管理運作上所遇到的法律相關問題</li>
</ol>
<p>最後，我們歡迎非法律背景的人投稿這個議程，因為第一線碰到開源授權議題與相關困難的大多不具有法律背景，這些有實際處理經驗的人，在個案上的了解深度遠超過其他人，所以無論你是法律人、開發者、 行銷管理專家或是一般的使用者，只要你有相關經歷或是研究，都歡迎加入投稿的行列！</p>
'''
Track(pid='2023').save_track_description(
    track_id='ea457', lang='zh-tw', content=content.strip())

content = '''
<p>All kind of topics related to Public Licenses, such as FOSS, CC, Open Data, or OpenRAIL licenses are welcome.</p>
<p>The core of this track is the FOSS license and the FOSS-related Public licenses. Any proposed issue or topic related to or derived from FOSS licenses is welcome to be submitted. For your reference is the following a list, which can give you some directions or ideas, what you can talk in this track. But please don't limit yourself in the list. You can submit any topic related to or derived from FOSS licenses.</p>
<ol>
    <li>Content of FOSS licenses or any related issues.</li>
    <li>Problems and the measures for resolving them.</li>
    <li>Latest relevant licenses,  such as Mulan series licenses, or AI related open source license.</li>
    <li>Issues rise during commercial use of FOSS, such as SPDX, Open Chain.</li>
    <li>Licenses or issues about open font, open document etc.</li>
    <li>Licensing issues derived from the contribution of FOSS projects, such as Contributor License Agreement (CLA).</li>
    <li>Legal related problems encountered in management of FOSS projects.</li>
</ol>
<p>You don't have to have any legal background to submit a proposal. In most cases, the people who encounter FOSS license problems don't possess any relating knowledge. But they do have unique insights or in-depth experiences towards their own cases. Therefore, no matter you are a legal person, an R&D engineer, a marketing professional, a management expert, or just an normal user, you all are welcome to submit a proposal.</p>
<p>Lastly, if the Creative Commons licenses are not suitable for your presentation slide or video recording, please contact us. We will find out how to deal with it.</p>
'''
Track(pid='2023').save_track_description(
    track_id='ea457', lang='en', content=content.strip())

# ------

content = '''
<p>本議程將聚焦於如何使開放知識運動更具備多元性。討論如何鼓勵代表性不足的群體投入維基媒體運動、如何使運動本身對多元價值更加友善、如何公平且妥善地配置資源，以及如何在尊重不同群體主題性的前題下，協調台灣的所有開放知識運動進程。</p>
'''
Track(pid='2023').save_track_description(
    track_id='94258', lang='zh-tw', content=content.strip())

content = '''
<p>This program will focus on how to make the open knowledge movement more diverse. It will discuss how to encourage underrepresented groups to participate in the Wikimedia movement, how to make the movement itself more friendly to diversity, how to allocate resources fairly and properly, and how to coordinate all open knowledge movements in Taiwan while respecting the thematic differences of different groups.</p>
'''
Track(pid='2023').save_track_description(
    track_id='94258', lang='en', content=content.strip())
# ------

content = '''
<p>持續讓更多人知道開放文化和科技，用它們來引領世界走向更美好的未來，一直是開放文化基金會的願景。我們希望透過新手村，把最基礎、最根本的開放原始碼、開放科技、開源理念帶給第一次到 COSCUP 或是第一次參與開源專案的夥伴。</p>
'''
Track(pid='2023').save_track_description(
    track_id='c834e', lang='zh-tw', content=content.strip())

content = '''
<p>Spreading awareness of open culture and technology and using them to lead the world towards a better future has always been the vision of the Open Culture Foundation. Through the "Newbie Village," we hope to bring the most fundamental concepts of open source, open technology, and open culture to those who are attending COSCUP for the first time or are participating in an open source project for the first time.</p>
'''
Track(pid='2023').save_track_description(
    track_id='c834e', lang='en', content=content.strip())
# ------

content = '''
<p>本軌歡迎討論開源為你的職涯帶來什麼樣的影響與成長，歡迎且不限於以下主題：</p>
<ol>
    <li>技術成長：分享影響您覺得超棒的開源學習教材，讓您自身技術得到成長，或是點了新的技能樹，應用在工作或是求職中！</li>
    <li>開源工具：透過開源工具，為你的工作帶來不同的改變，如效率上的提升，或是團隊的合作等議題</li>
    <li>開創事業：利用開源工具展開新的事業可能性，或是自身透過開源進行創業的經驗分享</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='2e81b', lang='zh-tw', content=content.strip())

content = '''
<p>This track discusses career growth and open source. Including but not limited to</p>
<ol>
    <li>Technological growth</li>
    <li>Open source tools</li>
    <li>Start a business</li>
</ol>
'''
Track(pid='2023').save_track_description(
    track_id='2e81b', lang='en', content=content.strip())

# ------

content = '''
<p>歡迎 Google Kubernetes Engine 相關議題包括:</p>
<ul>
    <li>Android/Java/Kotlin</li>
    <li>Google Cloud</li>
    <li>Flutter</li>
    <li>Google Assistant (AOG)</li>
    <li>TensorFlow</li>
    <li>WTM</li>
</ul>
'''
Track(pid='2023').save_track_description(
    track_id='ef371', lang='zh-tw', content=content.strip())

content = '''
<p>Welcome Google Kubernetes Engine related topics, such as:</p>
<ul>
    <li>Android/Java/Kotlin</li>
    <li>Google Cloud</li>
    <li>Flutter</li>
    <li>Google Assistant (AOG)</li>
    <li>TensorFlow</li>
    <li>WTM</li>
</ul>
'''
Track(pid='2023').save_track_description(
    track_id='ef371', lang='en', content=content.strip())

# ------

content = '''
<p>此徵稿議題設立目的是希望能集結社群及產官學界無線存取網路（RAN）、B5G/6G和軟體定義網路（SDN）相關的開放網路技術研究者及愛好者一起交流！可能適合這個議題的講題包括：</p>
<ul>
	<li>O-RAN 的開源專案及實作</li>
	<li>O-RAN 的虛擬化和自動化部署</li>
	<li>O-RAN 智慧控制器（RIC）</li>
	<li>O-RAN 的協議優化</li>
	<li>O-RAN 的物理層加速</li>
	<li>O-RAN 的軟體安全性</li>
	<li>O-RAN 軟體社群（OSC）和 O-RAN 聯盟的最新發展</li>
	<li>6G 的開放網路架構原型系統</li>
	<li>開發開放的 6G 原型系統</li>
	<li>測試和測量未來開放的 6G 系統功能技術</li>
	<li>開放 6G 用例的早期驗證</li>
	<li>在開放 6G 技術領域中的通訊人才培養</li>
	<li>B5G/6G 中與 O-RAN 相關的雲端技術</li>
	<li>開源 SDN 技術</li>
</ul>
<p>歡迎對以上議題有心得的朋友投稿交流，其他跟開源 O-RAN/B5G/6G 相關的主題也同樣歡迎共襄盛舉！</p>

<p>This issue is focused on open network technologies related to Radio Access Network (RAN), B5G/6G, and software-defined networking (SDN). Potential topics that may fit this issue include:</p>
'''
Track(pid='2023').save_track_description(
    track_id='43d00', lang='zh-tw', content=content.strip())

content = '''
<p>This issue is focused on open network technologies related to Radio Access Network (RAN), B5G/6G, and software-defined networking (SDN). Potential topics that may fit this issue include:</p>
<ul>
	<li>Open RAN open source projects and implementations</li>
	<li>Open RAN virtualization and automatic deployment</li>
	<li>Open RAN intelligent controller (RIC)</li>
	<li>Protocol optimization for Open RAN</li>
	<li>Physical layer acceleration for Open RAN</li>
	<li>Software security for Open RAN</li>
	<li>The latest development of the O-RAN Software Community (OSC) and O-RAN Alliance</li>
	<li>Open network architecture prototype systems for 6G</li>
	<li>Development of Open 6G prototype systems</li>
	<li>Testing and measurement of future Open 6G system functional technologies</li>
	<li>Early-stage verification of Open 6G use cases</li>
	<li>Communication talent cultivation in the field of Open 6G technology</li>
	<li>Cloud technologies related to O-RAN in B5G/6G</li>
	<li>Open SDN technologies</li>
</ul>
<p>These topics are aligned with the aim of developing key enabling software technologies for open network technologies and establishing forward-looking research for 6G technology. Other relevant topics related to O-RAN/B5G/6G can also be considered-.</p>
'''
Track(pid='2023').save_track_description(
    track_id='43d00', lang='en', content=content.strip())

# ------

content = '''
<p>Chatbot Developers Taiwan 社群致力於提供一個討論聊天機器人的相關應用的社群。在台北、台中每個月皆有一次的定期 meetup 聚會，每回小聚都會安排講者主題分享、新知討論，環繞在 chatbot 與 AI ，及大家共同關心的話題中。歡迎大家踴躍分享、自由與會眾交流，也期望大家可以在分享中得到收穫。 同時，也很歡迎各位自薦、推薦講者。亦或者是上台閃電秀，分享自己開發的 chatbot 或是任何 chatbot 有關的任何議題。</p>
'''
Track(pid='2023').save_track_description(
    track_id='74574', lang='zh-tw', content=content.strip())

content = '''
<p>Chatbot Developers Taiwan Community is dedicated to providing a platform for discussing chatbot-related applications. We hold regular meetups in Taipei and Taichung every month, featuring guest speakers and discussions on the latest developments and topics related to chatbots and AI. We welcome everyone to actively participate in sharing and exchanging ideas, and hope that everyone can benefit from these events. We also welcome recommendations for speakers, lightning talks, and sharing any chatbot-related topics, including your own chatbot development experiences.</p>
'''
Track(pid='2023').save_track_description(
    track_id='74574', lang='en', content=content.strip())

# ------

content = '''
<p>本議程邀請日本的開源社群 OSPN (Open Source People Network) 的講者，來分享日本開源相關議題的現況，並和 COSCUP 會眾進行國際交流。</p>
'''
Track(pid='2023').save_track_description(
    track_id='2ae73', lang='zh-tw', content=content.strip())

content = '''
<p>In this track, speakers from OSPN (Open Source People Network) Japan will present the newest open source related topics in Japan. The speakers are willing to share, to communicate and to interact with COSCUP attendees.</p>
<p>このトラックでは、OSPN（Open Source People Network）Japan のスピーカーの方々が日本で最新のオープンソース関連トピックを紹介します。COSCUPの参加者と情報共有し、コミュニケーションを図り、交流することを望みます。</p>
'''
Track(pid='2023').save_track_description(
    track_id='2ae73', lang='en', content=content.strip())

# ------

content = '''
<p>想知道 PyCon TW 走過十幾個年頭的酸甜苦辣嗎？想聽聽厲害的講者分享 Python 相關的開發經驗嗎？我們即將在 COSCUP 與大家交流研討會舉辦秘辛，並邀請優秀的講者來與我們分享精彩演講！期待在 COSCUP 2023 與您相見！</p>
'''
Track(pid='2023').save_track_description(
    track_id='e28f8', lang='zh-tw', content=content.strip())

content = '''
<p>Do you want to know the story of PyCon TW over the past decade? Are you curious about the development experience of Python experts? We’re going to invite speakers to give talks and share the secrets of the conference with everyone at COSCUP. We are looking forward to meeting you at COSCUP 2023!</p>
'''
Track(pid='2023').save_track_description(
    track_id='e28f8', lang='en', content=content.strip())

# ------
content = '''
<p>所有 Rust 相關開源議題。</p>
'''
Track(pid='2023').save_track_description(
    track_id='fda3f', lang='zh-tw', content=content.strip())

content = '''
<p>all open source topics related to Rust.</p>
'''
Track(pid='2023').save_track_description(
    track_id='fda3f', lang='en', content=content.strip())

# ------

content = '''
<p>Laravel Taiwan 和 Vue Taiwan 都是由熱愛相應技術的社群成員共同創立的社群，旨在提供對於 Laravel 和 Vue.js 相關議題、專案、技術以及工作的朋友們進行分享與交流的平台。去年與前年，兩個社群更攜手舉辦了 {Laravel x Vue} Conf Taiwan，廣邀各界技術高手前來共襄盛舉，希望能為技術愛好者打造一個良好的學習和交流環境。希望透過本次Coscup的社群議程與攤位，進行相關技術的推廣與分享。</p>
'''
Track(pid='2023').save_track_description(
    track_id='f194d', lang='zh-tw', content=content.strip())

content = '''
<p>Laravel Taiwan and Vue Taiwan are both communities founded by members who love the respective technologies, aiming to provide a platform for sharing and exchanging ideas related to Laravel and Vue.js, including topics, projects, techniques, and jobs. In the past two years, the two communities joined forces to hold {Laravel x Vue} Conf Taiwan, inviting experts from various fields to come and join the event, hoping to create a good learning and communication environment for technology enthusiasts. Through the community schedule and booth at this year's Coscup, we hope to promote and share related technologies.</p>
'''
Track(pid='2023').save_track_description(
    track_id='f194d', lang='en', content=content.strip())

# ------

content = '''
<p>我們好奇科技領域內的多元聲音，以及人們如何促進科技領域的開放共榮。我們關注職場安全、性別平等、多元文化，題目可包含（但不限）女性在職場環境裡如何突破職場的性別歧視、多元性別在科技領域裡的困境與復原力、貧富差距如何造就資訊差異及其補救措施⋯⋯等等。我們好奇的是，當人內心懷抱正義與理想時，要如何在舊有的不正義社會輪帶中脫離，又如何真正地行動與自我賦能。 </p>
'''
Track(pid='2023').save_track_description(
    track_id='5133e', lang='zh-tw', content=content.strip())

content = '''
<p>We are curious about the diverse voices in the field of technology and how people can promote openness and mutual prosperity in this area. We are concerned with workplace safety, gender equality, and multiculturalism. Possible topics may include (but are not limited to) how women can overcome gender discrimination in the workplace, the challenges and resilience of gender diversity in the technology field, how wealth disparity leads to information discrepancies and its remedies, and so on. We are curious about how individuals can break away from the unjust social system and take real action and self-empowerment when they hold justice and ideals in their hearts.</p>
'''
Track(pid='2023').save_track_description(
    track_id='5133e', lang='en', content=content.strip())

# ------

content = '''
<p>近年來胎玩有許多組織的型態並非單一的藝術組織，而是透過議題是的發生，結合各種不同領域的專業，進行對社會的提問，促使社會的各種面向被看見。這些組織特性以及目的皆不同，我們究竟應不應該定義組織的核心？又或者我們在進行跨域對話的時候，如何先從理解對方語言，在試著把自己的專業讓彼此了解，進而擴大各種可能性。若我們希望擴及各大的知識層面，促使更多人加入相關領域的研究和政策的推進，『開放』究竟是什麼？應該怎麼做？</p>
'''
Track(pid='2023').save_track_description(
    track_id='a3683', lang='zh-tw', content=content.strip())

content = '''
<p>In recent years, there have been many organizations in Taiwan that are not simply art organizations, but rather bring together professionals from various fields through issue-based events to raise questions and bring different aspects of society to light. These organizations have different characteristics and purposes, but should we define the core of these organizations? And in cross-disciplinary dialogues, how can we first understand each other's language, try to make our own expertise understood, and expand possibilities? If we hope to reach various knowledge levels and encourage more people to participate in related fields of research and policy promotion, what exactly is "openness" and how should we approach it?</p>
'''
Track(pid='2023').save_track_description(
    track_id='a3683', lang='en', content=content.strip())

# ------

content = '''
<p>開放教育議程軌，期望透過議程分享進一步探討有關開放教育資源（Open Education Resources）與開源教育（Open Source Education）等，和開放與教育相關的議題，從開放式課程、教材到開源貢獻者的培育與傳承等。我議程主題包含但不限於：</p>
<ul>
	<li>如何培育下一代開源貢獻者</li>
	<li>藉由 FLOSS 專案進行課程規劃的分享</li>
	<li>開放式課程與開放教育教材的使用者分析</li>
	<li>與教育有關的開源社群籌辦或參與經驗</li>
	<li>FLOSS 概念及開源精神在教育現場的應用情境</li>
</ul>
'''
Track(pid='2023').save_track_description(
    track_id='fecd1', lang='zh-tw', content=content.strip())

content = '''
<p>The Open Education track aims to further explore topics related to Open Education Resources and Open Source Education through sharing sessions. Including discussions on issues related to open education, from open courses and education resources to the training and continuation of open source contributors. session topics have included, but are not limited to:</p>
<ul>
	<li>How to educate the next generation of open source contributors</li>
	<li>Planning of FLOSS project related courses</li>
	<li>User analysis of open course platforms and open educational resourses</li>
	<li>Experiences in hosting or participating in open source communities related to education</li>
	<li>The usage of FLOSS and open source concept in different educational scenarios.</li>
</ul>
'''
Track(pid='2023').save_track_description(
    track_id='fecd1', lang='en', content=content.strip())

# ------
