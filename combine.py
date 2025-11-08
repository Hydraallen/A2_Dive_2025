#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并多个Vega-Lite可视化HTML文件
"""

import re
import argparse


def extract_spec(html_content):
    """从HTML内容中提取Vega-Lite规范"""
    spec_match = re.search(r'var spec = ({.*?});', html_content, re.DOTALL)
    return spec_match.group(1) if spec_match else '{}'


def merge_html_files(file_paths, output_path, titles=None):
    """
    合并多个HTML文件中的Vega-Lite可视化
    
    参数:
        file_paths: HTML文件路径列表
        output_path: 输出文件路径
        titles: 每个可视化的标题列表（可选）
    """
    
    # 默认标题
    if titles is None:
        titles = [
            "📊 Expenditure and Contribution Analysis",
            "🗺️ Geographic Distribution by County",
            "📈 Additional Analysis"
        ]
    
    # 确保标题数量足够
    while len(titles) < len(file_paths):
        titles.append(f"📊 Visualization {len(titles) + 1}")
    
    # 读取所有HTML文件并提取spec
    specs = []
    for i, file_path in enumerate(file_paths):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            spec = extract_spec(html_content)
            specs.append(spec)
            print(f"✓ 已读取文件 {i+1}: {file_path}")
        except FileNotFoundError:
            print(f"✗ 警告: 找不到文件 {file_path}")
            specs.append('{}')
    
    # 生成可视化div
    vis_divs = ""
    for i, title in enumerate(titles[:len(file_paths)]):
        vis_divs += f"""
    <!-- 第{i+1}个可视化 -->
    <div class="visualization">
      <div class="vis-title">{title}</div>
      <div id="vis{i+1}"></div>
    </div>
    """
    
    # 生成spec变量声明
    spec_declarations = ""
    for i, spec in enumerate(specs):
        spec_declarations += f"      var spec{i+1} = {spec};\n"
    
    # 生成渲染代码
    render_code = ""
    for i in range(len(specs)):
        render_code += f"""
      // 渲染第{i+1}个图表
      const el{i+1} = document.getElementById('vis{i+1}');
      vegaEmbed("#vis{i+1}", spec{i+1}, embedOpt)
        .catch(error => showError(el{i+1}, error));
      """
    
    # 生成CSS样式
    vega_embed_styles = ", ".join([f"#vis{i+1}.vega-embed" for i in range(1, len(specs) + 1)])
    vega_embed_details = ", ".join([f"#vis{i+1}.vega-embed details,\n    #vis{i+1}.vega-embed details summary" for i in range(1, len(specs) + 1)])
    
    # 创建合并后的HTML
    merged_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Michigan Political Finance Dashboard</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f5f5f5;
    }}
    
    .container {{
      max-width: 1400px;
      margin: 0 auto;
      background-color: white;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    h1 {{
      text-align: center;
      color: #333;
      margin-bottom: 10px;
      font-size: 28px;
    }}
    
    .subtitle {{
      text-align: center;
      color: #666;
      margin-bottom: 30px;
      font-size: 14px;
    }}
    
    .visualization {{
      margin-bottom: 40px;
      border: 1px solid #ddd;
      padding: 20px;
      border-radius: 5px;
      background-color: #fafafa;
    }}
    
    .visualization:last-child {{
      margin-bottom: 0;
    }}
    
    .vis-title {{
      font-size: 20px;
      font-weight: bold;
      color: #555;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 2px solid #007bff;
    }}

    {vega_embed_styles} {{
      width: 100%;
      display: flex;
    }}

    {vega_embed_details} {{
      position: relative;
    }}
    
    .footer {{
      text-align: center;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #ddd;
      color: #999;
      font-size: 12px;
    }}
  </style>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-lite@5.20.1"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
</head>
<body>
  <div class="container">
    <h1>Michigan Political Finance Analysis Dashboard</h1>
    <div class="subtitle">Comprehensive visualization of political finance data</div>
    {vis_divs}
    <div class="footer">
      Generated with Vega-Lite | Data visualization dashboard
    </div>
  </div>

  <script>
    (function(vegaEmbed) {{
      // 图表规范
{spec_declarations}
      
      var embedOpt = {{"mode": "vega-lite"}};

      function showError(el, error){{
          el.innerHTML = ('<div style="color:red;">'
                          + '<p>JavaScript Error: ' + error.message + '</p>'
                          + "<p>This usually means there's a typo in your chart specification. "
                          + "See the javascript console for the full traceback.</p>"
                          + '</div>');
          throw error;
      }}
      {render_code}
    }})(vegaEmbed);

  </script>
</body>
</html>"""
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(merged_html)
    
    print(f"\n✅ 成功合并 {len(file_paths)} 个HTML文件到: {output_path}")


if __name__ == "__main__":
    # 直接指定要合并的文件
    files = [
        "michigan_choropleth.html",
        "michigan_choropleth2.html", 
        "expenditure_contribution_dashboard.html"
    ]
    
    # 自定义标题（可选）
    titles = [
        "🗺️ Michigan Counties - Log Average Amount by County(Expenditure)",
        "📊 Michigan Counties - Log Average Amount by County(Contribution)",
        "📈 Trend Analysis Over Time"
    ]
    
    output = "index.html"
    
    try:
        merge_html_files(files, output, titles)
        print(f"🎉 合并完成！请在浏览器中打开 {output} 查看结果。")
        print(f"📊 共合并了 {len(files)} 个可视化图表")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
