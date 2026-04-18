import re

content = open(r'D:\Work\NovelAS-Universal\projects\SRNR\chapters\vol2\Interlude.002.md', 'r', encoding='utf-8').read()

# First restore all 「 back to " to get clean state
content = content.replace('「', '"')
content = content.replace('」', '"')

# Now convert "text" pairs to 「text」
# This regex matches " followed by non-" chars followed by "
content = re.sub(r'"([^"]+)"', r'「\1」', content)

open(r'D:\Work\NovelAS-Universal\projects\SRNR\chapters\vol2\Interlude.002.md', 'w', encoding='utf-8').write(content)
print('Done')
