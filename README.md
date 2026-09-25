<div align="center">

# Curriculum-Grounded Biology Resource Registry

**A theory-only, syllabus-grounded registry of trusted biology learning resources for Iranian higher education.**

![Scope](https://img.shields.io/badge/scope-theory--only-2f855a)
![Data](https://img.shields.io/badge/data-validated-2563eb)
![Status](https://img.shields.io/badge/status-pilot-f59e0b)
![Contributions](https://img.shields.io/badge/contributions-welcome-7c3aed)

</div>

> یک رجیستری مشارکتی برای پیوند دادن **سرفصل رسمی → درس نظری → منبع معتبر و به‌روز**.  
> این پروژه عمداً منابع عملی، پروتکل‌ها، SOPها، Laboratory Manualها و آموزش‌های hands-on را پوشش نمی‌دهد.

## Pilot

The first implemented course is:

**B.Sc. Animal Biology → Cell Biology (زیست‌شناسی سلولی)**  
MSRT revised curriculum (1400), 3 theoretical credits / 48 hours.

[Open the full course page →](courses/cell-biology/README.md)

### Featured textbooks

<table>
<tr>
<td align="center" width="33%">
<img src="https://cdn2.wwnorton.com/wwnproducts/COLLEG/4/9/9781324033394/9781324033394_198.jpg" width="145" alt="Essential Cell Biology 6e cover"><br>
<b>Essential Cell Biology</b><br>
6th International Student Edition · 2023<br>
<a href="https://wwnorton.co.uk/books/9781324033394-essential-cell-biology-c7a43b27-8186-4ee2-b83f-e60dd511e7ac">Publisher / Purchase</a>
</td>
<td align="center" width="33%">
<img src="https://fdslive.oup.com/covers/anz/desktop/medium/9780197583722.jpg" width="145" alt="The Cell A Molecular Approach 9e cover"><br>
<b>The Cell: A Molecular Approach</b><br>
9th Edition · 2022<br>
<a href="https://www.oup.com.au/books/higher-education/biological-sciences/9780197583722">Publisher / Purchase</a>
</td>
<td align="center" width="33%">
<img src="https://cdn2.wwnorton.com/wwnproducts/COLLEG/2/5/9780393884852/9780393884852_198.jpg" width="145" alt="Molecular Biology of the Cell 7e cover"><br>
<b>Molecular Biology of the Cell</b><br>
7th Edition · 2022<br>
<a href="https://wwnorton.co.uk/books/9780393884852-molecular-biology-of-the-cell">Publisher / Purchase</a>
</td>
</tr>
</table>

## Repository model

```text
Curriculum
  └── Theoretical course
        ├── Official syllabus topics
        ├── Core textbook(s)
        ├── Reference textbook(s)
        └── Recent peer-reviewed updates
```

A source is not accepted merely because it is popular. It must be linked to a defined course/topic and pass the criteria in [METHODOLOGY.md](METHODOLOGY.md).

## Structure

```text
curricula/   curriculum-facing navigation
courses/     human-readable course pages
data/        machine-readable registry
schemas/     data contracts
scripts/     validation
docs/        project map and visual rules
.github/     contribution and CI workflow
```

## Contribution

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Every proposed resource must identify:

- the course and syllabus topic(s) it covers;
- bibliographic identity (ISBN/DOI where applicable);
- a publisher, journal, or other authoritative source;
- why it belongs in the registry;
- confirmation that it is **theory-only**.

## Project status

This is a pilot implementation. The data model and review rules are active, but the curriculum registry is not yet comprehensive.

See [PROJECT_SPEC.md](PROJECT_SPEC.md) for durable scope and [docs/project-map.md](docs/project-map.md) for where project truth lives.
