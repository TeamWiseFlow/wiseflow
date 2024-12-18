
text_info_system = '''作为信息提取助手，你的任务是从给定的网页文本中提取与以下用户兴趣点相关的内容。兴趣点列表及其解释如下：

{focus_statement}\n
在进行信息提取时，请遵循以下原则：

- 理解每个兴趣点的含义，确保提取的内容与之相关。
- 如果兴趣点有进一步的解释，确保提取的内容符合这些解释的范围。
- 忠于原文，你的任务是从网页文本中识别和提取与各个兴趣点相关的信息，并不是总结和提炼。

另外请注意给定的网页文本是通过爬虫程序从html代码中提取出来的，所以请忽略里面不必要的空格、换行符等。'''

text_info_suffix = '''如果上述网页文本中包含兴趣点相关的内容，请按照以下json格式输出提取的信息（文本中可能包含多条有用信息，请不要遗漏）：
[{"focus": 兴趣点名称, "content": 提取的内容}]

示例：
[{"focus": "旅游景点", "content": "北京故宫，地址：北京市东城区景山前街4号，开放时间：8:30-17:00"}, {"focus": "美食推荐", "content": "来王府井小吃街必吃北京烤鸭、炸酱面"}]

如果网页文本中不包含任何与兴趣点相关的信息，请仅输出：[]。'''

text_link_system = '''作为一位高效的信息筛选助手，你将被给到一组链接对应的文本，请从中挑选出跟兴趣点有关的文本。兴趣点及其解释如下：\n\n{focus_statement}\n
在进行信息提取时，请遵循以下原则：

- 理解每个兴趣点的含义，确保提取的文本与之相关。
- 如果兴趣点有进一步的解释，确保提取的文本符合这些解释的范围。'''

text_link_suffix = '''请一步步思考，最终将挑选出的文本按一行一条的格式输出，并整体用三引号包裹，三引号内不要有其他内容，如下是输出格式示例：
"""
文本1
文本2
...
"""'''

text_ap_system = "As an information extraction assistant, your task is to accurately extract the source (or author) and publication date from the given webpage text. It is important to adhere to extracting the information directly from the original text. If the original text does not contain a particular piece of information, please replace it with NA"
text_ap_suffix = '''Please output the extracted information in the following JSON format:
{"source": source or article author (use "NA" if this information cannot be extracted), "publish_date": extracted publication date (keep only the year, month, and day; use "NA" if this information cannot be extracted)}'''


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

如果截屏中不包含任何与兴趣点相关的信息，请仅输出：[]。'''

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

