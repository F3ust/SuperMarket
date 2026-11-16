/* Bilingual layer, navigation and the commercial-insight pages (executive summary, revenue, net sales & discounts, customers & baskets, data quality). */
const L=(vi,en)=>LANG==='en'?en:vi;
const NUMRE=/\d[\d.,]*/g;
const origText=new WeakMap(),outText=new WeakMap(),hiddenEls=new Set();
const NDICT={};Object.keys(DICT).forEach(k=>{NDICT[k.replace(/\s+/g,' ')]=DICT[k];});
function fillNums(s,nums){let i=0;return s.replace(/#/g,()=>nums[i++]??'#');}
function translateNode(n){
  const p=n.parentElement;if(!p||/^(SCRIPT|STYLE)$/.test(p.tagName))return;
  const cur=n.nodeValue;let o=origText.get(n);if(o===undefined||outText.get(n)!==cur){o=cur;origText.set(n,o);}
  const core=o.trim().replace(/\s+/g,' ');let res=o;
  if(core){const e=core.startsWith('Bootstrap ')?'':NDICT[core.replace(NUMRE,'#')];if(e!==undefined){const nums=core.match(NUMRE)||[];const v=e===''?'':LANG==='en'?e[1]:(e[0]??core);
    const lead=o.match(/^\s*/)[0],trail=o.match(/\s*$/)[0];
    if(v===''){res='';const alone=p.textContent.trim().replace(/\s+/g,' ')===core;if(alone){const t=p.closest('.scope-note')||p;t.style.display='none';hiddenEls.add(t);}}
    else res=lead+fillNums(v,nums)+trail;}}
  if(res!==cur)n.nodeValue=res;outText.set(n,res);
}
function translateAttrs(el){
  for(const a of ['placeholder','title','aria-label']){if(!el.hasAttribute||!el.hasAttribute(a))continue;const k='data-o-'+a;if(!el.hasAttribute(k))el.setAttribute(k,el.getAttribute(a));
    const o=el.getAttribute(k),e=NDICT[o.replace(/\s+/g,' ').replace(NUMRE,'#')];if(e&&e!=='')el.setAttribute(a,fillNums(LANG==='en'?e[1]:(e[0]??o),o.match(NUMRE)||[]));else el.setAttribute(a,o);}
}
function translateTree(root){
  if(!root)return;if(root.nodeType===3){translateNode(root);return;}if(root.nodeType!==1)return;
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT);let n=w.currentNode;
  do{if(n.nodeType===3)translateNode(n);else translateAttrs(n);}while(n=w.nextNode());
}
let pendingTx=new Set(),txScheduled=false;
function scheduleTx(node){pendingTx.add(node);if(txScheduled)return;txScheduled=true;requestAnimationFrame(()=>{txScheduled=false;const s=pendingTx;pendingTx=new Set();s.forEach(x=>{if(x.isConnected)translateTree(x);});});}
new MutationObserver(ms=>{for(const m of ms){if(m.type==='characterData')scheduleTx(m.target);else m.addedNodes.forEach(scheduleTx);}}).observe(document.body,{childList:true,subtree:true,characterData:true});

/* ---- navigation ---- */
const NAV_GROUPS=[
  [['Hiệu quả kinh doanh','Performance'],[['overview','Tổng quan điều hành','Executive Summary','grid'],['growth','Phân tích doanh thu','Revenue Analysis','trend'],['netsales','Doanh thu thuần & chiết khấu','Net Sales & Discounts','basket'],['catalog','Cơ cấu ngành hàng','Merchandise Mix','cube'],['stores','Hiệu quả cửa hàng','Store Performance','store']]],
  [['Khách hàng','Customers'],[['loyalty','Kinh tế khách hàng & giỏ hàng','Customer & Basket Economics','users'],['customers','Giá trị khách hàng (RFM)','Customer Value (RFM)','users'],['basket','Phân tích giỏ hàng','Basket Analytics','basket']]],
  [['Mô hình dự báo','Predictive Models'],[['forecast','Dự báo doanh thu','Sales Forecast','trend'],['risk','Rủi ro rời bỏ','Churn Risk','shield'],['inference','Chấm điểm dữ liệu mới','Score New Data','spark']]],
  [['Tài chính & dữ liệu','Finance & Data'],[['finance','Lợi nhuận & vốn lưu động','Profitability & Working Capital','flow'],['explorer','Giao dịch chi tiết','Transaction Explorer','table'],['quality','Chất lượng dữ liệu & định nghĩa','Data Quality & Definitions','shield']]]
];
[['netsales','x','trend'],['loyalty','x','users'],['quality','x','shield']].forEach(r=>{if(!routes.some(v=>v[0]===r[0]))routes.push(r);});
['netsales','loyalty','quality'].forEach(k=>frozen.add(k));
function buildMenu(){const items=NAV_GROUPS.flatMap(g=>g[1]).map(([k,vi,en,i])=>[k,L(vi,en),i]);roleMenus.executive=items;roleMenus.operations=items;return items;}
buildMenu();
function roleNavigation(){
  userRole='executive';buildMenu();document.body.dataset.role='executive';
  $('navigation').innerHTML=NAV_GROUPS.map(g=>`<div class="nav-group">${L(g[0][0],g[0][1])}</div>`+g[1].map(([k,vi,en,i])=>`<a href="#${k}" data-route="${k}">${icon(i)}<span>${L(vi,en)}</span></a>`).join('')).join('');
  document.querySelector('.workspace b').textContent=L('Chuỗi bán lẻ · Complete Journey','Retail chain · Complete Journey');
  document.querySelector('.workspace small').textContent=L('FY2017 · USD · 2.469 hộ · 457 cửa hàng','FY2017 · USD · 2,469 households · 457 stores');
  document.querySelector('#sidebar>.nav-caption').textContent=L('PHÂN TÍCH','ANALYTICS');
  if(D){$('sourceState').textContent=L('Đã đối soát '+N(D.meta.rows)+' dòng',N(D.meta.rows)+' rows reconciled');$('footerStatus').textContent=L('Snapshot '+D.meta.runId+' · xử lý trong trình duyệt','Snapshot '+D.meta.runId+' · processed in browser');document.querySelector('.app-footer span').textContent='Retail Intelligence';}
}
function setLang(l){
  LANG=l==='en'?'en':'vi';try{localStorage.setItem('retailLang',LANG);}catch{}
  document.documentElement.lang=LANG;document.title=L('Retail Intelligence | Phân tích dữ liệu bán lẻ','Retail Intelligence | Retail Analytics Platform');
  hiddenEls.forEach(e=>{e.style.display='';});hiddenEls.clear();
  document.querySelectorAll('.lang-switch button').forEach(b=>b.classList.toggle('active',b.dataset.lang===LANG));
  if(ready){roleNavigation();render();}
  translateTree(document.body);
}
(()=>{const bar=document.querySelector('.top-actions');if(!bar)return;const w=document.createElement('div');w.className='lang-switch';w.innerHTML='<button data-lang="vi" type="button">VI</button><button data-lang="en" type="button">EN</button>';bar.insertBefore(w,bar.firstChild);
  w.addEventListener('click',e=>{const b=e.target.closest('button[data-lang]');if(b)setLang(b.dataset.lang);});
  document.querySelectorAll('.lang-switch button').forEach(b=>b.classList.toggle('active',b.dataset.lang===LANG));document.documentElement.lang=LANG;document.title=L('Retail Intelligence | Phân tích dữ liệu bán lẻ','Retail Intelligence | Retail Analytics Platform');translateTree(document.body);})();

/* ---- helpers ---- */
const INS=()=>D.insights;
const usd=(v,d=0)=>N(v,d),k$=v=>N(v/1000,0)+'K',pc=(v,d=1)=>P(v,d),xx=(v,d=1)=>N(v,d)+'×';
const MON=()=>LANG==='en'?['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']:['T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12'];
const WKD=()=>LANG==='en'?['Mon','Tue','Wed','Thu','Fri','Sat','Sun']:['T2','T3','T4','T5','T6','T7','CN'];
const HERO=(tag,title,sub)=>`<div class="hero"><div class="hero-tag">${tag}</div><h1>${title}</h1><p>${sub}</p></div>`;
const noActions=' ';
function insightCards(items){return `<div class="insight-grid">${items.map(i=>`<div class="ins"><div class="ins-k">${i.k}</div><div class="ins-v">${i.v}</div><h3>${i.t}</h3><p>${i.p}</p></div>`).join('')}</div>`;}
const soWhat=(t)=>`<div class="sowhat"><b>${L('Nhận định','Insight')}</b><span>${t}</span></div>`;
const pill=(t,type='')=>`<span class="mini-pill ${type}">${t}</span>`;
function barLine(id,x,bars,line,opts={}){
  plot(id,[{type:'bar',x,y:bars,name:opts.barName||'',marker:{color:C.green,cornerradius:3},hovertemplate:'%{x}<br>%{y:,.0f}<extra></extra>'},
    {type:'scatter',mode:'lines+markers',x,y:line,yaxis:'y2',name:opts.lineName||'',line:{color:C.amber,width:2.5},marker:{size:6},hovertemplate:'%{x}<br>%{y:.1%}<extra></extra>'}],
    {yaxis:{tickformat:',.0f',rangemode:'tozero'},yaxis2:{overlaying:'y',side:'right',tickformat:'.0%',showgrid:false,rangemode:'tozero',zeroline:false,tickfont:{size:9}},showlegend:true,legend:{orientation:'h',y:1.12,x:0},margin:{l:56,r:48,t:28,b:36}},opts.h||300);
}

/* ---- Executive summary ---- */
function pgOverview(){
  const I=INS(),g=I.gross_to_net,c=I.customers,b=I.basket,br=I.brand,bb=I.basket_bands,days=I.days,st=I.stores;
  const prior=R.prior,delta=prior&&prior.sales?R.sales/prior.sales-1:null;
  const totalDisc=g.gross-g.net,big=bb.slice(4),bigShare=big.reduce((s,x)=>s+x.share,0),bigBaskets=big.reduce((s,x)=>s+x.baskets,0)/b.count;
  const ds=I.departments.filter(d=>d.share>=.03&&d.growth!=null),best=[...ds].sort((a,b2)=>b2.growth-a.growth)[0],worst=[...ds].sort((a,b2)=>a.growth-b2.growth)[0];
  const promoDeep=I.departments.filter(d=>d.share>=.03).sort((a,b2)=>b2.rate-a.rate).slice(0,2);
  const rm=D.risk_summary.test_metrics.filter(x=>x.model==='hist_gradient'),rLift=rm.reduce((s,x)=>s+x.lift_top20,0)/rm.length,rRec=rm.reduce((s,x)=>s+x.recall_top20,0)/rm.length;
  const wape=D.forecast_summary.test_metrics.find(x=>x.model===D.forecast_summary.champion_selected_on_validation)?.WAPE;
  const f=[
    {k:L('Tập trung khách hàng','Customer concentration'),v:pc(c.top10),t:L('Top 10% hộ tạo '+pc(c.top10)+' doanh thu','Top 10% of households drive '+pc(c.top10)+' of net sales'),p:L('50% hộ thấp nhất chỉ đóng góp '+pc(c.bottom50)+'. Giữ chân nhóm top decile là ưu tiên số một.','The bottom 50% contribute only '+pc(c.bottom50)+'. Retaining the top decile is the first priority.')},
    {k:L('Chiết khấu','Discounting'),v:pc(g.rate),t:L('Chiết khấu bằng '+pc(g.rate)+' doanh thu gộp ('+k$(totalDisc)+' USD)','Discounts equal '+pc(g.rate)+' of gross sales (USD '+k$(totalDisc)+')'),p:L(pc(g.promo_line_share,0)+' dòng hàng có chiết khấu; thẻ thành viên chiếm '+pc(g.retail/totalDisc,0)+' tổng chiết khấu.',pc(g.promo_line_share,0)+' of lines carry a discount; loyalty discounts are '+pc(g.retail/totalDisc,0)+' of the total.')},
    {k:L('Nhãn riêng','Private label'),v:pc(g.private_share),t:L('Nhãn riêng chiếm '+pc(g.private_share)+' doanh thu thuần','Private label is '+pc(g.private_share)+' of net sales'),p:L('Tỷ lệ chiết khấu '+pc(br.private_rate)+' so với '+pc(br.national_rate)+' của hàng thương hiệu: đòn bẩy cho biên lợi nhuận.','Discount rate '+pc(br.private_rate)+' vs '+pc(br.national_rate)+' for national brands: a margin-mix lever.')},
    {k:L('Quy mô giỏ hàng','Basket size'),v:pc(bigShare,0),t:L('Giỏ từ 21 dòng hàng chiếm '+pc(bigBaskets,0)+' số giỏ nhưng '+pc(bigShare,0)+' doanh thu','Baskets of 21+ lines are '+pc(bigBaskets,0)+' of baskets but '+pc(bigShare,0)+' of net sales'),p:L('Giỏ có coupon ('+pc(b.coupon_share)+') đạt AOV '+usd(b.coupon_aov,2)+' USD, gấp '+xx(b.coupon_aov/b.plain_aov)+' giỏ thường.','Coupon baskets ('+pc(b.coupon_share)+') average USD '+usd(b.coupon_aov,2)+', '+xx(b.coupon_aov/b.plain_aov)+' standard baskets.')},
    {k:L('Cơ cấu ngành','Category momentum'),v:'+'+pc(best.growth,0),t:L(best.name+' tăng '+pc(best.growth)+' (Q4 so với Q1); '+worst.name+' '+pc(worst.growth),best.name+' grew '+pc(best.growth)+' (Q4 vs Q1); '+worst.name+' '+pc(worst.growth)),p:L('Chiết khấu sâu nhất ở '+promoDeep.map(d=>d.name+' ('+pc(d.rate)+')').join(', ')+' so với GROCERY '+pc(I.departments[0].rate)+'.','Deepest discounting in '+promoDeep.map(d=>d.name+' ('+pc(d.rate)+')').join(', ')+' vs GROCERY '+pc(I.departments[0].rate)+'.')},
    {k:L('Tính mùa vụ','Seasonality'),v:xx(days.top[0][1]/days.mean),t:L('Ngày cao điểm '+days.top[0][0]+' đạt '+usd(days.top[0][1])+' USD, gấp '+xx(days.top[0][1]/days.mean)+' ngày bình quân','Peak day '+days.top[0][0]+' reached USD '+usd(days.top[0][1])+', '+xx(days.top[0][1]/days.mean)+' the average day'),p:L('Ngày thấp nhất '+days.low[0][0]+' ('+usd(days.low[0][1])+' USD). Kế hoạch nhân sự và tồn kho cần bám lịch lễ.','Lowest day '+days.low[0][0]+' (USD '+usd(days.low[0][1])+'). Staffing and inventory plans should follow the holiday calendar.')},
    {k:L('Năng suất cửa hàng','Store productivity'),v:xx(st.per_hh_p90/st.per_hh_p10),t:L('Doanh thu/hộ chênh '+xx(st.per_hh_p90/st.per_hh_p10)+' giữa nhóm P90 và P10 của cửa hàng','Sales per household differ '+xx(st.per_hh_p90/st.per_hh_p10)+' between P90 and P10 stores'),p:L('Trung vị '+usd(st.per_hh_median)+' USD/hộ ('+st.active_hh20+' cửa hàng có ≥20 hộ). Cửa hàng dưới P10 cần rà soát danh mục và khuyến mãi.','Median USD '+usd(st.per_hh_median)+' per household ('+st.active_hh20+' stores with 20+ households). Stores below P10 need a range and promotion review.')},
    {k:L('Mô hình dự báo','Predictive models'),v:xx(rLift),t:L('Mô hình rủi ro bắt '+pc(rRec,0)+' khách ngừng mua trong top 20% điểm','Churn model captures '+pc(rRec,0)+' of lapsing households in the top 20% of scores'),p:L('Dự báo doanh thu 7 ngày có WAPE '+pc(wape)+' (baseline trung bình 28 ngày).','7-day sales forecast WAPE is '+pc(wape)+' (28-day mean baseline).')}
  ];
  const mo=I.monthly;
  const ready_=[
    [L('Doanh thu thuần, AOV, số giỏ','Net sales, AOV, basket count'),pill(L('Có','Available'),'ok'),L('Giao dịch POS (mẫu hộ)','POS transactions (household panel)')],
    [L('Doanh thu gộp & chiết khấu','Gross sales & discounts'),pill(L('Có','Available'),'ok'),L('Cột chiết khấu thẻ, coupon, coupon match','Loyalty, coupon and coupon-match discount columns')],
    [L('Biên lợi nhuận gộp','Gross margin'),pill(L('Cần dữ liệu','Input required'),'warn'),L('Giá vốn theo SKU–ngày, rebate','Unit cost by SKU-day, vendor rebates')],
    [L('EBITDA / EBIT','EBITDA / EBIT'),pill(L('Cần dữ liệu','Input required'),'warn'),L('OPEX, khấu hao, chi phí cửa hàng','OPEX, D&A, store costs')],
    [L('Vòng quay tồn kho / GMROI','Inventory turns / GMROI'),pill(L('Cần dữ liệu','Input required'),'warn'),L('Tồn kho bình quân theo giá vốn','Average inventory at cost')],
    [L('Chu kỳ chuyển đổi tiền (CCC)','Cash conversion cycle (CCC)'),pill(L('Cần dữ liệu','Input required'),'warn'),L('Phải thu, phải trả, tồn kho','Receivables, payables, inventory')],
    [L('LFL / doanh thu trên m²','LFL / sales per sq m'),pill(L('Cần dữ liệu','Input required'),'warn'),L('POS toàn chuỗi, diện tích, lịch mở cửa','Full-chain POS, floor area, trading calendar')]
  ];
  $('content').innerHTML=HERO(L('TỔNG QUAN ĐIỀU HÀNH','EXECUTIVE SUMMARY'),L('Doanh thu thuần '+usd(R.sales)+' USD'+(delta==null?'':', '+(delta>=0?'tăng ':'giảm ')+pc(Math.abs(delta))+' so với kỳ trước'),'Net sales USD '+usd(R.sales)+(delta==null?'':', '+(delta>=0?'up ':'down ')+pc(Math.abs(delta))+' vs prior period')),
      L('Chiết khấu '+pc(g.rate)+' doanh thu gộp · top 10% hộ tạo '+pc(c.top10)+' doanh thu · FY2017: '+usd(g.net)+' USD thuần','Discounts '+pc(g.rate)+' of gross · top 10% households drive '+pc(c.top10)+' of net sales · FY2017: USD '+usd(g.net)+' net'))+
    `<div class="kpi-grid six">${kpi(L('Doanh thu thuần','Net sales'),usd(R.sales),'USD',prior?L('so với kỳ trước','vs prior period'):'',delta,'trend')}${kpi(L('Số giỏ','Baskets'),usd(R.baskets),'',L('giao dịch','transactions'),null,'basket')}${kpi('AOV',usd(R.aov,2),'USD',L('giá trị giỏ bình quân','average basket value'),null,'cube')}${kpi(L('Hộ hoạt động','Active households'),usd(R.customers),'',usd(R.lines)+L(' dòng hàng',' lines'),null,'users')}${kpi(L('Doanh thu/hộ','Sales / household'),usd(R.sales/Math.max(1,R.customers),0),'USD',L('trong kỳ','in period'),null,'users')}${kpi(L('Tỷ lệ chiết khấu FY','FY discount rate'),pc(g.rate),'',L('trên doanh thu gộp','of gross sales'),null,'shield')}</div>`+
    `<h2 class="sec">${L('Phát hiện chính','Key findings')}</h2>`+insightCards(f)+
    `<div class="grid two">${panel(L('Doanh thu thuần và tỷ lệ chiết khấu theo tháng','Monthly net sales and discount rate'),L('FY2017 · USD','FY2017 · USD'),chartDiv('ovMonthly'))}${panel(L('Cơ cấu doanh thu theo ngành','Net sales by department'),L('Kỳ đang chọn · USD','Selected period · USD'),chartDiv('ovDept'))}</div>`+
    panel(L('Doanh thu theo ngày','Daily net sales'),L('Kỳ đang chọn · USD','Selected period · USD'),chartDiv('ovDaily'))+
    panel(L('Mức sẵn sàng của chỉ tiêu tài chính','Financial KPI readiness'),L('Chỉ tiêu quan sát được và dữ liệu cần bổ sung','Observable KPIs and data required to complete them'),table('readiness',[L('Chỉ tiêu','KPI'),L('Trạng thái','Status'),L('Dữ liệu cần','Data required')],ready_,[0,r=>r[1],2]),csvButton('readiness'));
  barLine('ovMonthly',MON(),mo.map(m=>m.net),mo.map(m=>m.rate),{barName:L('Doanh thu thuần','Net sales'),lineName:L('Tỷ lệ chiết khấu','Discount rate')});
  horizontal('ovDept',R.depts,'sales',8);
  plot('ovDaily',[{type:'scatter',mode:'lines',x:R.days.map(d=>dayISO(d.day)),y:R.days.map(d=>d.sales),line:{color:C.green,width:2.2},fill:'tozeroy',fillcolor:'rgba(15,124,120,.08)',hovertemplate:'%{x}<br>%{y:,.0f}<extra></extra>'}],{yaxis:{tickformat:',.0f'}},260);
}

/* ---- Revenue analysis ---- */
function pgRevenue(){
  const I=INS(),mo=I.monthly,prior=R.prior,valid=prior&&prior.sales&&prior.baskets&&prior.aov;
  let vol=0,val=0;if(valid){vol=(R.baskets-prior.baskets)*(R.aov+prior.aov)/2;val=(R.aov-prior.aov)*(R.baskets+prior.baskets)/2;}
  const d=R.sales-(prior?.sales||0),deps=I.departments.filter(x=>x.growth!=null);
  const momRows=mo.map((m,i)=>[m.month,usd(m.net),i?pc(m.net/mo[i-1].net-1):'—',usd(m.baskets),usd(m.aov,2),pc(m.rate)]);
  const best=[...deps].filter(x=>x.share>=.01).sort((a,b)=>b.growth-a.growth)[0],peakM=[...mo].sort((a,b)=>b.net-a.net)[0],lowM=[...mo].sort((a,b)=>a.net-b.net)[0];
  $('content').innerHTML=heading('REVENUE',L('Phân tích doanh thu','Revenue Analysis'),L('Tăng trưởng, cơ cấu ngành và tính mùa vụ.','Growth, mix and seasonality.'),noActions)+
    `<div class="kpi-grid">${kpi(L('Doanh thu thuần','Net sales'),usd(R.sales),'USD','',prior?R.sales/prior.sales-1:null,'trend')}${kpi(L('Thay đổi tuyệt đối','Absolute change'),valid?(d>=0?'+':'')+usd(d):'—','USD',L('so với kỳ trước','vs prior period'),null,'flow')}${kpi(L('Do số giỏ','Volume effect'),valid?(vol>=0?'+':'')+usd(vol):'—','USD',L('thay đổi số giao dịch','change in transactions'),null,'basket')}${kpi(L('Do giá trị giỏ','Ticket effect'),valid?(val>=0?'+':'')+usd(val):'—','USD',L('thay đổi AOV','change in AOV'),null,'cube')}</div>`+
    `<div class="grid two">${panel(L('Cầu nối doanh thu','Net sales bridge'),valid?dayISO(prior.start)+' → '+dayISO(prior.end)+'  vs  '+dayISO(filters.start)+' → '+dayISO(filters.end):L('Cần kỳ trước đủ dữ liệu (ví dụ chọn Tháng 12)','Requires a complete prior period (e.g. choose December)'),valid?chartDiv('rvBridge'):'<div class="empty">—</div>')}${panel(L('Doanh thu thuần theo tháng','Monthly net sales'),L('FY2017 · USD · nhãn = tăng trưởng MoM','FY2017 · USD · labels = MoM growth'),chartDiv('rvMonthly'))}</div>`+
    `<div class="grid two">${panel(L('Tăng trưởng theo ngành: Q4 so với Q1','Department growth: Q4 vs Q1'),L('Ngành có doanh thu ≥ 1% tổng','Departments with ≥ 1% of net sales'),chartDiv('rvDeptGrowth'))}${panel(L('Mức doanh thu ngành theo tháng','Department sales index by month'),L('1,0 = trung bình của ngành trong năm','1.0 = department annual average'),chartDiv('rvHeat'))}</div>`+
    `<div class="grid two">${panel(L('Doanh thu theo tuần','Weekly net sales'),L('FY2017 · USD','FY2017 · USD'),chartDiv('rvWeekly'))}${panel(L('Mật độ doanh thu theo thứ và giờ','Sales density by weekday and hour'),L('FY2017 · USD','FY2017 · USD'),chartDiv('rvDow'))}</div>`+
    soWhat(L(best.name+' tăng nhanh nhất ('+pc(best.growth)+' Q4/Q1). Doanh thu cao nhất tháng '+peakM.month+' ('+usd(peakM.net)+' USD), thấp nhất tháng '+lowM.month+' ('+usd(lowM.net)+' USD): chênh '+pc(peakM.net/lowM.net-1,0)+'.',best.name+' grew fastest ('+pc(best.growth)+' Q4/Q1). Peak month '+peakM.month+' (USD '+usd(peakM.net)+'), low month '+lowM.month+' (USD '+usd(lowM.net)+'): a '+pc(peakM.net/lowM.net-1,0)+' spread.'))+
    panel(L('Bảng tháng','Monthly table'),'',table('rvTable',[L('Tháng','Month'),L('Doanh thu thuần (USD)','Net sales (USD)'),'MoM',L('Số giỏ','Baskets'),'AOV (USD)',L('Chiết khấu','Discount rate')],momRows,[0,1,2,3,4,5],{numeric:[1,2,3,4,5]}),csvButton('rvTable'));
  if(valid)plot('rvBridge',[{type:'waterfall',x:[L('Kỳ trước','Prior'),L('Số giỏ','Volume'),'AOV',L('Kỳ chọn','Selected')],measure:['absolute','relative','relative','total'],y:[prior.sales,vol,val,0],increasing:{marker:{color:C.green}},decreasing:{marker:{color:C.red}},totals:{marker:{color:C.blue}},hovertemplate:'%{x}<br>%{y:,.0f}<extra></extra>'}],{yaxis:{tickformat:',.0f',range:[Math.min(prior.sales,prior.sales+vol+val)*.9,Math.max(prior.sales,prior.sales+vol+val)*1.03]}},300);
  plot('rvMonthly',[{type:'bar',x:MON(),y:mo.map(m=>m.net),marker:{color:C.green,cornerradius:3},text:mo.map((m,i)=>i?(m.net/mo[i-1].net-1>=0?'+':'')+pc(m.net/mo[i-1].net-1):''),textposition:'outside',cliponaxis:false,hovertemplate:'%{x}<br>%{y:,.0f}<extra></extra>'}],{yaxis:{tickformat:',.0f',rangemode:'tozero'},margin:{l:56,r:20,t:24,b:32}},300);
  const dg=[...deps].filter(x=>x.share>=.01).sort((a,b)=>a.growth-b.growth);
  plot('rvDeptGrowth',[{type:'bar',orientation:'h',y:dg.map(x=>x.name),x:dg.map(x=>x.growth),marker:{color:dg.map(x=>x.growth>=0?C.green:C.red),cornerradius:3},text:dg.map(x=>(x.growth>=0?'+':'')+pc(x.growth)),textposition:'outside',cliponaxis:false,hovertemplate:'%{y}<br>%{x:.1%}<extra></extra>'}],{xaxis:{tickformat:'.0%'},yaxis:{type:'category',tickfont:{size:9}},margin:{l:110,r:50,t:8,b:28}},320);
  const dm=I.dept_month,z=dm.z.map(row=>{const m=row.reduce((s,v)=>s+v,0)/row.length;return row.map(v=>m?v/m:0);});
  plot('rvHeat',[{type:'heatmap',x:MON(),y:dm.depts,z,zmid:1,zmin:.5,zmax:1.5,colorscale:[[0,'#c2584f'],[.5,'#f4f6f8'],[1,'#0f7c78']],hovertemplate:'%{y} · %{x}<br>index %{z:.2f}<extra></extra>',colorbar:{thickness:8,len:.8}}],{yaxis:{type:'category',autorange:'reversed',tickfont:{size:9}},margin:{l:100,r:10,t:8,b:30}},320);
  plot('rvWeekly',[{type:'scatter',mode:'lines',x:I.weekly.slice(1).map(w=>w[0]),y:I.weekly.slice(1).map(w=>w[1]),line:{color:C.green,width:2.2},fill:'tozeroy',fillcolor:'rgba(15,124,120,.08)',hovertemplate:L('Tuần ','Week ')+'%{x}<br>%{y:,.0f}<extra></extra>'}],{xaxis:{title:L('Tuần trong năm','Week of year')},yaxis:{tickformat:',.0f',rangemode:'tozero'}},300);
  plot('rvDow',[{type:'heatmap',x:Array.from({length:24},(_,i)=>i),y:WKD(),z:I.weekday_hour,colorscale:[[0,'#f4f6f8'],[1,'#0f7c78']],hovertemplate:'%{y} %{x}h<br>%{z:,.0f}<extra></extra>',colorbar:{thickness:8,len:.8}}],{yaxis:{type:'category',autorange:'reversed'},xaxis:{title:L('Giờ','Hour'),dtick:3},margin:{l:36,r:10,t:8,b:40}},300);
}

/* ---- Net sales & discounts ---- */
function pgNetSales(){
  const I=INS(),g=I.gross_to_net,mo=I.monthly,br=I.brand,dp=I.departments,disc=g.gross-g.net,bands=I.discount_bands,bk=I.basket;
  const top=[...dp].filter(d=>d.share>=.02).sort((a,b)=>b.rate-a.rate);
  $('content').innerHTML=heading('NET SALES',L('Doanh thu thuần & chiết khấu','Net Sales & Discounts'),L('Từ doanh thu gộp đến doanh thu thuần · FY2017.','From gross sales to net sales · FY2017.'),noActions)+
    `<div class="kpi-grid six">${kpi(L('Doanh thu gộp','Gross sales'),k$(g.gross),'USD',L('trước chiết khấu','before discounts'),null,'trend')}${kpi(L('Tổng chiết khấu','Total discounts'),k$(disc),'USD',pc(g.rate)+L(' doanh thu gộp',' of gross'),null,'shield')}${kpi(L('Doanh thu thuần','Net sales'),k$(g.net),'USD',L('sau chiết khấu','after discounts'),null,'cube')}${kpi(L('Chiết khấu thẻ thành viên','Loyalty discount'),k$(g.retail),'USD',pc(g.retail/disc,0)+L(' tổng chiết khấu',' of discounts'),null,'users')}${kpi(L('Tỷ lệ dòng có chiết khấu','Promoted line rate'),pc(g.promo_line_share,0),'',L('số dòng hàng','of transaction lines'),null,'basket')}${kpi(L('Nhãn riêng / doanh thu','Private label share'),pc(g.private_share),'',L('doanh thu thuần','of net sales'),null,'cube')}</div>`+
    `<div class="grid two">${panel(L('Cầu nối doanh thu gộp sang thuần','Gross-to-net bridge'),'FY2017 · USD',chartDiv('nsBridge'))}${panel(L('Tỷ lệ chiết khấu theo tháng','Monthly discount rate'),L('Doanh thu gộp và thuần (cột), tỷ lệ chiết khấu (đường)','Gross and net (bars), discount rate (line)'),chartDiv('nsMonthly'))}</div>`+
    `<div class="grid two">${panel(L('Tỷ lệ chiết khấu theo ngành','Discount rate by department'),L('Ngành ≥ 2% doanh thu','Departments with ≥ 2% of net sales'),chartDiv('nsDept'))}${panel(L('Độ sâu chiết khấu theo hộ khách','Household discount depth'),L('Chi tiêu bình quân/hộ theo mức chiết khấu hưởng (USD)','Average spend per household by discount depth received (USD)'),chartDiv('nsBands'))}</div>`+
    panel(L('Nhãn riêng và thương hiệu quốc gia','Private label vs national brands'),'FY2017',table('nsBrand',[L('Nhãn','Brand'),L('Doanh thu thuần (USD)','Net sales (USD)'),L('Tỷ trọng','Share'),L('Tỷ lệ chiết khấu','Discount rate')],[[L('Nhãn riêng','Private'),usd(br.private_net),pc(br.private_net/g.net),pc(br.private_rate)],[L('Thương hiệu quốc gia','National'),usd(br.national_net),pc(br.national_net/g.net),pc(br.national_rate)]],[0,1,2,3],{numeric:[1,2,3]}))+
    soWhat(L('Chiết khấu '+k$(disc)+' USD ('+pc(g.rate)+' doanh thu gộp), '+pc(g.retail/disc,0)+' từ thẻ thành viên. '+top[0].name+' ('+pc(top[0].rate,0)+') và '+top[1].name+' ('+pc(top[1].rate,0)+') chiết khấu sâu nhất. Giỏ có coupon chỉ '+pc(bk.coupon_share)+' số giỏ nhưng AOV '+xx(bk.coupon_aov/bk.plain_aov)+' giỏ thường. Nhãn riêng chiết khấu thấp hơn '+N((br.national_rate-br.private_rate)*100,1)+' điểm %.','Discounts total USD '+k$(disc)+' ('+pc(g.rate)+' of gross), '+pc(g.retail/disc,0)+' from the loyalty card. '+top[0].name+' ('+pc(top[0].rate,0)+') and '+top[1].name+' ('+pc(top[1].rate,0)+') are discounted deepest. Coupon baskets are only '+pc(bk.coupon_share)+' of baskets but average '+xx(bk.coupon_aov/bk.plain_aov)+' the AOV of standard baskets. Private label is discounted '+N((br.national_rate-br.private_rate)*100,1)+' pp less.'));
  plot('nsBridge',[{type:'waterfall',x:[L('Doanh thu gộp','Gross sales'),L('Chiết khấu thẻ','Loyalty'),'Coupon',L('Coupon match','Coupon match'),L('Doanh thu thuần','Net sales')],measure:['absolute','relative','relative','relative','total'],y:[g.gross,-g.retail,-g.coupon,-g.match,0],decreasing:{marker:{color:C.amber}},totals:{marker:{color:C.blue}},text:[k$(g.gross),'−'+k$(g.retail),'−'+k$(g.coupon),'−'+k$(g.match),k$(g.net)],textposition:'outside',hovertemplate:'%{x}<br>%{y:,.0f}<extra></extra>'}],{yaxis:{tickformat:',.0f',range:[g.net*.8,g.gross*1.06]}},300);
  plot('nsMonthly',[{type:'bar',x:MON(),y:mo.map(m=>m.gross),name:L('Gộp','Gross'),marker:{color:'#b7c7d6',cornerradius:3}},{type:'bar',x:MON(),y:mo.map(m=>m.net),name:L('Thuần','Net'),marker:{color:C.green,cornerradius:3}},{type:'scatter',mode:'lines+markers',x:MON(),y:mo.map(m=>m.rate),yaxis:'y2',name:L('Tỷ lệ chiết khấu','Discount rate'),line:{color:C.amber,width:2.5},marker:{size:6},hovertemplate:'%{x}<br>%{y:.1%}<extra></extra>'}],{barmode:'group',yaxis:{tickformat:',.0f',rangemode:'tozero'},yaxis2:{overlaying:'y',side:'right',tickformat:'.0%',range:[0,.25],showgrid:false,tickfont:{size:9}},showlegend:true,legend:{orientation:'h',y:1.12,x:0},margin:{l:56,r:44,t:28,b:34}},300);
  plot('nsDept',[{type:'bar',orientation:'h',y:[...top].reverse().map(d=>d.name),x:[...top].reverse().map(d=>d.rate),marker:{color:[...top].reverse().map(d=>d.rate>g.rate?C.amber:C.green),cornerradius:3},text:[...top].reverse().map(d=>pc(d.rate)),textposition:'outside',cliponaxis:false,hovertemplate:'%{y}<br>%{x:.1%}<extra></extra>'}],{xaxis:{tickformat:'.0%',range:[0,.32]},yaxis:{type:'category',tickfont:{size:9}},shapes:[{type:'line',x0:g.rate,x1:g.rate,y0:-.5,y1:top.length-.5,line:{color:C.ink,dash:'dot',width:1}}],margin:{l:110,r:44,t:8,b:28}},320);
  plot('nsBands',[{type:'bar',x:bands.map(b=>b.band),y:bands.map(b=>b.spend),marker:{color:C.blue,cornerradius:3},text:bands.map(b=>usd(b.households)+L(' hộ',' HH')),textposition:'outside',cliponaxis:false,hovertemplate:'%{x}<br>USD %{y:,.0f}<extra></extra>'}],{xaxis:{title:L('Tỷ lệ chiết khấu của hộ','Household discount rate'),type:'category'},yaxis:{tickformat:',.0f',rangemode:'tozero'},margin:{l:56,r:20,t:24,b:44}},320);
}

/* ---- Customer & basket economics ---- */
function pgLoyalty(){
  const I=INS(),c=I.customers,mo=I.monthly.slice(1),fr=I.frequency,bb=I.basket_bands,b=I.basket,heavy=fr[fr.length-1];
  $('content').innerHTML=heading('CUSTOMERS',L('Kinh tế khách hàng & giỏ hàng','Customer & Basket Economics'),L('Mức tập trung, tần suất mua và quy mô giỏ · FY2017.','Concentration, purchase frequency and basket size · FY2017.'),noActions)+
    `<div class="kpi-grid six">${kpi(L('Hộ có mua','Active households'),usd(c.households),'',L('FY2017','FY2017'),null,'users')}${kpi(L('Chi tiêu/hộ (TB)','Spend / household (mean)'),usd(c.mean),'USD',L('trung vị ','median ')+usd(c.median),null,'cube')}${kpi('Top 10%',pc(c.top10),'',L('doanh thu thuần','of net sales'),null,'trend')}${kpi('Top 20%',pc(c.top20),'',L('doanh thu thuần','of net sales'),null,'trend')}${kpi(L('Hộ mua đa cửa hàng','Multi-store households'),pc(c.multi_store,0),'',L('mua từ 2 cửa hàng','shop at 2+ stores'),null,'store')}${kpi('AOV',usd(b.aov,2),'USD',L('trung vị ','median ')+usd(b.median,2),null,'basket')}</div>`+
    `<div class="grid two">${panel(L('Đường tập trung doanh thu (Lorenz)','Revenue concentration (Lorenz curve)'),L('% doanh thu tích lũy theo % hộ, từ hộ lớn nhất','Cumulative % of net sales by % of households, largest first'),chartDiv('lyLorenz'))}${panel(L('Tần suất mua','Purchase frequency'),L('Số hộ và tỷ trọng doanh thu theo số giỏ trong năm','Households and share of net sales by baskets per year'),chartDiv('lyFreq'))}</div>`+
    `<div class="grid two">${panel(L('Hộ mới và hộ quay lại','New vs returning households'),L('Từ tháng 2; tháng 1 là điểm khởi đầu của dữ liệu','From February; January is the panel start'),chartDiv('lyNew'))}${panel(L('Quy mô giỏ hàng','Basket size'),L('Số dòng hàng/giỏ: % số giỏ và % doanh thu','Lines per basket: % of baskets and % of net sales'),chartDiv('lyBasket'))}</div>`+
    panel(L('Giỏ có coupon và giỏ thường','Coupon vs standard baskets'),'FY2017',table('lyCoupon',[L('Loại giỏ','Basket type'),L('Tỷ trọng số giỏ','Share of baskets'),'AOV (USD)',L('Dòng hàng/giỏ','Lines / basket')],[[L('Có coupon','With coupon'),pc(b.coupon_share),usd(b.coupon_aov,2),N(b.coupon_lines,1)],[L('Thường','Standard'),pc(1-b.coupon_share),usd(b.plain_aov,2),N(b.plain_lines,1)]],[0,1,2,3],{numeric:[1,2,3]}))+
    soWhat(L('Top 10% hộ tạo '+pc(c.top10)+' doanh thu, 50% thấp nhất '+pc(c.bottom50)+'. '+usd(heavy.households)+' hộ mua từ 40 giỏ/năm tạo '+pc(heavy.share,0)+' doanh thu. Giỏ từ 21 dòng hàng chiếm '+pc(bb[4].share+bb[5].share,0)+' doanh thu.','Top 10% of households drive '+pc(c.top10)+' of net sales; the bottom 50% only '+pc(c.bottom50)+'. '+usd(heavy.households)+' households with 40+ baskets/year generate '+pc(heavy.share,0)+'. Baskets of 21+ lines are '+pc(bb[4].share+bb[5].share,0)+' of net sales.'));
  plot('lyLorenz',[{type:'scatter',mode:'lines',x:[0,...c.lorenz.map(p=>p[0])],y:[0,...c.lorenz.map(p=>p[1])],line:{color:C.green,width:2.5},fill:'tozeroy',fillcolor:'rgba(15,124,120,.08)',name:L('Thực tế','Actual'),hovertemplate:'%{x:.0%} HH → %{y:.1%}<extra></extra>'},{type:'scatter',mode:'lines',x:[0,1],y:[0,1],line:{color:C.gray,dash:'dot'},hoverinfo:'skip'}],{xaxis:{tickformat:'.0%',title:L('% hộ (lớn nhất trước)','% of households (largest first)')},yaxis:{tickformat:'.0%',range:[0,1]}},300);
  plot('lyFreq',[{type:'bar',x:fr.map(f=>f.band),y:fr.map(f=>f.households),name:L('Số hộ','Households'),marker:{color:'#b7c7d6',cornerradius:3}},{type:'scatter',mode:'lines+markers',x:fr.map(f=>f.band),y:fr.map(f=>f.share),yaxis:'y2',name:L('% doanh thu','% of net sales'),line:{color:C.amber,width:2.5},marker:{size:6},hovertemplate:'%{x}<br>%{y:.1%}<extra></extra>'}],{xaxis:{type:'category',title:L('Số giỏ/năm','Baskets per year')},yaxis:{tickformat:',.0f'},yaxis2:{overlaying:'y',side:'right',tickformat:'.0%',showgrid:false,range:[0,1]},showlegend:true,legend:{orientation:'h',y:1.12,x:0},margin:{l:50,r:44,t:28,b:44}},300);
  plot('lyNew',[{type:'bar',x:mo.map((m,i)=>MON()[i+1]),y:mo.map(m=>m.repeat_hh),name:L('Quay lại','Returning'),marker:{color:C.green}},{type:'bar',x:mo.map((m,i)=>MON()[i+1]),y:mo.map(m=>m.new_hh),name:L('Mới','New'),marker:{color:C.amber}}],{barmode:'stack',yaxis:{tickformat:',.0f'},showlegend:true,legend:{orientation:'h',y:1.12,x:0},margin:{l:50,r:20,t:28,b:34}},300);
  plot('lyBasket',[{type:'bar',x:bb.map(x=>x.band),y:bb.map(x=>x.baskets/b.count),name:L('% số giỏ','% of baskets'),marker:{color:'#b7c7d6',cornerradius:3}},{type:'bar',x:bb.map(x=>x.band),y:bb.map(x=>x.share),name:L('% doanh thu','% of net sales'),marker:{color:C.green,cornerradius:3}}],{barmode:'group',xaxis:{type:'category',title:L('Số dòng hàng trong giỏ','Lines per basket')},yaxis:{tickformat:'.0%'},showlegend:true,legend:{orientation:'h',y:1.12,x:0},margin:{l:50,r:20,t:28,b:44}},300);
}

/* ---- Data quality & definitions ---- */
function pgQuality(){
  const m=D.meta,q=D.insights.quality||{};
  const scope=[
    [L('Giao dịch trong phạm vi','Transactions in scope'),usd(m.rows)],[L('Doanh thu thuần thô (USD)','Raw net sales (USD)'),usd(m.rawSalesCents/100,2)],
    [L('Hộ khách','Households'),usd(q.households||2469)],[L('Cửa hàng','Stores'),usd(q.stores||457)],[L('Giỏ hàng','Baskets'),usd(q.baskets||155762)],
    [L('Dòng ngoài kỳ (loại)','Out-of-period lines (excluded)'),usd(q.out_of_scope||534)],[L('Dòng thiếu mã SKU','Lines without SKU mapping'),usd(q.unmatched||4833)+' ('+pc(q.unmatched_rate||.0033,2)+')'],
    [L('Dòng không dương (giữ ở dữ liệu gốc)','Non-positive lines (kept in raw data)'),usd(q.excluded||11266)],[L('Ngày thiếu dữ liệu','Missing date'),'2017-12-25'],[L('Trùng lặp','Duplicates'),'0']
  ];
  const defs=[
    [L('Doanh thu thuần','Net sales'),L('sales_value: số tiền doanh nghiệp thực nhận trên mỗi dòng, sau chiết khấu.','sales_value: amount received by the retailer per line, after discounts.')],
    [L('Doanh thu gộp','Gross sales'),L('Doanh thu thuần + chiết khấu thẻ + coupon + coupon match.','Net sales + loyalty + coupon + coupon-match discounts.')],
    [L('Tỷ lệ chiết khấu','Discount rate'),L('Tổng chiết khấu / doanh thu gộp.','Total discounts / gross sales.')],
    [L('AOV','AOV'),L('Doanh thu thuần / số giỏ (basket_id).','Net sales / number of baskets (basket_id).')],
    [L('Hộ hoạt động','Active household'),L('Hộ có ít nhất một dòng mua dương trong kỳ.','Household with at least one positive purchase line in the period.')],
    [L('RFM','RFM'),L('Recency (ngày từ lần mua cuối), Frequency (số giỏ), Monetary (chi tiêu).','Recency (days since last purchase), Frequency (baskets), Monetary (spend).')],
    [L('Lift','Lift'),L('Xác suất mua cặp A–B so với mức kỳ vọng nếu độc lập; > 1 là liên kết dương.','Co-purchase probability of A–B vs independence; > 1 means positive association.')],
    [L('WAPE','WAPE'),L('Σ|thực tế − dự báo| / Σ|thực tế|; thấp hơn là tốt hơn.','Σ|actual − forecast| / Σ|actual|; lower is better.')],
    [L('Bias','Bias'),L('(Dự báo − thực tế) / Σ thực tế; dương = dự báo cao hơn thực tế.','(Forecast − actual) / Σ actual; positive = forecast above actual.')],
    [L('Precision / Recall / Lift@20%','Precision / Recall / Lift@20%'),L('Trong top 20% điểm rủi ro: tỷ lệ chọn đúng, tỷ lệ khách ngừng mua bắt được, và mức vượt chọn ngẫu nhiên.','In the top 20% of risk scores: hit rate, share of lapsing households captured, and uplift over random selection.')],
    [L('Hòa vốn','Break-even'),L('Chi phí cố định / tỷ lệ đóng góp.','Fixed costs / contribution margin.')],
    [L('CCC','CCC'),L('DIO + DSO − DPO.','DIO + DSO − DPO.')]
  ];
  $('content').innerHTML=heading('DATA',L('Chất lượng dữ liệu & định nghĩa','Data Quality & Definitions'),L('Phạm vi, kiểm tra đối soát và định nghĩa chỉ tiêu.','Scope, reconciliation checks and KPI definitions.'),noActions)+
    `<div class="grid two">${panel(L('Phạm vi và đối soát','Scope & reconciliation'),L('Complete Journey · FY2017','Complete Journey · FY2017'),table('qScope',[L('Hạng mục','Item'),L('Giá trị','Value')],scope,[0,1],{numeric:[1]}),csvButton('qScope'))}${panel(L('Phạm vi sử dụng','Scope of use'),'',`<ul class="info-list"><li><h3>${L('Mẫu hộ theo dõi','Household panel')}</h3><p>${L('Doanh thu là của nhóm hộ được theo dõi, không phải doanh thu toàn chuỗi.','Sales reflect the tracked household panel, not total chain revenue.')}</p></li><li><h3>${L('Chỉ tiêu cần dữ liệu doanh nghiệp','KPIs requiring client data')}</h3><p>${L('Biên gộp, EBITDA, vòng quay tồn, CCC, LFL cần giá vốn, OPEX, tồn kho, công nợ.','Gross margin, EBITDA, inventory turns, CCC and LFL need COGS, OPEX, inventory and payables.')}</p></li><li><h3>${L('Ngày 25/12','25 December')}</h3><p>${L('Không có bản ghi trong dữ liệu nguồn.','No records in the source data.')}</p></li></ul>`)}</div>`+
    panel(L('Định nghĩa chỉ tiêu','KPI definitions'),'',table('qDefs',[L('Chỉ tiêu','KPI'),L('Định nghĩa','Definition')],defs,[0,1]),csvButton('qDefs'));
}
