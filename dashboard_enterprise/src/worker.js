/* Every filtered total scans the full in-scope transaction columns. No sampling. */
let C,DICT,META,PM;
const types={uint8:Uint8Array,uint16:Uint16Array,uint32:Uint32Array,int32:Int32Array,float32:Float32Array};
function matches(i,f){return C.day[i]>=f.start&&C.day[i]<=f.end&&(f.store<0||C.store[i]===f.store)&&(f.dept<0||C.dept[i]===f.dept)&&(f.category<0||C.category[i]===f.category)&&(f.brand<0||C.brand[i]===f.brand);}
function groups(size){return {sales:new Float64Array(size),lines:new Uint32Array(size),baskets:Array.from({length:size},()=>new Set()),customers:Array.from({length:size},()=>new Set())};}
function compact(g,names){return names.map((name,i)=>({index:i,name,sales:g.sales[i]/100,lines:g.lines[i],baskets:g.baskets[i].size,customers:g.customers[i].size})).filter(x=>x.lines).sort((a,b)=>b.sales-a.sales);}
function aggregate(f){
  const daily=groups(365),monthly=groups(12),dept=groups(DICT.department.length),store=groups(DICT.store_id.length),category=groups(DICT.product_category.length),brand=groups(DICT.brand.length);
  const skus=new Map(),customers=new Map(),baskets=new Set(),positiveBaskets=new Set(),weekSales=new Float64Array(7),hours=new Float64Array(24),discountSales=[0,0],discountLines=[0,0];
  let cents=0,lines=0,excludedLines=0,excludedCents=0;
  const startDate=new Date(Date.UTC(2017,0,1+f.start)),endDate=new Date(Date.UTC(2017,0,1+f.end)),calendarAligned=startDate.getUTCDate()===1&&endDate.getUTCDate()===new Date(Date.UTC(2017,endDate.getUTCMonth()+1,0)).getUTCDate(),monthCount=endDate.getUTCMonth()-startDate.getUTCMonth()+1;
  const priorEnd=f.start-1,priorStart=calendarAligned?Math.round((Date.UTC(2017,startDate.getUTCMonth()-monthCount,1)-Date.UTC(2017,0,1))/86400000):priorEnd-(f.end-f.start),priorComplete=priorStart>=0;let priorCents=0,priorBaskets=new Set();
  for(let i=0;i<META.rows;i++){
    if(priorComplete&&C.day[i]>=priorStart&&C.day[i]<=priorEnd&&(f.store<0||C.store[i]===f.store)&&(f.dept<0||C.dept[i]===f.dept)&&(f.category<0||C.category[i]===f.category)&&(f.brand<0||C.brand[i]===f.brand)){priorCents+=C.sales[i];priorBaskets.add(C.basket[i]);}
    if(!matches(i,f))continue;
    const val=C.sales[i],b=C.basket[i],h=C.customer[i],day=C.day[i];cents+=val;lines++;baskets.add(b);
    const month=new Date(Date.UTC(2017,0,1+day)).getUTCMonth();
    for(const [g,k] of [[daily,day],[monthly,month],[dept,C.dept[i]],[store,C.store[i]],[category,C.category[i]],[brand,C.brand[i]]]){g.sales[k]+=val;g.lines[k]++;g.baskets[k].add(b);g.customers[k].add(h);}
    weekSales[(day+0)%7]+=val;hours[C.hour[i]]+=val;
    let sku=skus.get(C.sku[i]);if(!sku){sku={index:C.sku[i],sales:0,lines:0,quantity:0,baskets:new Set()};skus.set(C.sku[i],sku);}sku.sales+=val;sku.lines++;sku.quantity+=C.quantity[i];sku.baskets.add(b);
    const good=C.quantity[i]>0&&val>0;
    if(!good){excludedLines++;excludedCents+=val;continue;}
    positiveBaskets.add(b);const discounted=+(C.retailDiscount[i]!==0||C.couponDiscount[i]!==0||C.matchDiscount[i]!==0);discountSales[discounted]+=val;discountLines[discounted]++;
    let cu=customers.get(h);if(!cu){cu={index:h,sales:0,baskets:new Set(),stores:new Set(),categories:new Set(),first:day,last:day,discounted:0,lines:0};customers.set(h,cu);}
    cu.sales+=val;cu.baskets.add(b);cu.stores.add(C.store[i]);cu.categories.add(C.category[i]);cu.first=Math.min(cu.first,day);cu.last=Math.max(cu.last,day);cu.discounted+=discounted;cu.lines++;
  }
  const customerRows=[...customers.values()].map(v=>({index:v.index,id:DICT.household_id[v.index],sales:v.sales/100,frequency:v.baskets.size,stores:v.stores.size,categories:v.categories.size,recency:f.end-v.last,first:v.first,last:v.last,discountShare:v.discounted/v.lines})).sort((a,b)=>b.sales-a.sales);
  const skuRows=[...skus.values()].map(v=>({index:v.index,id:DICT.product_id[v.index],type:PM[v.index][0],pack:PM[v.index][1],sales:v.sales/100,lines:v.lines,quantity:v.quantity,baskets:v.baskets.size,dept:DICT.department[PM[v.index][2]],category:DICT.product_category[PM[v.index][3]],brand:DICT.brand[PM[v.index][4]]})).sort((a,b)=>b.sales-a.sales);
  let cumulative=0;for(const row of skuRows){row.share=lines?row.sales/(cents/100):0;row.ABC=cumulative<.8?'A':cumulative<.95?'B':'C';cumulative+=Math.max(0,row.share);row.cumulative=cumulative;}
  const days=Array.from({length:365},(_,i)=>({day:i,sales:daily.sales[i]/100,lines:daily.lines[i],baskets:daily.baskets[i].size,customers:daily.customers[i].size})).filter(x=>x.day>=f.start&&x.day<=f.end);
  const top20=customerRows.slice(0,Math.ceil(customerRows.length*.2)).reduce((s,v)=>s+v.sales,0),totalPositive=customerRows.reduce((s,v)=>s+v.sales,0);
  return {filter:f,lines,sales:cents/100,baskets:baskets.size,customers:customerRows.length,rawCustomers:new Set(customerRows.map(v=>v.index)).size,aov:baskets.size?cents/100/baskets.size:null,excludedLines,excludedSales:excludedCents/100,positiveSales:totalPositive,positiveBaskets:positiveBaskets.size,days,months:compact(monthly,Array.from({length:12},(_,i)=>`2017-${String(i+1).padStart(2,'0')}`)).sort((a,b)=>a.index-b.index),depts:compact(dept,DICT.department),stores:compact(store,DICT.store_id),categories:compact(category,DICT.product_category),brands:compact(brand,DICT.brand),skus:skuRows,customerRows,weekSales:[...weekSales].map(v=>v/100),hours:[...hours].map(v=>v/100),discountSales:discountSales.map(v=>v/100),discountLines,top20Share:totalPositive?top20/totalPositive:null,prior:priorComplete?{sales:priorCents/100,baskets:priorBaskets.size,aov:priorBaskets.size?priorCents/100/priorBaskets.size:null,start:priorStart,end:priorEnd,calendarAligned}:null,missingDays:META.missingDays.filter(d=>d>=f.start&&d<=f.end)};
}
function rowPage(f,offset,limit,search,entity){let seen=0;const out=[];search=(search||'').trim().toLowerCase();for(let i=0;i<META.rows;i++){if(!matches(i,f))continue;const sku=DICT.product_id[C.sku[i]],basket=DICT.basket_id[C.basket[i]],customer=DICT.household_id[C.customer[i]],type=PM[C.sku[i]][0];if(entity&&({sku,basket,customer}[entity.type]!==String(entity.value)))continue;if(search&&![sku,basket,customer,type].some(x=>String(x).toLowerCase().includes(search)))continue;if(seen++<offset)continue;out.push({row:i+1,day:C.day[i],hour:C.hour[i],store:DICT.store_id[C.store[i]],basket,customer,sku,type,quantity:C.quantity[i],sales:C.sales[i]/100,department:DICT.department[C.dept[i]],category:DICT.product_category[C.category[i]],retailDiscount:C.retailDiscount[i]/100,couponDiscount:C.couponDiscount[i]/100,matchDiscount:C.matchDiscount[i]/100});if(out.length===limit)break;}return {rows:out,offset,hasMore:out.length===limit};}
onmessage=async e=>{const {id,type,payload}=e.data;try{
  if(type==='init'){META=payload.meta;DICT=payload.dictionaries;PM=payload.productMeta;const bytes=Uint8Array.from(atob(payload.packed),c=>c.charCodeAt(0));if(!self.DecompressionStream)throw Error('Trình duyệt cần hỗ trợ DecompressionStream. Hãy dùng Chrome hoặc Edge hiện hành.');const buffer=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();C={};for(const [name,c]of Object.entries(payload.columns))C[name]=new types[c.dtype](buffer,c.offset,c.length);let total=0;for(let i=0;i<META.rows;i++)total+=C.sales[i];if(total!==META.rawSalesCents)throw Error('Đối soát dữ liệu trong trình duyệt không khớp.');postMessage({id,type:'ready',result:{rows:META.rows,sales:total/100}});}
  else if(type==='aggregate')postMessage({id,result:aggregate(payload)});
  else if(type==='uploadHeaders')postMessage({id,result:await uploadHeaders(payload.file)});
  else if(type==='uploadValidate')postMessage({id,result:await validateUpload(payload)});
  else if(type==='uploadScore')postMessage({id,result:scoreUpload(payload)});
  else if(type==='uploadSample')postMessage({id,result:sampleUploadCSV()});
  else if(type==='uploadClear'){uploadDraft=null;uploadCommitted=null;postMessage({id,result:{cleared:true}});}
  else if(type==='rows')postMessage({id,result:rowPage(payload.filters,payload.offset,payload.limit,payload.search,payload.entity)});
}catch(error){postMessage({id,error:error.message,stack:error.stack});}};
