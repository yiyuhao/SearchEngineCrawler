# SearchEngineCrawler
A crawler for collecting the identity information of clients scattered in various websites through keywords searching in each search engineen by scrapy


## Rule Config
```
{
	name: 搜索引擎唯一标志,
	search_url: 带格式化参数的url,
	page_size: (int) 搜索结果页每页链接数量,
	page_param: 通过页数计算url中page_param的表达式,
	result_selector: 搜索结果的a标签CSS选择器
}

{
	name: "google",
	search_url: "https://www.google.com/search?q={keywords}&start={page_param}",
	page_size: 10,
	page_param: '{}*10',
	result_selector: 'h3 > a'
}

{
	name: "bing",
	search_url: "http://www.bing.com/search?q={keywords}&first={page_param}",
	page_size: 10,
	page_param: '{}*10',
	result_selector: 'h2 > a'
}

{
	name: "baidu",
	search_url: "http://www.baidu.com/s?wd={keywords}&pn={page_param}",
	page_size: 10,
	page_param: '{}*10',
	result_selector: 'h3 > a'
}

{
	name: "yahoo",
	search_url: "https://search.yahoo.com/search;?p={keywords}&b={page_param}",
	page_size: 10,
	page_param: '{}*10 + 1',
	result_selector: 'h3 > a'
}

```
