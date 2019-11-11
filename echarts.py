"""
    <div id="main" style="width: 600px;height:400px;"></div>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('main'));

        // 指定图表的配置项和数据
        var option = {
            xAxis: {
                type: 'category',
                data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            },
            yAxis: {
                type: 'value'
            },
            series: [{
                type: 'bar',
                data: [120, 200, 150, 80, 70, 110, 130]
            }]
        };
        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    </script>
    """
#根据参数输出html图表h5 柱状图和线图
def html_bar_line_out(keys, values, name="main", width=600, height=400, bar_line="bar"):
    div=f'<div id="{name}" style="width: {width}px;height:{height}px;"></div>'
    var_chart = f"var myChart = echarts.init(document.getElementById('{name}'));"
    #key_data = "data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']"
    key_data = "data: " + str(keys)
     #value_data = "data: [120, 200, 150, 80, 70, 110, 130]"
    value_data = "data: " + str(values) +","
    type_data = f"     type: '{bar_line}'"
    
    html_str = div + '<script type="text/javascript">\n' + var_chart;
    html_str += """
    var option = {
        xAxis: {
        type: 'category',
    """ + key_data + """
                },
        yAxis: {
            type: 'value'
            },
        series: [{
    """ +value_data + type_data + """
          }]
      };
      // 使用刚指定的配置项和数据显示图表。
      myChart.setOption(option);
    </script>
    """
    return html_str
    
def html_line_out(keys, values, name="main", width=600, height=400):
    return html_bar_line_out(keys, values, name, width, height, "line")

def html_bar_out(keys, values, name="main", width=600, height=400):
    return html_bar_line_out(keys, values, name, width, height, "bar")    

"""
    //饼图
        <div id="main2" style="width: 600px;height:400px;"></div>
    <script>
        // 绘制图表。
        var myChart = echarts.init(document.getElementById('main2'))
        var option = ({
            series: {
                type: 'pie',
                data: [
                    {name: 'A', value: 1212},
                    {name: 'B', value: 2323},
                    {name: 'C', value: 1919}
                ]
            }
        });
        myChart.setOption(option)
    </script>"""  
#生成饼图字符串    
def html_pie_out(key_values, name="main", width=600, height=400):
    div=f'<div id="{name}" style="width: {width}px;height:{height}px;"></div>'
    var_chart = f"var myChart = echarts.init(document.getElementById('name'));"
    key_values_data = " "
    for key, value in key_values.items():
         key_values_data += f"{name: '{key}', value: '{value}'},"
    key_values_data = key_values_data[0, -2]
    html_str = div + "<script>" + var_chart + """
            var option = ({
            series: {
                type: 'pie',
                data: [
    """ + key_values_data + """
                    ]
            }
        });
        myChart.setOption(option)
    </script>
    """
    
