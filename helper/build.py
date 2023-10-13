from datetime import datetime
import importlib.util
import os
import sys
import shutil


try:
    root_dir = os.path.dirname(os.path.dirname(__file__))
    src_dir = os.path.join(root_dir, "src")
    sys.path.append(root_dir)
    from helper.defs import *
    from helper.git_manager import get_lst_file
except Exception as e:
    raise e


class TamperScript:
    def __init__(self, desc: "list[tuple[str,str]]", lines: "str|list[str]") -> None:
        self.desc = desc
        self.lines = lines if isinstance(lines, list) else lines.split('\n')
        self.lines = [line[:-2] if line.endswith('\r\n')
                      else line[:-1] if line.endswith('\n')
                      else line
                      for line in self.lines]
        a = 1

    def save(self, path: str):
        """保存脚本数据"""
        with open(path, 'w+') as f:
            f.write('// ==UserScript==\n')
            f.writelines([f"// {k}{' '*max(1,15-len(k))}{v}\n"for k, v in self.desc])
            f.write('// ==/UserScript==\n\n\n')
            f.writelines([f"{line}\n"for line in self.lines])

    def get_version(self):
        for k, v in self.desc:
            if k == '@version':
                return v
        return None

    def set_version(self, version):
        for i, (k, v) in enumerate(self.desc):
            if k == '@version':
                self.desc[i] = (k, version)
                return
        self.desc.append(('@version', version))

    def equals_without_version(self, other: "TamperScript|None"):
        if not other or not isinstance(other, TamperScript):
            return False
        if self.lines != other.lines:
            return False

        if len(self.desc) != len(other.desc):
            return False

        for (sk, sv), (ok, ov) in zip(self.desc, other.desc):
            if sk != ok:
                return False
            if sk == '@version':
                continue
            if sv != ov:
                return False
        return True


def load_module_info_file(info, *Types):
    """加载模块的信息文件"""
    info = info[0], os.path.join(info[1], 'info.py')
    module_spec = importlib.util.spec_from_file_location(*info)
    if module_spec is None:
        raise f"[info_file] [{info[0]}] 无法找到 {info[1]}"
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    Values = [None] * len(Types)
    for key in module.__dir__():
        if key.startswith("_"):
            continue
        val = getattr(module, key)
        for i, ty in enumerate(Types):
            if isinstance(val, ty):
                Values[i] = val
    return Values


def get_infos():
    """加载所有模块信息"""
    module_infos = [
        (sub, os.path.join(src_dir, sub))
        for sub in os.listdir(src_dir)
        if os.path.isdir(os.path.join(src_dir, sub))
    ]
    module_infos = [
        (*info, *load_module_info_file(info, BuildInfo, Require))
        for info in module_infos
    ]
    return module_infos


def build_single(name: str, path: str,
                 build_info: BuildInfo, require: Require):
    """构建单一脚本"""
    def error(*infos):
        info = " ".join(infos)
        raise Exception(f"[build_single] [{name}] {info}")

    if build_info is None:
        error("缺失构建信息")

    files = [name for l, name in [(n.lower(), n)for n in os.listdir(path)]
             if ("index" in l or "main" in l)
             and (l.endswith(".js") or l.endswith('.ts'))]
    if len(files) > 1:
        error("找到多个脚本文件:", *files)
    elif len(files) == 1:
        src_script = os.path.join(path, files[0])
    else:
        error("找不到脚本文件")

    dst_dir = os.path.join(root_dir, "build", name)
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    os.makedirs(dst_dir)
    dst_script = os.path.join(dst_dir, "index.js")
    if src_script.endswith(".ts"):
        ts2js(src_script, dst_script)
        src_script = dst_script

    build_info.default_info['@name'] = name
    lst_file = parse_js(get_lst_file(os.path.relpath(dst_script, root_dir)))
    new_file = summon_js(src_script, build_info, require)

    new_version = get_new_version(lst_file, new_file, build_info)
    new_file.set_version(new_version)
    new_file.save(dst_script)

    build_readme(new_file, dst_dir, path, build_info, require)


def build_readme(script: "TamperScript", dst_dir: str, src_dir: str,
                 bi: BuildInfo, require: Require):
    """构建README文件"""
    prefix, suffix = "readme", ".md"

    def summon_readme(filename="README.md", locale="", append=""):
        name = bi.get_info("@name", locale)
        ns = bi.get_info("@namespace", locale)
        desc = bi.get_info("@description", locale)
        author = bi.get_info("@author", locale)
        v = script.get_version()
        auto = f"# {name}  \n> {ns}\n> author: {author}\n> version: {v}\n\n__{desc}__\n"
        append = f"\n{append}" if append else ""
        with open(os.path.join(dst_dir, filename), "w+") as f:
            f.writelines([auto, append])

    no_readme = True
    for filename in os.listdir(src_dir):
        l = filename.lower()
        if not l.startswith(prefix) or not l.endswith(suffix):
            continue
        locale = l[len(prefix):-len(suffix)]
        if locale and not ('a' <= locale[0] <= 'z'):
            locale = locale[1:]
        with open(os.path.join(src_dir, filename), "r") as f:
            summon_readme(filename, locale, f.read())
            no_readme = False
    if no_readme:
        summon_readme()


def get_new_version(lst: "TamperScript", new: "TamperScript", bi: "BuildInfo"):
    """获取新的版本号(可能不变)"""
    no_update = new.equals_without_version(lst)
    lst_v = lst.get_version() if lst else None
    bi_v = bi.get_info('@version')

    def nv(make):
        new_v = make(get_time_version())
        if lst_v:
            while new_v == lst_v:
                new_v = make(get_time_version())
        return str(new_v)

    if bi_v:  # 有前缀
        bi_v = bi_v if bi_v.endswith(".") else f"{bi_v}."
        if no_update and lst_v and lst_v.startswith(bi_v):
            return lst_v  # 无更新, 有旧版, 前缀符合
        return nv(lambda time_v: bi_v + time_v)
    if no_update and lst_v:  # 没有更新, 有旧版, 没有前缀
        return lst_v

    return nv(lambda time_v: time_v)


def get_time_version():
    """返回当前基于版本的时间戳"""
    t = datetime.now()
    s1 = t.strftime("%Y%m%d.%H%M%S")
    s2 = t.microsecond // 100000
    return f"{s1}{s2}"


def parse_js(src: "list[str]|str|None"):
    """
    分离用户脚本中的定义与实际内容
    """
    if not src:
        return None
    in_desc = False
    all_desc: "list[tuple[str, str]]" = []
    lines: list[str] = []
    src = src if isinstance(src, list) else src.split('\n')
    for line in src:
        ls = line.strip()
        if ls.startswith("//"):
            if "==/UserScript==" in ls:
                in_desc = False
                continue
            elif "==UserScript==" in ls:
                in_desc = True
            elif in_desc and '@' in ls:
                key_i1 = ls.index('@')
                key_i2 = ls.index(' ', key_i1)
                key = ls[key_i1:key_i2]
                value = ls[key_i2:].strip()
                all_desc.append((key, value))
        if not in_desc:
            if line.endswith('\n'):
                line = line[:-1]
            if line.endswith('\r'):
                line = line[:-1]
            lines.append(line)
    return TamperScript(all_desc, lines)


def summon_js(src_script: str, build_info: BuildInfo, require: Require):
    """解析原始脚本, 并添加新的内容"""
    with open(src_script, "r") as f:
        src = f.read()

    ts = parse_js(src)
    if require:
        for req in require.require:
            ts.desc.append('@require', req)

    ts.desc.sort(key=lambda x: f"{x[0]}{' '*max(1,15-len(x[0]))}{x[1]}\n")

    for key, value in reversed(build_info.info.items()):
        found = False
        for i, (k, _) in enumerate(ts.desc):
            if k == key:
                if value:
                    ts.desc[i] = (key, value)
                found = True
                break
        if not found:
            ts.desc.insert(0, (key, value if value else build_info.default_info[key]))

    return ts


def ts2js(in_file, out_file):
    """将TypeScript转换为JavaScript"""
    cmds = [
        "npx tsc",
        f'"{in_file}"',
        "--outfile",
        f'"{out_file}"',
    ]
    cmd = " ".join(cmds)
    os.system(cmd)


if __name__ == "__main__":
    mis = get_infos()
    for mi in mis:
        build_single(*mi)
