"""Export only the article-fetch dependency tree from the native WeChat hunter."""
import ast


def bindings(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, ast.Import):
        return {item.asname or item.name.split('.')[0] for item in node.names}
    if isinstance(node, ast.ImportFrom):
        return {item.asname or item.name for item in node.names}
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        return {item.id for target in targets for item in ast.walk(target) if isinstance(item, ast.Name)}
    if isinstance(node, ast.Try):
        return set().union(*(bindings(item) for item in node.body))
    return set()


def export_fetch_module(source):
    tree = ast.parse(source)
    parser = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'build_parser')
    original = ast.get_source_segment(source, parser)
    if original.count('    # posts-list') != 1:
        raise ValueError('Native WeChat parser changed; review fetch export')
    fetch_parser = ast.parse(original.split('    # posts-list')[0] + '    return p\n').body[0]
    nodes = [fetch_parser if node is parser else node for node in tree.body]
    required = {'cmd_fetch', 'build_parser', 'main'}
    selected = set()
    while True:
        previous = (len(required), len(selected))
        for position, node in enumerate(nodes):
            if bindings(node) & required:
                selected.add(position)
                required.update(item.id for item in ast.walk(node) if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load))
        if previous == (len(required), len(selected)):
            break
    parts = ['"""Fetch public WeChat article links and optional images/cover over HTTP."""',
             'from __future__ import annotations']
    for position, node in enumerate(nodes):
        if position in selected:
            parts.append(ast.unparse(node) if node is fetch_parser else ast.get_source_segment(source, node))
    parts.append('if __name__ == "__main__":\n    sys.exit(main())')
    result = '\n\n'.join(parts) + '\n'
    result = result.replace('pip install httpx zstandard sqlcipher3', 'xiaobei-runtime setup --full')
    ast.parse(result)
    forbidden = ('WX_BIZ_', 'sqlcipher', 'sqlite3', 'cmd_posts_list', 'posts-list', '_docker_', 'wechat_keys', 'zstd')
    remaining = [value for value in forbidden if value.lower() in result.lower()]
    if remaining:
        raise ValueError('Article export unexpectedly includes client database dependencies: ' + ', '.join(remaining))
    return result


def export_fetch_manual(source):
    header, _, body = source[4:].partition('\n---\n')
    start = body.index('## fetch — 获取文章全文')
    end = body.index('## posts-list', start)
    return ('---\n' + header + '\n---\n\n# 微信公众号文章获取\n\n'
            '用户提供 mp.weixin.qq.com 文章链接时，用本技能获取正文、图片和封面；不读取本机客户端或账号后台。\n\n'
            '以用户提供的文章链接为输入，批量先验证一篇，成功后再处理其他链接。返回失败时保留实际错误，不把风控、删除或缺少正文当作成功。\n\n'
            + body[start:end].strip() + '\n')
