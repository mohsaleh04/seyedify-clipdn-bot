import re

from defaults import YOUTUBE_PATTERNS, INSTAGRAM_PATTERNS, LinkType


def is_message_contains_a_social_link(text: str) -> bool:
	for pattern in YOUTUBE_PATTERNS:
		if re.search(pattern, text):
			return True
	for pattern in INSTAGRAM_PATTERNS:
		if re.search(pattern, text):
			return True
	return False


def extract_social_links_from_text(text: str) -> tuple:
	ltype = LinkType.YOUTUBE.value
	links = _link_extractor(text, YOUTUBE_PATTERNS)
	if not links:
		ltype = LinkType.INSTAGRAM.value
		links = _link_extractor(text, INSTAGRAM_PATTERNS)
	return ltype, links


def _link_extractor(text: str, valid_patterns: list[str]):
	links = []
	for pattern in valid_patterns:
		matches = re.finditer(pattern, text)
		for match in matches:
			links.append(match.group(0))
	return links


def is_link_from_seyed_ecosystem_groups(title) -> bool:
	seyed_keywords = ["سید", "فرندز", "رفقا"]
	for keyword in seyed_keywords:
		if keyword in title.lower():
			return True
	return False
