# 公开仓库用：去掉内网端口表等安全敏感段落（本机原件不动）
import re, pathlib
p = pathlib.Path('天气预报_AIWeatherStudio/调查/B_sons02调查.md')
s = p.read_text(encoding='utf-8')
s2 = re.sub(r'## 7\. 端口占用.*?(?=\n## 8\.)', '## 7. 端口占用\n\n（公开仓库里删去了内网端口和服务清单，原件在本机。）\n', s, flags=re.S)
p.write_text(s2, encoding='utf-8')
print('redacted' if s2 != s else 'no-change')
