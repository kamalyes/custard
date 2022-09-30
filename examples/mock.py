from pprint import pprint

from custard.mock import Mock

Mock = Mock()

pprint(Mock.mock('@csentence 变量示例'))
pprint(Mock.mock('@paragraph 变量示例'))
pprint(Mock.mock('@cparagraph 变量示例'))
pprint(Mock.mock('@sentence 变量示例'))
pprint(Mock.mock('@csentence 变量示例'))
pprint(Mock.mock('@word 变量示例'))
pprint(Mock.mock('@cword 变量示例'))
pprint(Mock.mock('@emoji 变量示例'))
pprint(Mock.mock('@title 变量示例'))
pprint(Mock.mock('@ctitle 变量示例'))

pprint(Mock.mock({
    'list|1-10': [{
        'id|+1': 1,
        'email': '@EMAIL'
    }]
}))

pprint(Mock.mock({
    'number1|1-100.1-10': 1,
    'number2|123.1-10': 1,
    'number3|123.3': 1,
    'number4|123.10': 1.123
}))

pprint(Mock.mock({
    'regexp1': r'/[a-z][A-Z][0-9]/',
    'regexp2': r'/\w\W\s\S\d\D/',
    'regexp3': r'/\d{5,10}/',
    'regexp4': r'\/\d{5,10}\/'  # output raw regexp with escape slash
}))

pprint(Mock.mock({
    'name': {
        'first': '@first',
        'middle': '@first',
        'last': '@last',
        'email': 'example\\@gmail.com',
        'full': '@first @middle @last'
    }
}
))

pprint(Mock.mock_js("""
{
    name: {
        first: "@cfirst", 
        last: "@clast",
        name: "@first@last",
    }
}
"""))

pprint(Mock.mock({
    'random': {
        'name': [
            '@name',
            '@cname'
        ],
        'image': [
            # @image( size, background, foreground, format, text )
            "@image",
            "@image('300x400')",
            "@image('300x400', '占位图文字')",
            "@image('300x400', '#234567', '#FFFFFF', 'png', 'HelloWorld')"
        ],
        'emoji': [
            # emoji( pool, min, max )
            "@emoji",
            "@emoji('😀😁😂😃😄')",
            "@emoji(1, 3)",
            "@emoji('123🌘😷🙊★♠♫', 3, 6)"
        ]
    }
}
))
