#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给专栏 README 里未完成的文章补「发布标题」行。

发布标题 = 填到 CSDN 的文章标题，也是正文 H1。搜索友好型：
含核心词、疑问式优先、12-24 字、不加课次前缀。
"""

import io
import os
import re
import sys

README = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "S0-语言与浏览器基础",
    "01-HTML与CSS地基",
    "README.md",
)

# 清单条目名 -> 发布标题
TITLES = {
    # HTML 表格
    "一张数据表": "table 标签怎么写？tr、th、td 一次讲清",
    "合并单元格": "colspan 和 rowspan 怎么用？表格合并单元格",
    # HTML 表单
    "用 form 把输入收成一组": "form 标签是什么？表单怎么收集数据",
    "单行文本框，和旁边的文字": "input text 怎么写？label 和 placeholder",
    "密码框、邮箱框和多行文字": "input 密码框邮箱框怎么写？textarea 多行",
    "单选和多选": "radio 和 checkbox 有什么区别？单选多选怎么写",
    "下拉框": "select 和 option 怎么写？下拉框一次讲清",
    "提交按钮": "button 标签怎么用？submit、reset 区别",
    "提交前，浏览器会做的检查": "required 和 maxlength 是什么？表单校验",
    "给一组输入加个小标题": "fieldset 和 legend 怎么用？表单分组",
    "不能改的两种情况": "disabled 和 readonly 有什么区别？表单禁用",
    # 声音、视频和标签页
    "播放声音和视频": "video 和 audio 标签怎么用？网页播放音视频",
    "标签页上的小图标": "favicon 怎么设置？link rel=icon 图标写法",
    "标签页标题，和一段简介": "title 和 meta description 怎么写？页面摘要",
    # 样式写在哪，写给谁
    "样式放进 css 文件": "CSS 文件怎么引入？link rel=stylesheet 用法",
    "一条样式长什么样": "CSS 语法结构是什么？选择器和声明怎么写",
    "用 class 给一组元素加样式": "class 选择器怎么用？CSS 类选择器一次讲清",
    "选中某一种标签": "标签选择器怎么用？CSS 元素选择器写法",
    "选中某一块里面的元素": "后代选择器还是子选择器？nav a 和 nav > a",
    "鼠标放上去，以及键盘选中时": "hover 和 focus 怎么用？CSS 伪类一次讲清",
    "两条样式冲突时，听谁的": "CSS 优先级怎么算？选择器权重和层叠顺序",
    "选择器的强弱怎么数": "CSS 优先级怎么数？id、class、标签权重对比",
    "颜色和字体会不会传给里面": "CSS 样式继承是什么？哪些属性会继承",
    # 字和颜色
    "颜色的三种写法": "CSS 颜色怎么写？颜色名、十六进制和 rgb",
    "字号、字体和粗细": "font-size 和 font-family 怎么用？CSS 字体设置",
    "行高，和文字靠哪边": "line-height 和 text-align 是什么？行高与对齐",
    # 盒子的边距、边框和背景
    "内容、内边距、边框、外边距": "盒模型是什么？content、padding、border、margin",
    "width 到底包住哪几层": "box-sizing 是什么？border-box 和 width 的关系",
    "上下外边距会粘成一段": "外边距合并是什么？margin 塌陷怎么解决",
    "背景色铺在哪一层": "background-color 铺在哪？背景色和外边距的关系",
    "用一张图做背景": "background-image 怎么用？cover 和 contain 区别",
    "边框和圆角": "border 和 border-radius 怎么写？边框圆角一次讲清",
    # 元素默认怎么排队
    "独占一行，还是挤在同一行": "块级元素和行内元素的区别？display 入门",
    "留在一行里，又能设宽高": "inline-block 是什么？既排列又能设宽高",
    "块往下排，字往右排": "CSS 元素默认怎么排列？正常文档流一次讲清",
    "让文字绕着图片走": "float 是什么？CSS 浮动布局怎么用",
    "浏览器自带的边距和圆点": "浏览器默认样式是什么？body 边距和列表圆点",
    # 用 Flex 排成一行或一列
    "让子元素排成一行": "display: flex 怎么用？Flex 布局入门",
    "改成竖排，或排满就换行": "flex-direction 和 flex-wrap 怎么用？Flex 换行",
    "这一行靠左、居中，还是两端分开": "justify-content 怎么用？Flex 主轴对齐",
    "项在上下方向靠哪": "align-items 怎么用？Flex 交叉轴对齐",
    "换成多行之后，行与行怎么分": "align-content 是什么？Flex 多行怎么分间距",
    "多出来的空白分给谁": "flex-grow 是什么？Flex 剩余空间怎么分",
    "分空白之前，每一项先占多宽": "flex-basis 是什么？Flex 基准宽度",
    "一行挤不下时，谁缩小": "flex-shrink 是什么？Flex 压缩规则",
    "一行写完放大、缩小和基准": "flex 简写怎么写？flex: 1 和 auto 区别",
    "项和项之间留一条缝": "gap 是什么？Flex 和 Grid 的间距属性",
    "改看到的顺序，不改阅读顺序": "order 是什么？Flex 顺序和阅读顺序的区别",
    "在盒子里水平垂直居中": "Flex 水平垂直居中怎么写？justify-content",
    "导航：左边商标，右边菜单": "Flex 布局做导航栏？两端对齐和 margin auto",
    "一排里每块一样宽": "Flex 等分列怎么写？flex: 1 的用法",
    "内容少时，页脚仍在窗口底部": "Flex 布局让页脚固定底部？sticky footer",
    # 用 Grid 排成格子
    "划出几列、几行": "display: grid 怎么用？Grid 布局入门",
    "把剩下的宽度分成几份": "fr 是什么？CSS Grid 分数单位",
    "卡片有最小宽度，列数跟着变": "repeat auto-fit minmax 怎么用？自适应卡片",
    "一个格子跨两列": "grid-column: span 2 怎么用？Grid 跨列跨行",
    "用第几条线来指定位置": "grid-column 和 grid-row 怎么写？Grid 线定位",
    "给页头、侧栏、内容起名字": "grid-template-areas 怎么用？Grid 区域布局",
    "格子里面的内容靠哪边": "justify-items 和 align-items 区别？Grid 对齐",
    # 脱离正常排队，以及谁盖住谁
    "五种定位，各自相对谁": "position 有哪几种？static、relative、absolute",
    "相对原来的位置挪一挪": "position: relative 怎么用？相对定位详解",
    "离开队伍，相对父元素来摆": "position: absolute 怎么用？绝对定位和包含块",
    "钉在浏览器窗口上": "position: fixed 怎么用？固定定位详解",
    "滚到顶部就吸住": "position: sticky 怎么用？粘性定位详解",
    "重叠时，默认谁在上面": "CSS 层叠顺序是什么？元素重叠谁在上面",
    "z-index 只在同一层里比较": "z-index 怎么用？层叠上下文一次讲清",
    "为什么 z-index 有时出不去": "层叠上下文怎么形成的？z-index 失效原因",
    # 屏幕变窄、变宽
    "让手机按真实宽度来排": "viewport 怎么写？移动端适配第一步",
    "百分比是相对谁的": "CSS 百分比怎么算？宽度和高度的参照",
    "em 跟着这块的字号，rem 跟着整页": "em 和 rem 有什么区别？CSS 相对单位",
    "按窗口的宽和高来取值": "vw 和 vh 是什么？CSS 视口单位",
    "屏幕够宽，才用这组样式": "media 怎么用？CSS 媒体查询入门",
    "在页面开始挤的地方设断点": "响应式断点怎么定？CSS 媒体查询实战",
    "图片不要撑破旁边的容器": "图片自适应怎么写？max-width 100% 用法",
    # 做成一张课程介绍页
    "同一种颜色只写一次": "CSS 自定义属性怎么用？var 变量写法",
    "给盒子加一层浅阴影": "box-shadow 怎么写？CSS 阴影效果详解",
    "一栏内容停在页面中间": "CSS 水平居中怎么写？max-width 和 margin auto",
    "悬停时，颜色慢慢变化": "transition 怎么用？CSS 过渡效果",
    "把链接做成按钮的样子": "a 标签怎么变成按钮？CSS 按钮样式",
    "课程介绍页：先只写结构": "用 HTML 写课程介绍页？语义化结构实战",
    "课程介绍页：页头和首屏": "HTML 课程介绍页实战？页头和首屏结构",
    "课程介绍页：三张卡片": "HTML 课程介绍页实战？三张卡片结构",
    "课程介绍页：接上页脚": "HTML 课程介绍页实战？页脚结构和语义",
    "课程介绍页：窄屏幕怎么排": "课程介绍页响应式怎么写？媒体查询实战",
}


def main():
    with io.open(README, encoding="utf-8") as f:
        lines = f.read().split("\n")

    out = []
    inserted = 0
    missing = []
    seen = set()

    for line in lines:
        out.append(line)
        m = re.match(r"^- \[ \] (.+)$", line)
        if not m:
            continue
        name = m.group(1).strip()
        if name not in TITLES:
            missing.append(name)
            continue
        if name in seen:
            continue
        seen.add(name)
        out.append(f"  - 发布标题：{TITLES[name]}")
        inserted += 1

    if missing:
        print("警告：这些条目没找到标题映射：")
        for x in missing:
            print("  -", x)

    with io.open(README, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print(f"已插入 {inserted} 条发布标题")
    unused = set(TITLES) - seen
    if unused:
        print("警告：映射里这些没被用到：")
        for x in sorted(unused):
            print("  -", x)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
