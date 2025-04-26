import re

from defaults import YOUTUBE_PATTERNS


def is_link_a_youtube_link(text):
	for pattern in YOUTUBE_PATTERNS:
		if re.search(pattern, text):
			return True
	return False


def extract_youtube_links_from_text(text):
	links = []
	for pattern in YOUTUBE_PATTERNS:
		matches = re.finditer(pattern, text)
		for match in matches:
			links.append(match.group(0))
	return links


def is_link_from_seyed_ecosystem(title) -> bool:
	seyed_keywords = ["سید", "فرندز", "رفقا"]
	for keyword in seyed_keywords:
		if keyword in title.lower():
			return True
	return False
