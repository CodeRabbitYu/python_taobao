import time
import numpy as np
import pandas as pd
import jieba.analyse
from pyecharts import options as opts
from pyecharts.globals import SymbolType, ThemeType

from pyecharts.charts import Pie, Bar, Map, WordCloud

# 淘宝商品原生excel文件保存路径
GOODS_EXCEL_PATH = 'taobao_goods.xlsx'
# 淘宝商品标准excel文件保存路径
GOODS_STANDARD_EXCEL_PATH = 'taobao_goods_standard.xlsx'
# 清洗词
STOP_WORDS_FILE_PATH = 'stop_words.txt'
# 读取标准数据
DF_STANDARD = pd.read_excel(GOODS_STANDARD_EXCEL_PATH)

SEARCHKEY_WORD = '防晒服'


def standard_data():
    '''
    清洗淘宝爬下来的原生数据
    例：
        1.5万人付款 -> 15000
        广州 广州 -> 广州
    '''
    df = pd.read_excel(GOODS_EXCEL_PATH)

    # 1. 将价格转化为整数型
    raw_sales = df['销量'].values
    new_sales = []
    for sales in raw_sales:
        sales = sales[:-3]
        sales = sales.replace('+', '')
        if '万' in sales:
            sales = sales[:-1]
            if '.' in sales:
                sales = sales.replace('.', '') + '000'
            else:
                sales = sales + '0000'
        sales = int(sales)
        new_sales.append(sales)
    df['销量'] = new_sales
    # print(df['销量'].values)

    # 2、将地区转化为只包含省
    raw_location = df['店铺位置'].values
    new_location = []
    for location in raw_location:
        if ' ' in location:
            location = location[:location.find(' ')]
        new_location.append(location)
    # df.location与df[location]效果类似
    df['店铺位置'] = new_location
    # print(df['店铺位置'].values)

    # 3. 处理价格，去掉前面的符号
    raw_price = df['价格'].values
    new_price = []
    for price in raw_price:
        if '¥' in price:
            price = price[1:]
        new_price.append(price)
    df['价格'] = new_price
    # print(df['价格'].values)

    # 3、生成新的excel
    writer = pd.ExcelWriter(GOODS_STANDARD_EXCEL_PATH)
    # columns参数用于指定生成的excel中列的顺序
    df.to_excel(excel_writer=writer, columns=['标题', '价格', '店铺', '销量', '店铺位置', '是否包邮', '是否是天猫', '是否参加活动', '商品地址',  '商品图片'], index=False,
                encoding='utf-8', sheet_name='Sheet')
    writer.save()
    writer.close()


def analysis_title():
    """
    词云分析商品标题
    :return:
    """
    # 引入全局数据
    global DF_STANDARD
    # 数据清洗，去掉无效词
    jieba.analyse.set_stop_words(STOP_WORDS_FILE_PATH)
    # 1、词数统计
    keywords_count_list = jieba.analyse.textrank(
        ' '.join(DF_STANDARD["标题"]), topK=50, withWeight=True)
    # print(keywords_count_list)
    # 生成词云
    word_cloud = (
        WordCloud()
        .add("", keywords_count_list, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"功能词云TOP50"))
    )
    word_cloud.render('title-word-cloud.html')

    # 2、商品标题词频分析生成柱状图
    # 2.1统计词数
    # 取前20高频的关键词
    keywords_count_dict = {i[0]: 0 for i in reversed(keywords_count_list[:20])}
    cut_words = jieba.cut(' '.join(DF_STANDARD["标题"]))
    for word in cut_words:
        for keyword in keywords_count_dict.keys():
            if word == keyword:
                keywords_count_dict[keyword] = keywords_count_dict[keyword] + 1
    # print(keywords_count_dict)
    # 2.2生成柱状图
    keywords_count_bar = (
        Bar()
        .add_xaxis(list(keywords_count_dict.keys()))
        .add_yaxis("", list(keywords_count_dict.values()))
        .reversal_axis()
        .set_series_opts(label_opts=opts.LabelOpts(position="right"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"功能TOP20"),
            yaxis_opts=opts.AxisOpts(name="功能"),
            xaxis_opts=opts.AxisOpts(name="商品数")
        )
    )
    keywords_count_bar.render('title-word-count-bar.html')

    # 3、标题高频关键字与平均销量关系
    keywords_sales_dict = analysis_title_keywords(
        keywords_count_list, '销量', 20)
    # 生成柱状图
    keywords_sales_bar = (
        Bar()
        .add_xaxis(list(keywords_sales_dict.keys()))
        .add_yaxis("", list(keywords_sales_dict.values()))
        .reversal_axis()
        .set_series_opts(label_opts=opts.LabelOpts(position="right"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"功能与平均销量TOP20"),
            yaxis_opts=opts.AxisOpts(name="功能"),
            xaxis_opts=opts.AxisOpts(name="平均销量")
        )
    )
    keywords_sales_bar.render('title-word-sales-bar.html')

    # 4、标题高频关键字与平均售价关系
    keywords_price_dict = analysis_title_keywords(
        keywords_count_list, '价格', 20)
    # 生成柱状图
    keywords_price_bar = (
        Bar()
        .add_xaxis(list(keywords_price_dict.keys()))
        .add_yaxis("", list(keywords_price_dict.values()))
        .reversal_axis()
        .set_series_opts(label_opts=opts.LabelOpts(position="right"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"商品功能与平均售价TOP20"),
            yaxis_opts=opts.AxisOpts(name="功能"),
            xaxis_opts=opts.AxisOpts(name="平均售价")
        )
    )
    keywords_price_bar.render('title-word-price-bar.html')


def analysis_title_keywords(keywords_count_list, column, top_num) -> dict:
    """
    分析标题关键字与其他属性的关系
    :param keywords_count_list: 关键字列表
    :param column: 需要分析的属性名
    :param top_num: 截取前多少个
    :return:
    """
    '''

    '''

    # 1、获取高频词，生成一个dict={'keyword1':[], 'keyword2':[],...}
    keywords_column_dict = {i[0]: [] for i in keywords_count_list}
    for row in DF_STANDARD.iterrows():
        for keyword in keywords_column_dict.keys():
            if keyword in row[1]['标题']:
                # 2、 将标题包含关键字的属性值放在列表中，dict={'keyword1':[属性值1,属性值2, 数据源中该标题一列的数据...]}
                keywords_column_dict[keyword].append(row[1][column])
    # 3、 求属性值的平均值，dict={'keyword1':平均值1, 'keyword2',平均值2}
    for keyword in keywords_column_dict.keys():
        keyword_column_list = keywords_column_dict[keyword]
        keywords_column_dict[keyword] = sum(
            keyword_column_list) / len(keyword_column_list)

    # 4、 根据平均值排序，从小到大
    keywords_price_dict = dict(
        sorted(keywords_column_dict.items(), key=lambda d: d[1]))
    # 5、截取平均值最高的20个关键字
    keywords_price_dict = {k: keywords_price_dict[k] for k in list(
        keywords_price_dict.keys())[-top_num:]}
    # print(keywords_price_dict)

    return keywords_price_dict


def analysis_price():
    """
    分析商品价格
    :return:
    """
    # 引入全局数据
    global DF_STANDARD
    # 设置切分区域
    price_list_bins = [0, 20, 40, 60, 80, 100, 120, 150, 200, 1000000]
    # 设置切分后对应标签
    price_list_labels = ['0-20', '21-40', '41-60', '61-80',
                         '81-100', '101-120', '121-150', '151-200', '200以上']
    # 分区统计
    price_count = cut_and_sort_data(
        price_list_bins, price_list_labels, DF_STANDARD['价格'])
    print(price_count)
    # 生成柱状图
    bar = (
        Bar()
        .add_xaxis(list(price_count.keys()))
        .add_yaxis("", list(price_count.values()))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"商品价格区间分布柱状体"),
            yaxis_opts=opts.AxisOpts(name="个商品"),
            xaxis_opts=opts.AxisOpts(name="商品售价：元")
        )
    )
    bar.render('price-bar.html')
    # 生成饼图
    age_count_list = [list(z) for z in zip(
        price_count.keys(), price_count.values())]
    legend_opts = opts.LegendOpts(orient="vertical",
                                  pos_top="20%",
                                  pos_left="10%")
    pie = (
        Pie()
        .add("", age_count_list)
        .set_global_opts(title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"商品价格区间饼图", pos_left='center'), legend_opts=legend_opts)
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    pie.render('price-pie.html')


def analysis_sales():
    """
    销量情况分布
    :return:
    """
    # 引入全局数据
    global DF_STANDARD
    # 设置切分区域
    listBins = [0, 100, 500, 1000, 5000, 10000, 100000]
    # 设置切分后对应标签
    listLabels = ['一百以内', '一百到五百', '五百到一千', '一千到五千', '五千到一万', '一万以上']
    # 分区统计
    sales_count = cut_and_sort_data(listBins, listLabels, DF_STANDARD['销量'])
    print(sales_count)

    legend_opts = opts.LegendOpts(orient="vertical",
                                  pos_top="20%",
                                  pos_left="10%")

    # 生成柱状图
    bar = (
        Bar()
        .add_xaxis(list(sales_count.keys()))
        .add_yaxis("", list(sales_count.values()))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"商品销量区间分布柱状图"),

            yaxis_opts=opts.AxisOpts(name="个商品"),
            xaxis_opts=opts.AxisOpts(name="销售件数")
        )
    )
    bar.render('sales-bar.html')
    # 生成饼图
    age_count_list = [list(z) for z in zip(
        sales_count.keys(), sales_count.values())]
    pie = (
        Pie()
        .add("", age_count_list)
        .set_global_opts(title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"商品销量区间饼图"), legend_opts=legend_opts,)
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    pie.render('sales-pie.html')


def cut_and_sort_data(listBins, listLabels, data_list) -> dict:
    '''
    统计list中的元素个数，返回元素和count
    :param listBins: 数据切分区域
    :param listLabels: 切分后对应标签
    :param data_list: 数据列表形式
    :return: key为元素value为count的dict
    '''
    data_labels_list = pd.cut(data_list, bins=listBins,
                              labels=listLabels, include_lowest=True)
    # 生成一个以listLabels为顺序的字典，这样就不需要后面重新排序
    data_count = {i: 0 for i in listLabels}
    # 统计结果
    for value in data_labels_list:
        # get(value, num)函数的作用是获取字典中value对应的键值, num=0指示初始值大小。

        print(data_count.get(value))

        data_count[value] = data_count.get(value) + 1
    print(data_count)
    return data_count


def analysis_price_sales():
    """
    商品价格与销量关系分析
    :return:
    """
    # 引入全局数据
    global DF_STANDARD
    df = DF_STANDARD.copy()
    df['group'] = pd.qcut(df['价格'], 12, precision=0)
    df.group.value_counts().reset_index()
    df_group_sales = df[['销量', 'group']].groupby(
        'group').mean().reset_index().round(2)
    df_group_str = [str(i) for i in df_group_sales['group']]
    print(df.group)
    # 生成柱状图
    bar = (
        Bar()
        .add_xaxis(df_group_str)
        .add_yaxis("", list(df_group_sales['销量']), category_gap="50%")
        .set_global_opts(
            title_opts=opts.TitleOpts(title=SEARCHKEY_WORD+"商品价格分区与平均销量柱状图"),
            yaxis_opts=opts.AxisOpts(name="平均销量"),
            xaxis_opts=opts.AxisOpts(
                name="价格区间", axislabel_opts={"rotate": 30})
        )
    )
    bar.render('price-sales-bar.html')


def analysis_province_sales():
    """
    省份与销量的分布
    :return:
    """
    # 引入全局数据
    global DF_STANDARD

    # 1、全国商家数量分布
    province_location = DF_STANDARD['店铺位置'].value_counts()
    province_location_list = [list(item) for item in province_location.items()]
    # print(province_location_list)
    # 1.1 生成热力图
    province_location_map = (
        Map(init_opts=opts.InitOpts(width="800px",
                                    height="860px"))
        .add(SEARCHKEY_WORD+"商家数量全国分布图", province_location_list, "china", zoom=1)
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(min_=0, max_=150),
        )
    )
    province_location_map.render('province-location-map.html')
    # 1.2 生成柱状图
    province_location_bar = (
        Bar()
        .add_xaxis(province_location.index.tolist())
        .add_yaxis("", province_location.values.tolist(), category_gap="50%")
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=SEARCHKEY_WORD + "商家数量地区柱状图"),
            yaxis_opts=opts.AxisOpts(name="商家数量"),
            xaxis_opts=opts.AxisOpts(name="地区", axislabel_opts={"rotate": 0})
        )

    )
    province_location_bar.render('province-location-bar.html')

    # 2、全国商家省份销量总和分布
    province_location_sum = DF_STANDARD.pivot_table(
        index='店铺位置', values='销量', aggfunc=np.sum)
    # print(province_location_sum)

    '''
    .astype(int) 可以用这个方法对数据转换为 整数
    .round(2) 保留两位小数
    在pyecharts的Map中，如果有一个值为0，jiu
    '''
    # 根据销量排序
    province_location_sum = province_location_sum.sort_values(
        '销量',  ascending=False).astype(float)

    province_location_sum_list = [list(item) for item in
                                  zip(province_location_sum.index, np.ravel(province_location_sum.values))]
    # print(province_location_sum_list)

    # 2.1 生成热力图
    province_location_sum_map = (
        Map(init_opts=opts.InitOpts(width="800px",
                                    height="860px"))
        .add(SEARCHKEY_WORD+"各省商家销量总和全国分布图", province_location_sum_list, "china", zoom=1)
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(min_=0, max_=10000),
        )
    )
    province_location_sum_map.render('province-location-sum-map.html')
    # 2.2 生成柱状图
    province_location_sum_bar = (
        Bar()
        .add_xaxis(province_location_sum.index.tolist())
        .add_yaxis("", list(np.ravel(province_location_sum.values)), category_gap="50%")
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=SEARCHKEY_WORD+"各省商家销量总和地区柱状图"),
            yaxis_opts=opts.AxisOpts(name="总销量"),
            xaxis_opts=opts.AxisOpts(
                name="地区", axislabel_opts={"rotate": 0})
        )
    )
    province_location_sum_bar.render('province-location-sum-bar.html')

    # 3、全国商家省份平均销量分布
    province_location_mean = DF_STANDARD.pivot_table(
        index='店铺位置', values='销量', aggfunc=np.mean)
    # 根据平均销量排序
    province_location_mean = province_location_mean.sort_values(
        '销量', ascending=False).round(2)
    province_location_mean_list = [list(item) for item in
                                   zip(province_location_mean.index, np.ravel(province_location_mean.values))]

    print(province_location_mean_list)
    # 3.1 生成热力图
    Map().add(SEARCHKEY_WORD+"商家平均销量全国分布图", province_location_mean_list, "china").set_global_opts(
        visualmap_opts=opts.VisualMapOpts(min_=0, max_=10000),
    ).render('province_location_mean_map.html')

    # 3.2 生成柱状图
    province_location_mean_bar = (
        Bar()
        .add_xaxis(province_location_mean.index.tolist())
        .add_yaxis("", list(map(int, np.ravel(province_location_mean.values))), category_gap="50%")
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=SEARCHKEY_WORD+"各省商家平均销量地区柱状图"),
            yaxis_opts=opts.AxisOpts(name="平均销量"),
            xaxis_opts=opts.AxisOpts(name="地区", axislabel_opts={"rotate": 0})
        )
    )
    province_location_mean_bar.render('province-location-mean-bar.html')


if __name__ == '__main__':
    # 数据清洗
    standard_data()
    # analysis_title() # 词云分析商品标题
    # analysis_price() # 分析商品价格
    # analysis_sales() # 销量情况分布

    analysis_price_sales()  # 商品价格与销量关系分析
    # 省份与销量的分布
    # 1. 全国商家数量分布 2. 全国商家省份销量总和分布 3. 全国商家省份平均销量分布
    # analysis_province_sales()
