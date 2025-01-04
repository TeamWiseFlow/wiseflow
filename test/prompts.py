
get_info_system = '''你将被给到一段使用<text></text>标签包裹的网页文本，你的任务是从前到后仔细阅读文本，并提取出所有与如下关注点之一相关的部分。关注点列表及其解释如下：

{focus_statement}\n
在进行提取时，请遵循以下原则：
- 理解每个关注点的含义以及进一步的解释（如有），确保提取的内容与关注点强相关并符合解释（如有）的范围
- 有必要的话，可以连同相关的上下文一并提取，从而保证提取出的内容信息完备、意思完整'''

get_info_suffix = '''如果网页文本中包含关注点相关的部分，请按照以下json格式输出：
"""{"focus": 关注点, "content": 提取的内容}"""

如果有多个相关部分，请逐条输出，每一条都用三引号包裹，三引号内不要有其他内容。'''

text_info_system = '''你将被给到一段使用<text></text>标签包裹的网页文本，请分别按如下关注点对网页文本提炼摘要。关注点列表及其解释如下：

{focus_statement}\n
在提炼摘要时，请遵循以下原则：
- 理解每个关注点的含义以及进一步的解释（如有），确保摘要与关注点强相关并符合解释（如有）的范围
- 摘要应当详实、充分
- 摘要信息务必忠于原文'''

text_info_suffix = '''请对关注点逐一生成摘要，不要遗漏任何关注点，如果网页文本与关注点无关，可以对应输出"NA"。输出结果整体用三引号包裹，三引号内不要有其他内容。如下是输出格式示例：
"""
//关注点1//
摘要1
//关注点2//
摘要2
//关注点3//
NA
...
"""'''

text_link_system = '''你将被给到数行格式为"<编号>//内容//"的文本，你的任务是逐条分析这些文本，并分别与如下关注点之一相关联。关注点列表及其解释如下：

{focus_statement}\n
在进行关联分析时，请遵循以下原则：

- 理解每个关注点的含义
- 如果关注点有进一步的解释，确保提取的内容符合这些解释的范围'''

text_link_suffix = '''请分行逐条输出结果，每一条的输出格式为"<编号>//关注点名称//"，如果某条内容不与任何关注点相关，请输出"<编号>//NA//"。输出结果整体用三引号包裹，三引号内不要有其他内容。如下是输出格式示例：
"""
<t1>//关注点1名称//
<t2>//关注点2名称//
<t3>//NA//
...
"""'''

text_ap_system = "As an information extraction assistant, your task is to accurately extract the source (or author) and publication date from the given webpage text. It is important to adhere to extracting the information directly from the original text. If the original text does not contain a particular piece of information, please replace it with NA"
text_ap_suffix = '''Please output the extracted information in the following format(output only the result, no other content):
"""source or article author (use "NA" if this information cannot be extracted)//extracted publication date (keep only the year, month, and day; use "NA" if this information cannot be extracted)"""'''


verified_system = '''判断给定的信息是否与网页文本相符。信息将用标签<info></info>包裹，网页文本则用<text></text>包裹。请遵循如下工作流程:
1、尝试找出网页文本中所有与信息对应的文本片段（可能有多处）；
2、基于这些片段给出是否相符的最终结论，最终结论仅为“是”或“否”'''
verified_suffix = '先输出找到的所有文本片段，再输出最终结论（仅为是或否）'


image_info_system = '''作为信息提取助手，你的任务是从给定的网页截屏中提取与以下用户兴趣点相关的内容。兴趣点列表及其解释如下：

{focus_statement}\n
在进行信息提取时，请遵循以下原则：

- 理解每个兴趣点的含义，确保提取的内容与之相关。
- 如果兴趣点有进一步的解释，确保提取的内容符合这些解释的范围。
- 忠于原文，你的任务是从网页截屏中识别和提取与各个兴趣点相关的信息，并不是总结和提炼。'''

image_info_suffix = '''如果网页截屏中包含兴趣点相关的内容，请按照以下json格式输出提取的信息（文本中可能包含多条有用信息，请不要遗漏）：
[{"focus": 兴趣点名称, "content": 提取的内容}]

示例：
[{"focus": "旅游景点", "content": "北京故宫，地址：北京市东城区景山前街4号，开放时间：8:30-17:00"}, {"focus": "美食推荐", "content": "来王府井小吃街必吃北京烤鸭、炸酱面"}]

如果截屏中不包含任何与兴趣点相关的信息或者你判断这是一个文章列表页面，请仅输出：[]。'''

image_link_system = "作为一位高效的信息筛选助手，你的任务是根据给定的兴趣点，从给定的网页截屏中挑选出最值得关注的链接推荐给用户进一步点击查看。兴趣点及其解释如下：\n\n{focus_statement}"
image_link_suffix = '''只要输出值得关注的链接对应的文本文字即可。按一行一条的格式输出，最终输出的列表整体用三引号包裹，三引号内不要有其他内容，如下是输出格式示例：
"""
链接文字1
链接文字2
...
"""'''

image_ap_system = "As an information extraction assistant, your task is to accurately extract the source (or author) and publication date from the given webpage screenshot. If the screenshot does not contain a particular piece of information, please replace it with NA"
image_ap_suffix = '''Please output the extracted information in the following JSON format:
{"source": source or article author (use "NA" if this information cannot be found), "publish_date": publication date (keep only the year, month, and day; use "NA" if this information cannot be found)}'''

image_system = "提取图片中的所有文字，如果图片不包含文字或者文字很少或者你判断图片仅是网站logo、商标、图标等，则输出NA。注意请仅输出提取出的文字，不要输出别的任何内容。"
image_system_en = "Extract all text from the image. If the image does not contain any text or contains very little text or you determine that the image is only a logo, trademark, or icon, output NA. Note that you should only output the extracted text, and do not output any other content."
