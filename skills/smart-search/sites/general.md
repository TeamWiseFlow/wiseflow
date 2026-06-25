# 通用搜索引擎

> last_verified: 2026-06-15

## Bing（推荐）

```
https://www.bing.com/search?q={keyword}
```

时间过滤（追加到 URL）：
- 24 小时内：`&filters=ex1:"ez1"`
- 一周内：`&filters=ex1:"ez2"`
- 一月内：`&filters=ex1:"ez3"`

分页：`&first={offset}` 其中 offset = (page − 1) × 10 + 1

### Bing News

```
https://www.bing.com/news/search?q={keyword}
```

### Bing Images

```
https://www.bing.com/images/search?q={keyword}
```

图片时间过滤：`&qft=filterui:age-lt{minutes}`（1440=天 / 10080=周 / 44640=月 / 525600=年）

## Baidu（backup）

```
https://www.baidu.com/s?wd={keyword}
```

### 百度图片

```
https://image.baidu.com/search/index?tn=baiduimage&fm=result&ie=utf-8&word={keyword}
```

## Quark / 夸克（fallback）

```
https://quark.sm.cn/s?q={keyword}
```

## Pitfalls

无特殊 pitfalls。通用搜索引擎不需要 Cookie Warmup。
