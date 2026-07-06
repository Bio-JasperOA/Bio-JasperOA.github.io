---
layout: archive
title: ""
permalink: /
author_profile: true
redirect_from:
  - /about/
  - /about.html
---

<span class='anchor' id='about-me'></span>

# 👋 关于我

Jie (J. Song) 是一位专注于生物信息学的数据科学家与研究人员，具有基因组学与转录组学分析、工具开发与多组学整合经验。致力于开发高效的生物信息学工具和方法论，推动精准医学和生物医学研究的发展。

**研究方向**：
- 基因组学与转录组学 - 大规模测序数据分析与处理
- 生物信息学工具开发 - Nextflow / Snakemake 工作流设计
- 多组学数据整合 - 蛋白质组、代谢组、表观遗传学整合分析
- 机器学习应用 - 深度学习在生物信息学中的应用
- 开源软件贡献 - 参与和维护开源生物信息学项目

---

## 📝 发表论文

{% for pub in site.data.publications %}
<div class='paper-box'>
  <div class='paper-box-image'>
    <div>
      <div class="badge">{{ pub.year }}</div>
    </div>
  </div>
  <div class='paper-box-text' markdown="1">
**{{ pub.title }}**

{{ pub.authors }}

*{{ pub.journal }}*{% if pub.link %} [![](https://img.shields.io/badge/Paper-000?logo=readthedocs&logoColor=fff)]({{ pub.link }}){:target="_blank"}{% endif %}
  </div>
</div>
{% else %}
<p style="text-align:center; color: #999; margin: 2rem 0;">暂无发表论文记录 — 在 <code>_data/publications.yml</code> 中添加</p>
{% endfor %}

---

## 🏆 奖项荣誉

{% for award in site.data.awards %}
- **{{ award.year }}** - {{ award.title }}{% if award.by %} (*{{ award.by }}*){% endif %}
{% else %}
<p style="color: #999;">暂无奖项记录 — 在 <code>_data/awards.yml</code> 中添加</p>
{% endfor %}

---

## 📖 教育经历

- **Ph.D. Candidate in Bioinformatics** | University (2023-2025)  
  *Supervisor: Prof. XYZ*

- **M.S. in Computational Biology** | University (2021-2023)

- **B.S. in Biological Sciences** | University (2017-2021)

---

## 🛠️ 技能专长

**编程语言**
- Python, R, Bash, Perl, Go

**生物信息工具**
- GATK, SAMtools, BWA, Trinity, DESeq2

**工作流框架**
- Nextflow, Snakemake, WDL, CWL

**数据科学**
- Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch

**开发工具**
- Git/GitHub, Docker, Singularity, Linux/macOS

---

## 📚 最新博客

{% for post in site.posts limit:8 %}
- [{{ post.title }}]({{ post.url }}) — {{ post.date | date: "%Y-%m-%d" }}
{% else %}
<p style="color: #999;">尚无博客文章 — 在 <code>_posts/</code> 文件夹中添加 Markdown 文件</p>
{% endfor %}

---

## 📧 联系方式

- **邮箱**: jie@example.com
- **GitHub**: [@Bio-JasperOA](https://github.com/Bio-JasperOA)
- **ORCID**: [点击填写](#)
