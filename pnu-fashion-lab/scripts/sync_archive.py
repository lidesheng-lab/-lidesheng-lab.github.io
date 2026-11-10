#!/usr/bin/env python3
"""Refresh official factual archive. pip install beautifulsoup4; review diff before publishing."""
import concurrent.futures, datetime, hashlib, json, pathlib, re, urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://fashiondesign.pusan.ac.kr'
PAGES={'professor':'71508','members':'71516','alumni':'72664','publications':'71512','conferences':'71520','awards':'71509','works':'71514'}
def clean(x):return re.sub(r'\s+',' ',x.get_text(' ',strip=True) if hasattr(x,'get_text') else str(x)).strip()
def fetch(url):
 for attempt in range(3):
  try:return BeautifulSoup(urllib.request.urlopen(url,timeout=45).read(),'html.parser')
  except Exception:
   if attempt==2:raise

def absolute(url):return urljoin(BASE,url)
def records(soup):
 out=[]
 for li in soup.select('.dissertation-Warp li'):
  a=li.select_one('.title a');dd=[clean(n) for n in li.select('dd')]
  if not a or len(dd)<4:raise ValueError('Publication schema changed')
  out.append({'title':clean(a),'author':dd[0],'venue':dd[1],'date':dd[2],'attachmentCount':int(dd[3]),'source':absolute(a['href']).split('?')[0]})
 return out

def collect(key):
 url=BASE+'/fashiondesign/'+PAGES[key]+'/subview.do';s=fetch(url)
 if key in ('members','alumni'):
  result=[]
  for li in s.select('._prFlLi'):
   a=li.select_one('.artclTitle a');dd=[clean(n) for n in li.select('dd')]
   result.append(dict(name=clean(a),english=dd[0],role=dd[1],email=dd[2],research=dd[3],source=absolute(a['href'])))
  if not result:raise ValueError('No profiles')
  return result
 if key in ('publications','conferences'):
  total=int(clean(s.select_one('.artclSerch .fnLeft strong')));fn='354' if key=='publications' else '355'
  result=records(s)
  for page in range(2,(total+9)//10+1):result+=records(fetch(BASE+f'/thesis/fashiondesign/{fn}/list.do?page={page}'))
  if len(result)!=total or len({x['source'] for x in result})!=total:raise ValueError('Incomplete publication pagination')
  return result
 if key=='awards':
  return [{'date':re.sub(r'\s+','',clean(tr.th)),'title':clean(tr.td),'source':url} for tr in s.select('#_JW_hist_basic tbody tr')]
 if key=='professor':
  # Store source text for human review; the page uses a concise editorial biography.
  return {'name':'이윤경 / Yoon Kyung Lee','image':absolute(s.select_one('.prof img')['src']),'source':url,'sourceDigest':hashlib.sha256(clean(s.select_one('.prof')).encode()).hexdigest()}
 if key=='works':
  total=int(clean(s.select_one('.board-rss strong')));lists=[s]
  for page in range(2,(total+7)//8+1):lists.append(fetch(BASE+f'/bbs/fashiondesign/17869/artclList.do?page={page}'))
  result=[]
  for page in lists:
   for li in page.select('.thumbLi'):
    a=li.select_one('.artclLinkView');img=li.select_one('img');title=img.get('alt','').removesuffix(' main image').strip() or clean(li.select_one('.artclTitle'))
    result.append({'title':title,'date':clean(li.select_one('._artclregDate dd')),'description':clean(li.select_one('.artclContent')),'image':absolute(img['src']) if img else '', 'source':absolute(a['href'])})
  if len(result)!=total:raise ValueError('Incomplete works pagination')
  return result
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
 data=dict(zip(PAGES,pool.map(collect,PAGES)))
def enrich(item):
 s=fetch(item['source'])
 item['attachments']=[{'label':clean(a),'url':absolute(a['href'])} for a in s.select('a[href*="fileDown.do"],a[href*="download.do"]')]
 if '/bbs/' in item['source']:
  content=s.select_one('.artclView')
  item['title']=clean(s.select_one('.artclViewTitle'))
  item['description']=clean(content)
  item['images']=[absolute(img['src']).replace(':443/','/') for img in content.select('img[src]')]
  if item['images']:item['image']=item['images'][0]
 else:
  item['links']=[{'label':clean(a) or 'Publication','url':a['href']} for a in s.select('.artclInsert a[href]') if a['href'].startswith(('https://','http://'))]
 return item
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 list(pool.map(enrich,data['publications']+data['conferences']+data['works']))
data['sources']={key:BASE+'/fashiondesign/'+value+'/subview.do' for key,value in PAGES.items()}
data['updatedAt']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
# Do not overwrite the previous good snapshot until every category validates.
path=ROOT/'archive-data.json'
previous=json.loads(path.read_text()) if path.exists() else {}
if {k:v for k,v in previous.items() if k!='updatedAt'} == {k:v for k,v in data.items() if k!='updatedAt'}:
 print('No source changes; keeping the existing snapshot date.')
else:
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print({k:len(v) for k,v in data.items() if isinstance(v,list)})
