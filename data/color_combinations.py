import re
combs_str = """
#00539C, #EEA47F
#2F3C7E, #FBEAEB
#101820, #FEE715
#F96167, #FCE77D
#CCF381, #4831D4
#E2D1F9, #317773
#990011, #FCF6F5
#8AAAE5, #FFFFFF
#FF69B4, #00FFFF
#FCEDDA, #EE4E34
#ADD8E6, #00008b
#89ABE3, #EA738D
#EC449B, #99F443
#8A307F, #79A7D3
#CC313D, #F7C5CC
#AA96DA, #C5FAD5
#2BAE66, #FCF6F5
#033E3E, #FCC1C1
#FFE77A, #2C5F2D
#201E20, #E0A96D
#234E70, #FBF8BE
#408EC6, #1E2761
#B85042, #E7E8D1
#B85042, #A7BEAE
#ef8a62, #67a9cf
#F1A340, #998EC3
#EFA3C9, #A1D76A
#AF8DC3, #7FBF7B
#4286F4, #E29922
#111111, #EEEEEE
"""

pattern = re.compile(
r"#([a-zA-Z0-9]{6}), #([a-zA-Z0-9]{6})"
)

COLOR_COMBINATIONS = pattern.findall(combs_str)
