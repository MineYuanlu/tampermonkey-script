class BuildInfo:
    """构建信息"""

    def __init__(self,
                 name="",
                 namespace="",
                 version="",
                 description="",
                 author="",
                 **other: "dict[str,str]"
                 ):
        self.info = {
            "@name": name,
            "@namespace": namespace,
            "@version": version,
            "@description": description,
            "@author": author,
        }
        self.default_info = {
            "@name": "",
            "@namespace": "bid.yuanlu",
            "@version": "",
            "@description": "",
            "@author": "yuanlu",
        }
        for k, v in other.items():
            if not k.startswith('@'):
                k = f"@{k}"
            k = k.replace("_", ":")
            self.info[k] = v

    def get_info(self, tag, locale="") -> str:
        if locale:
            locale = f"{tag}:{locale}"
            locale = self.get_info(locale)
            if locale:
                return locale
        if tag in self.info and self.info[tag]:
            return self.info[tag]
        elif tag in self.default_info and self.default_info[tag]:
            return self.default_info[tag]
        else:
            return ""


class Require:
    """引用预设"""

    def __init__(self,
                 *urls,
                 jquery=False,
                 ):
        req = []
        if jquery:
            req.append['https://code.jquery.com/jquery-latest.js']

        req.extend(urls)

        self.require = req
