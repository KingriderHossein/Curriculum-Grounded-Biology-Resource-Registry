#!/usr/bin/env python3
"""One-time, idempotent content migration. Version 1.0.0.

Scope: this registry only. No network, subprocess, source deletion or new resources.
Writes only the known data, student pages and navigation files listed below.
"""
from __future__ import annotations
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
DATE = '2026-09-25'
L, P = '\u2066', '\u2069'

REPLACEMENTS = {
 'OPENSTAX-BIOLOGY2E-2018': ('https://covers.openlibrary.org/b/isbn/9781947172517-L.jpg?default=false','b62180a7a3e05fb381f643e9e0d6153bc8de3caa4811beb87b4ad8d6f58ce030','Open Library; full second-edition cover','9781947172517'),
 'BOOK-LEHNINGER-CORE-1E-2025': ('https://prod-cat-files.macmillan.cloud/MediaResources/Jackets/258W/9781319589967.jpg','3a39c652911a1207c855c4e42a3ca4a53ca183aed0cf6147c1299dd5e5c6d680','Macmillan Learning, exact ISBN','9781319589967'),
 'BOOK-BIOCHEMISTRY10-2023': ('https://prod-cat-files.macmillan.cloud/MediaResources/Jackets/258W/9781319498504.jpg','0785a69e038451c7e6acc40f47e65d9f7a2f7358f41b80330a64ff1692a2d6d5','Macmillan Learning, exact ISBN','9781319498504'),
 'BOOK-LEHNINGER8-2021': ('https://prod-cat-files.macmillan.cloud/MediaResources/Jackets/258W/9781319381493.jpg','b0afe2bff603fdef1803d691b74d62a983809afa745f61fb4b92b892cb77a925','Macmillan Learning, exact ISBN','9781319381493'),
 'BOOK-GENETICS-CONCEPTUAL7-2024': ('https://prod-cat-files.macmillan.cloud/MediaResources/Jackets/258W/9781319546700.jpg','5055198bd8ac62a5c4bf654a9715f217c224c6690e52cb7d099f45da946f31f8','Macmillan Learning, exact ISBN','9781319546700'),
 'BOOK-INTRO-GENETIC-ANALYSIS12-2025': ('https://prod-cat-files.macmillan.cloud/MediaResources/Jackets/258W/9781319589943.jpg','ff0db1b4dff0c7a37a6d2427c85473688474388897dbcbf39e20c5e08b5215a9','Macmillan Learning, exact ISBN','9781319589943'),
 'BOOK-GENETIC-THEORY-ANALYSIS2-2023': ('https://dynamic.indigoimages.ca/v1/books/books/1118086929/1.jpg','8db6c1ba722ecfbe7368f7dbd6a127b4e40e6220f1ce106a0905f61120ff673e','Indigo retailer; title and second edition visually checked','9781118086926'),
 'BOOK-MOLECULAR-BIOLOGY3-2019': ('https://dynamic.indigoimages.ca/v1/books/books/0128132884/1.jpg','38e526b1b45f2a7d45a49599a1429123a140df4d3dea64f5846186148ecfd727','Indigo retailer; Clark/Pazdernik/McGehee third edition visually checked','9780128132883'),
 'BOOK-LEWIN-ESSENTIAL-GENES4-2021': ('https://images.booksense.com/images/130/173/9781284173130.jpg','dbe0274c1b6cf0b51e9572e99e0afa884330e7ac81b2f2eae7ba213af87348bc','MIT Press Bookstore image service; fourth-edition package cover','9781284173130'),
 'BOOK-PRESCOTT-MICROBIOLOGY12-2026': ('https://www.mheducation.com/cover-images/Jpeg_400-high/1265827176.jpeg','0bd1859d868837e0b7a6f60d62789430ad4c4c65482f95ef0e5d14a0a5436c1e','McGraw Hill; 2026 international release cover','9781265827175'),
 'BOOK-MICROBIOLOGY-EVOLVING6-2023': ('https://cdn2.wwnorton.com/wwnproducts/COLLEG/1/6/9781324033561/9781324033561_198.jpg','3164b65fe4e85d4e34e60cef78e67242217a0e37b69778348713c559af934f91','W. W. Norton, exact ISBN','9781324033561'),
 'BOOK-BROCK-MICROORGANISMS16-2024': ('https://www.pearson.com/store/pmccommercewebservices/v2/medias/size-W370-A1030-00-25-75-A103000257574-A103000257574-Lrg.jpg?context=bWFzdGVyfGltYWdlc3wyMzg3MnxpbWFnZS9qcGVnfHN5cy1tYXN0ZXIvaW1hZ2VzL2g3Mi9oN2QvMTU0NDE0MzAxNTExOTgvc2l6ZV9XMzcwXy9BMTAzMC8wMC8yNS83NS9BMTAzMDAwMjU3NTc0L0ExMDMwMDAyNTc1NzRfTHJnLmpwZ3wzOTdjOTEzMWE5ZjVjY2MyZWEzNjUzYmY1YTk1Nzk2YjU0NTFjOWIzYTVmZWIzMjNjYmI3ZTYwYjgwN2RjZDA4&imwidth=3840','c6b724a938755dc86b718a2776b1a0e8b1c6fecb7606e00a50da21999e49ccc4','Pearson product page, global sixteenth edition','9781292404790')
}
UNCHANGED_HASHES = {
 'BOOK-ECB6-2023':'60e8746c33cd04fa7e854518830f49551b09985a1334c09db18667d30d0a6de3',
 'BOOK-CELL9-2022':'ea258cff125dd35b21afbdf96fe8e528a1a3a04de05adfc95cbc02c84f6a41de',
 'BOOK-MBOC7-2022':'84179ec3ef90b2c6a160732fe25d1bebc58ad4a4e0f15e0fada25cf6d7e8fd44',
 'BOOK-CELL-SIGNALING2-2024':'744941cd3ff1a279443454636d9f54cc85619d14bd1dfdba977845de32f0d175',
 'OPENSTAX-MICROBIOLOGY-2016':'014c3d7cb747d6a477f25da97d173dc5bed774cd3a2cedaf6f4b090155bb3e61'
}
BRANCHES = {
 'cell-envelope-surface': ('پوشش سلولی و معماری سطح میکروب','ساختمان سلول باکتری و آرکی'),
 'sensing-motility-physiology': ('حسگری، حرکت و فیزیولوژی میکروبی','فیزیولوژی، رشد و پاسخ به محیط'),
 'microbial-metabolism-regulation': ('متابولیسم میکروبی و تنظیم آن','مسیرهای سوخت‌وساز و زیست‌انرژی'),
 'microbial-genetics-mge': ('ژنتیک میکروبی و عناصر ژنتیکی متحرک','وراثت و انتقال افقی ژن'),
 'diversity-archaea-early-evolution': ('تنوع میکروبی، آرکی‌ها و تکامل اولیه','تنوع زیستی و تبارزایی میکروب‌ها'),
 'microbial-ecology-communities': ('اکولوژی میکروبی و تعاملات جوامع','اکولوژی و چرخه‌های زیست‌ژئوشیمیایی'),
 'host-microbiome': ('تعامل میزبان و میکروبیوم','همزیستی و میکروبیوتای طبیعی'),
 'pathogenesis-virulence': ('بیماری‌زایی و تعامل با میزبان','مبانی بیماری‌زایی و دفاع میزبان'),
 'antimicrobial-resistance': ('مقاومت ضدمیکروبی','مبانی داروهای ضدمیکروبی و تکامل')
}
TERMS = {
 'mobile genetic element':'عنصر ژنتیکی متحرک','microbial metabolism':'متابولیسم میکروبی',
 'antibiotic efficacy':'اثربخشی آنتی‌بیوتیک','natural product':'فراورده طبیعی',
 'energy program':'برنامه متابولیسم انرژی','sweep':'جاروب انتخابی','cross-feeding':'تغذیه متقابل',
 'microbiome':'میکروبیوم','metabolite':'متابولیت','genotype':'ژنوتیپ','phenotype':'فنوتیپ',
 'chemotaxis':'شیمی‌گرایی','flagella':'تاژک‌ها','envelope':'پوشش سلولی','morphology':'ریخت‌شناسی',
 'colonization':'استقرار میکروبی','pathogenesis':'بیماری‌زایی','ecology':'اکولوژی',
 'virulence':'بیماری‌زایی','metabolism':'متابولیسم','sensing':'حسگری','feedback':'بازخورد',
 'selection':'انتخاب طبیعی','dependency':'وابستگی','variation':'تنوع','evolution':'تکامل',
 'tolerance':'تحمل','redox':'اکسایش–کاهش','scale':'مقیاس','Roadmap':'نقشه‌راه',
 'Review':'مقاله مروری','workflow':'گردش‌کار'
}


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def write(path, data):
    (ROOT/path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT/path).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def iso(text):
    return L + str(text) + P


def fa(text):
    text = text.replace(L,'').replace(P,'')
    for term in sorted(TERMS, key=len, reverse=True):
        text = re.sub(r'(?<![A-Za-z])'+re.escape(term)+r'(?![A-Za-z])', TERMS[term], text)
    return re.sub(r'[A-Za-z][A-Za-z0-9+–—./-]*(?: +[A-Za-z][A-Za-z0-9+–—./-]*)*', lambda m: iso(m[0]), text)


def main():
    resources = read('data/resources.json'); by_id = {r['id']:r for r in resources['resources']}
    placements = read('data/placements.json'); subjects = read('data/subjects.json')
    old_urls = {}
    for rid,(url,sha,source,image_isbn) in REPLACEMENTS.items():
        r=by_id[rid]; old_urls[r['cover']['url']]=url
        r['cover'].update(url=url, source=source, image_isbn=image_isbn, expected_sha256=sha, visual_reviewed_on=DATE, visual_review_status='title_and_edition_checked')
        r['cover']['source_url']=r['publisher_url']
    for rid,sha in UNCHANGED_HASHES.items():
        by_id[rid]['cover'].update(expected_sha256=sha, visual_reviewed_on=DATE, visual_review_status='title_and_edition_checked', source_url=by_id[rid]['publisher_url'])
    lewin=by_id['BOOK-LEWIN-ESSENTIAL-GENES4-2021']
    lewin['cover']['source_url']='https://mitpressbookstore.mit.edu/book/9781284173130'
    lewin['cover']['variant_note']='Same fourth edition; image shows the companion-website package ISBN 9781284173130, not the standalone print ISBN 9781284189834.'
    brock=by_id['BOOK-BROCK-MICROORGANISMS16-2024']
    brock['published_year']=2021
    brock['bibliographic_note']='Exact print ISBN 9781292404790 is listed as published in 2021; the publisher page header 2024 refers to later digital products. The legacy resource ID is retained for stable links.'
    prescott=by_id['BOOK-PRESCOTT-MICROBIOLOGY12-2026']
    prescott.update(isbn='9781265827175', edition='2026 Release, International Student Edition', authors=['Joanne M. Willey','Kathleen M. Sandman','Sarah N. Salm','Nathan W. Rigel'])
    prescott['publisher_url']='https://www.mheducation.co.uk/prescott-s-microbiology-2026-release-ise-9781265827175-emea-group'
    prescott['purchase_url']=prescott['publisher_url'];prescott['cover']['source_url']=prescott['publisher_url']
    prescott['bibliographic_note']='2026 ISE authors checked against the publisher cover and the National Diet Library record. The commercial page retained the older three-author listing at review time; no stock guarantee is made.'
    prescott['metadata_sources']=[prescott['publisher_url'],'https://ndlsearch.ndl.go.jp/en/books/R100000136-I1970589942157279361']
    micro=[p for p in placements['placements'] if p['subject_id']=='MICROBIOLOGY']
    for p in micro:
        r=by_id[p['resource_id']]
        r['verification_evidence']={'checked_on':DATE,'scope':'publisher bibliographic metadata and abstract/TOC; not a full-text quality certification','sources':r.get('metadata_sources',[r['publisher_url']])}
        if r['resource_type']=='review_article':
            r['publication_status']='published'
        for key in ('best_for','why','how_to_use','next_step'):
            p['student_guidance_fa'][key]=fa(p['student_guidance_fa'][key])
    for rid in ['REVIEW-HELICOBACTER-FLAGELLA-2026','REVIEW-CIRCADIAN-MICROBIOME-2026']:
        by_id[rid]['publication_status']='peer_reviewed_advance_online'
    open_ids=['REVIEW-BACTERIAL-CHEMOTAXIS-2024','REVIEW-EARLY-MICROBIAL-LIFE-2024','REVIEW-CORRINOID-COMMUNITIES-2025','REVIEW-AMR-EVOLUTION-SCALES-2024','REVIEW-ACTINOMYCETOTA-METABOLITES-2025']
    for rid in open_ids:
        by_id[rid]['access_url']=by_id[rid]['publisher_url'];by_id[rid]['access_status']='open_access';by_id[rid]['license']='CC BY 4.0 (article text; inspect third-party credits)'
    by_id['REVIEW-METABOLISM-AMR-2025']['access_url']='https://pmc.ncbi.nlm.nih.gov/articles/PMC12173792/'
    by_id['REVIEW-METABOLISM-AMR-2025']['access_status']='free_author_manuscript'
    for p in micro:
        if p['resource_id']=='BOOK-BROCK-MICROORGANISMS16-2024':
            p['student_guidance_fa']['why']='فهرست مطالب ناشر، ساختار، فیزیولوژی، ژنتیک، تنوع و اکولوژی میکروبی را در یک مرجع گسترده گرد هم می‌آورد. این کتاب می‌تواند مرجع موضوعی یا کتاب اصلی یک درس دانشگاهی باشد.'
            p['student_guidance_fa']['how_to_use']='پس از مرور پیش‌نیازها، بخش مرتبط با موضوع را انتخاب کنید. خواندن همه کتاب‌های این نقشه‌راه پیش از استفاده از این مرجع الزامی نیست.'
        p['selection_rationale']=p['student_guidance_fa']['why']
    m=next(s for s in subjects['subjects'] if s['id']=='MICROBIOLOGY')
    m.update(status='complete_candidate')
    for b in m['branches']: b['fa_label']=BRANCHES[b['id']][0]
    write('data/resources.json',resources);write('data/placements.json',placements);write('data/subjects.json',subjects)
    pages=[ROOT/'README.md',*sorted((ROOT/'subjects').glob('*/README.md'))]
    for path in pages:
        text=path.read_text(encoding='utf-8')
        for old,new in old_urls.items():
            text=text.replace(old,html.escape(new,quote=True))
        if path.parent.name=='biochemistry' and by_id['OPENSTAX-BIOLOGY2E-2018']['cover']['url'] not in html.unescape(text):
            marker='### کتاب '+iso('Biology 2e')
            image='<p align="center"><img src="'+by_id['OPENSTAX-BIOLOGY2E-2018']['cover']['url']+'" width="155" alt="Biology 2e"></p>\n\n'
            if marker not in text: raise ValueError('Biochemistry foundation heading drifted')
            text=text.replace(marker,image+marker,1)
        path.write_text(text,encoding='utf-8')
    render_microbiology(m,micro,by_id)
    root=ROOT/'README.md';text=root.read_text(encoding='utf-8')
    row='| [میکروبیولوژی '+iso('Microbiology')+'](subjects/microbiology/README.md) | ۴ منبع | ۹ شاخه | ۲۲ |'
    if '](subjects/microbiology/README.md)' not in text:
        lines=text.splitlines();at=max(i for i,l in enumerate(lines) if l.startswith('| [') and 'subjects/' in l)
        lines.insert(at+1,row);text='\n'.join(lines)+'\n'
    root.write_text(text,encoding='utf-8')
    pmap=ROOT/'docs/project-map.md';t=pmap.read_text(encoding='utf-8')
    addition='\n- Microbiology: 4 general placements and 9 selected specialist branches.\n- Book-cover network/decoding audit: `scripts/audit_book_covers.py`; visual review evidence is stored per `cover` record.\n'
    if 'Book-cover network/decoding audit' not in t:pmap.write_text(t+addition,encoding='utf-8')
    print('Migration v1.0.0 complete: 12 cover replacements, 5 existing covers reviewed, Microbiology candidate rendered.')


def render_microbiology(subject, placements, by_id):
    lines=['<div dir="rtl" align="right">','', '# میکروبیولوژی | '+iso('Microbiology'),'','این نقشه‌راه برای مطالعه نظری میکروبیولوژی است: ساختمان و فیزیولوژی میکروب، متابولیسم، ژنتیک، تکامل، اکولوژی و تعامل با میزبان. منابع تخصصی پس از مبانی معرفی می‌شوند؛ این فهرست ادعای پوشش تمام ادبیات علمی را ندارد.','','**راهنمای انتخاب:** خواندن پیاپی هر چهار کتاب الزامی نیست. یک کتاب اصلی انتخاب کنید و منابع تکمیلی را برای موضوع‌هایی بخوانید که به توضیح یا عمق بیشتری نیاز دارند. مرحله‌بندی زیر پیشنهاد آموزشی این پروژه است، نه الزام ناشر.','','## مسیر عمومی','','پیش‌نیازها ← کتاب اصلی ← مطالعه تکمیلی ← مرجع پیشرفته و شاخه تخصصی','']
    stages=[('foundation','پایه'),('core','منبع اصلی'),('intermediate','منبع تکمیلی'),('advanced','مرجع پیشرفته')]
    for stage,title in stages:
        p=next(x for x in placements if x['learning_stage']==stage);r=by_id[p['resource_id']]
        lines.extend(['## '+title,'']);append_card(lines,p,r)
    lines.extend(['## شاخه‌های تخصصی','','در هر شاخه ابتدا مبحث عمومی معرفی‌شده را در کتاب اصلی بخوانید. سپس مقاله‌های زیر را به‌عنوان نمونه‌های تخصصی انتخاب کنید؛ دو مقاله جایگزین تمام مباحث آن شاخه نیستند.','','| شاخه | پیش‌نیاز موضوعی |','|---|---|'])
    for b in subject['branches']:
        label,prereq=BRANCHES[b['id']];lines.append('| '+label+' | '+prereq+' |')
    lines.append('')
    for b in subject['branches']:
        label,prereq=BRANCHES[b['id']]
        lines.extend(['<details>','<summary><strong>'+label+'</strong></summary>','','**ابتدا مطالعه کنید:** '+prereq+'، در کتاب اصلی یا مرجع پیشرفته.',''])
        ps=[p for p in placements if b['id'] in p.get('branch_ids',[])]
        for p in ps:append_card(lines,p,by_id[p['resource_id']])
        lines.extend(['</details>',''])
    lines.extend(['## حدود این نسخه','','برای مسیر عمومی چهار منبع و برای نه شاخه، هجده مقاله منتخب ثبت شده است. مباحثی مانند ویروس‌شناسی و قارچ‌شناسی در کتاب‌های عمومی وجود دارند، اما مسیر تخصصی مستقل آن‌ها هنوز بخشی از این صفحه نیست.','','اطلاعات کتاب‌شناختی و چکیده یا فهرست مطالب منابع با صفحات ناشر تطبیق داده شده‌اند. معرفی مقاله به معنای بررسی کامل متن یا تأیید تمام نتیجه‌گیری‌های آن نیست. منابع قدیمیِ مفهومی با سال واقعی معرفی می‌شوند؛ منابع جدید جای آن‌ها را به‌صورت خودکار نمی‌گیرند.','','[بازگشت به فهرست درس‌ها](../../README.md)','','</div>',''])
    (ROOT/'subjects/microbiology/README.md').write_text('\n'.join(lines),encoding='utf-8')


def append_card(lines,p,r):
    title=iso(r['title'])
    lines.extend(['### '+title,''])
    if r.get('cover'):
        lines.extend(['<p align="center"><a href="'+html.escape(r['publisher_url'],quote=True)+'"><img src="'+html.escape(r['cover']['url'],quote=True)+'" width="155" alt="'+html.escape(r['title']+' '+r.get('edition',''),quote=True)+'"></a></p>',''])
    guidance=p['student_guidance_fa']
    for key,label in [('best_for','مناسب برای'),('why','دلیل انتخاب'),('how_to_use','شیوه مطالعه'),('next_step','ادامه مسیر')]:
        lines.extend(['**'+label+':** '+guidance[key],''])
    parts=[', '.join(r['authors']),r.get('journal',r.get('publisher','')),str(r['published_year'])]
    if r.get('edition'):parts.append(r['edition'])
    parts.append(('ISBN: '+r['isbn']) if r.get('isbn') else 'DOI: '+r.get('doi',''))
    lines.extend(['<div dir="ltr" align="left">','',' · '.join(html.escape(s) for s in parts if s),'','</div>',''])
    links=['[صفحه رسمی منبع]('+r['publisher_url']+')']
    if r.get('purchase_url'):links.append('[خرید / بررسی موجودی]('+r['purchase_url']+')')
    if r.get('access_url'):links.append('[متن آزاد یا نسخه قانونی]('+r['access_url']+')')
    lines.extend([' · '.join(links),''])
    if r['id']=='BOOK-PRESCOTT-MICROBIOLOGY12-2026':
        lines.extend(['**دقت در نسخه:** این رکورد برای انتشار بین‌المللی ۲۰۲۶ است. نام نویسندگان با جلد و [رکورد کتابخانه ملی ژاپن](https://ndlsearch.ndl.go.jp/en/books/R100000136-I1970589942157279361) تطبیق داده شد؛ متن تبلیغاتی ناشر هنگام بررسی هنوز نام‌های نسخه پیشین را نشان می‌داد. پیش از خرید، شابک و موجودی را کنترل کنید.',''])
    if r['id']=='BOOK-BROCK-MICROORGANISMS16-2024':
        lines.extend(['**دقت در سال:** برای شابک چاپی این رکورد، ناشر سال ۲۰۲۱ را درج می‌کند. تاریخ ۲۰۲۴ بالای همان صفحه مربوط به عرضه‌های دیجیتال جدیدتر است.',''])
    if r.get('publication_status')=='peer_reviewed_advance_online':
        lines.extend(['**نوع انتشار:** مقاله مروری منتشرشده به‌صورت برخطِ پیش از شماره نهایی؛ پیش‌چاپ داوری‌نشده نیست.',''])
    if r['published_year']==2014:
        lines.extend(['**قدمت منبع:** این مقاله یک مرجع مفهومی قدیمی‌تر است، نه گزارش وضعیت پژوهش در سال ۲۰۲۶.',''])
    lines.extend(['---',''])

if __name__=='__main__':
    main()
