
get_link_system = '''你将被给到一段使用<text></text>标签包裹的网页文本，你的任务是从前到后仔细阅读文本，提取出与如下任一关注点相关的原文片段。关注点及其解释如下：

{focus_statement}\n
在进行提取时，请遵循以下原则：
- 理解关注点的含义以及进一步的解释（如有），确保提取的内容与关注点强相关并符合解释（如有）的范围
- 在满足上面原则的前提下，提取出全部可能相关的片段
- 提取出的原文片段务必保留类似"[3]"这样的引用标记，后续的处理需要用到这些引用标记'''

get_link_suffix = '''请逐条输出提取的原文片段，并整体用三引号包裹。三引号内除了提取出的原文片段外不要有其他内容，如果文本中不包含任何与关注点相关的内容则保持三引号内为空。
如下是输出格式示例：：
"""
原文片段1
原文片段2
...
"""'''

get_link_system_en = '''You will be given a webpage text wrapped in <text></text> tags. Your task is to carefully read the text from beginning to end, extracting fragments related to any of the following focus points. The focus points and their explanations are as follows:

{focus_statement}\n
When extracting fragments, please follow these principles:
- Understand the meaning of each focus point and its explanation (if any), ensure the extracted content strongly relates to the focus point and aligns with the explanation (if any)
- Extract all possible related fragments
- Ensure the extracted fragments retain the reference markers like "[3]", as these will be used in subsequent processing'''

get_link_suffix_en = '''Please output each extracted fragment one by one, and wrap the entire output in triple quotes. The triple quotes should contain only the extracted fragments, with no other content. If the text does not contain any content related to the focus points, keep the triple quotes empty.
Here is an example of the output format:
"""
Fragment 1
Fragment 2
...
"""'''

get_info_system = '''你将被给到一段使用<text></text>标签包裹的网页文本，请分别按如下关注点对网页文本提炼摘要。关注点列表及其解释如下：

{focus_statement}\n
在提炼摘要时，请遵循以下原则：
- 理解每个关注点的含义以及进一步的解释（如有），确保摘要与关注点强相关并符合解释（如有）的范围
- 摘要应当详实、充分，且绝对忠于原文
- 如果摘要涉及的原文片段中包含类似"[3]"这样的引用标记，务必在摘要中保留相关标记'''

get_info_suffix = '''请对关注点逐一生成摘要，不要遗漏任何关注点，如果网页文本与关注点无关，可以对应输出"NA"。输出结果整体用三引号包裹，三引号内不要有其他内容。如下是输出格式示例：
"""
//关注点1//
摘要1
//关注点2//
摘要2
//关注点3//
NA
...
"""'''

get_info_system_en = '''You will be given a webpage text wrapped in <text></text> tags. Please extract summaries from the text according to the following focus points. The list of focus points and their explanations are as follows:

{focus_statement}\n
When extracting summaries, please follow these principles:
- Understand the meaning of each focus point and its explanation (if any), ensure the summary strongly relates to the focus point and aligns with the explanation (if any)
- The summary should be detailed and comprehensive and absolutely faithful to the original text
- If the summary involves a reference marker like "[3]", it must be retained in the summary'''

get_info_suffix_en = '''Please generate summaries for each focus point, don't miss any focus points. If the webpage text is not related to a focus point, output "NA" for that point. The entire output should be wrapped in triple quotes with no other content inside. Here is an example of the output format:
"""
//Focus Point 1//
Summary 1
//Focus Point 2//
Summary 2
//Focus Point 3//
NA
...
"""'''

get_ap_system = "As an information extraction assistant, your task is to accurately extract the source (or author) and publication date from the given webpage text. It is important to adhere to extracting the information directly from the original text. If the original text does not contain a particular piece of information, please replace it with NA"
get_ap_suffix = '''Please output the extracted information in the following format(output only the result, no other content):
"""source or article author (use "NA" if this information cannot be extracted)//extracted publication date (keep only the year, month, and day; use "NA" if this information cannot be extracted)"""'''
