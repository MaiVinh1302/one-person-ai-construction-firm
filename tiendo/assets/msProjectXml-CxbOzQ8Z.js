import{n as e}from"./rolldown-runtime-Dd_uD5pT.js";var t=e({durationToMsFormat:()=>o,exportMsProjectXml:()=>l,parseMsDuration:()=>s,parseMsProjectXml:()=>f});function n(){if(typeof globalThis<`u`&&globalThis.DOMParser!==void 0)return new globalThis.DOMParser;if(typeof window<`u`&&window.DOMParser!==void 0)return new window.DOMParser;try{let{DOMParser:e}=Function(`moduleName`,`return require(moduleName)`)(`@xmldom/xmldom`);return new e}catch{throw Error(`Không tìm thấy DOMParser trong môi trường hiện tại.`)}}function r(e){return(e||``).replace(/&/g,`&amp;`).replace(/</g,`&lt;`).replace(/>/g,`&gt;`).replace(/"/g,`&quot;`).replace(/'/g,`&apos;`)}function i(e){switch(e){case`FF`:return 0;case`FS`:return 1;case`SF`:return 2;case`SS`:return 3;default:return 1}}function a(e){switch(e){case 0:return`FF`;case 1:return`FS`;case 2:return`SF`;case 3:return`SS`;default:return`FS`}}function o(e,t=480){let n=Math.round(e*t);return`PT${Math.floor(n/60)}H${n%60}M0S`}function s(e,t=480){if(!e)return{days:1,rawDays:1,isFractional:!1};let n=e.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/i);if(n){let e=parseInt(n[1]||`0`,10),r=parseInt(n[2]||`0`,10),i=parseInt(n[3]||`0`,10),a=(e*60+r+i/60)/t,o=Math.max(0,Math.ceil(a));return{days:o,rawDays:a,isFractional:a>0&&Math.abs(o-a)>.001}}let r=parseFloat(e.replace(/[^\d.-]/g,``));if(!isNaN(r)){let e=(r>500?r/10:r)/t,n=Math.max(0,Math.ceil(e));return{days:n,rawDays:e,isFractional:e>0&&Math.abs(n-e)>.001}}return{days:1,rawDays:1,isFractional:!1}}var c={1:`Càng muộn càng tốt (As Late As Possible)`,2:`Phải bắt đầu vào ngày (Must Start On)`,3:`Phải kết thúc vào ngày (Must Finish On)`,4:`Bắt đầu không sớm hơn (Start No Earlier Than)`,5:`Bắt đầu không muộn hơn (Start No Later Than)`,6:`Kết thúc không sớm hơn (Finish No Earlier Than)`,7:`Kết thúc không muộn hơn (Finish No Later Than)`};function l(e,t){let n=new Map;e.tasks.forEach((e,t)=>{n.set(e.id,t+1)});let a=new Date().toISOString(),s=e.startDate||a.slice(0,10),c=t?.projectEndDate||e.startDate||a.slice(0,10),l=`${s}T08:00:00`,u=`${c}T17:00:00`,d=e.calendar?.workDays||[1,2,3,4,5,6],f=e.calendar?.holidays||[],p=0;if(e.tasks.length>0){let t=e.tasks.reduce((e,t)=>e+(t.durationDays||0),0);if(t>0){let n=e.tasks.reduce((e,t)=>e+(t.durationDays||0)*(t.percentComplete||0),0);p=Math.round(n/t)}}let m=t?.totalDurationDays??0,h=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
`;h+=`<Project xmlns="http://schemas.microsoft.com/project">
`,h+=`  <SaveVersion>14</SaveVersion>
`,h+=`  <Name>${r(e.name||`Du-an-tien-do`)}</Name>\n`,h+=`  <Title>${r(e.name||``)}</Title>\n`,h+=`  <Company>${r(e.contractor||`Nhà thầu thi công`)}</Company>\n`,h+=`  <Manager>${r(e.siteManager||``)}</Manager>\n`,h+=`  <StartDate>${l}</StartDate>\n`,h+=`  <FinishDate>${u}</FinishDate>\n`,h+=`  <CurrentDate>${a}</CurrentDate>\n`,h+=`  <MinutesPerDay>480</MinutesPerDay>
`,h+=`  <DaysPerMonth>20</DaysPerMonth>
`,h+=`  <DefaultStartTime>08:00:00</DefaultStartTime>
`,h+=`  <DefaultFinishTime>17:00:00</DefaultFinishTime>
`,h+=`  <CalendarUID>1</CalendarUID>
`,h+=`  <Calendars>
`,h+=`    <Calendar>
`,h+=`      <UID>1</UID>
`,h+=`      <Name>Standard</Name>
`,h+=`      <IsBaseCalendar>1</IsBaseCalendar>
`,h+=`      <WeekDays>
`;for(let e=1;e<=7;e++){let t=(e-1)%7,n=d.includes(t);h+=`        <WeekDay>
`,h+=`          <DayType>${e}</DayType>\n`,h+=`          <DayWorking>${+!!n}</DayWorking>\n`,n&&(h+=`          <WorkingTimes>
`,h+=`            <WorkingTime>
`,h+=`              <FromTime>08:00:00</FromTime>
`,h+=`              <ToTime>12:00:00</ToTime>
`,h+=`            </WorkingTime>
`,h+=`            <WorkingTime>
`,h+=`              <FromTime>13:00:00</FromTime>
`,h+=`              <ToTime>17:00:00</ToTime>
`,h+=`            </WorkingTime>
`,h+=`          </WorkingTimes>
`),h+=`        </WeekDay>
`}return h+=`      </WeekDays>
`,f.length>0&&(h+=`      <Exceptions>
`,f.forEach(e=>{h+=`        <Exception>
`,h+=`          <EnteredByOccurrences>0</EnteredByOccurrences>
`,h+=`          <TimePeriod>
`,h+=`            <FromDate>${e}T00:00:00</FromDate>\n`,h+=`            <ToDate>${e}T23:59:59</ToDate>\n`,h+=`          </TimePeriod>
`,h+=`          <Occurrences>1</Occurrences>
`,h+=`          <Name>Nghỉ lễ</Name>
`,h+=`          <Type>1</Type>
`,h+=`          <DayWorking>0</DayWorking>
`,h+=`        </Exception>
`}),h+=`      </Exceptions>
`),h+=`    </Calendar>
`,h+=`  </Calendars>
`,h+=`  <Tasks>
`,h+=`    <Task>
`,h+=`      <UID>0</UID>
`,h+=`      <ID>0</ID>
`,h+=`      <Name>${r(e.name||`Dự án`)}</Name>\n`,h+=`      <Type>0</Type>
`,h+=`      <IsNull>0</IsNull>
`,h+=`      <OutlineLevel>0</OutlineLevel>
`,h+=`      <Summary>1</Summary>
`,h+=`      <Duration>${o(m,480)}</Duration>\n`,h+=`      <DurationFormat>7</DurationFormat>
`,h+=`      <Start>${l}</Start>\n`,h+=`      <Finish>${u}</Finish>\n`,h+=`      <PercentComplete>${p}</PercentComplete>\n`,h+=`    </Task>
`,e.tasks.forEach((e,a)=>{let s=a+1,c=e.kind===`summary`,d=e.kind===`milestone`,f=o(e.durationDays,480),p=(e.level||0)+1,m=t?.taskMap?.get(e.id),g=m?.startDate?`${m.startDate}T08:00:00`:l,_=m?.endDate?`${m.endDate}T17:00:00`:u;h+=`    <Task>
`,h+=`      <UID>${s}</UID>\n`,h+=`      <ID>${s}</ID>\n`,h+=`      <Name>${r(e.name)}</Name>\n`,h+=`      <Type>0</Type>
`,h+=`      <IsNull>0</IsNull>
`,h+=`      <OutlineLevel>${p}</OutlineLevel>\n`,h+=`      <Summary>${+!!c}</Summary>\n`,h+=`      <Milestone>${+!!d}</Milestone>\n`,h+=`      <Duration>${f}</Duration>\n`,h+=`      <DurationFormat>7</DurationFormat>
`,h+=`      <Start>${g}</Start>\n`,h+=`      <Finish>${_}</Finish>\n`,h+=`      <PercentComplete>${Math.round(e.percentComplete||0)}</PercentComplete>\n`,e.note&&(h+=`      <Notes>${r(e.note)}</Notes>\n`),e.links&&e.links.length>0&&e.links.forEach(e=>{let t=n.get(e.fromId);if(t){let n=i(e.type),r=Math.round((e.lag||0)*480*10);h+=`      <PredecessorLink>
`,h+=`        <PredecessorUID>${t}</PredecessorUID>\n`,h+=`        <Type>${n}</Type>\n`,h+=`        <CrossProject>0</CrossProject>
`,h+=`        <LinkLag>${r}</LinkLag>\n`,h+=`        <LagFormat>7</LagFormat>
`,h+=`      </PredecessorLink>
`}}),h+=`    </Task>
`}),h+=`  </Tasks>
`,h+=`</Project>
`,h}function u(e,t){let n=e&&e.getElementsByTagName?e.getElementsByTagName(t):[];return n.length>0?(n[0].textContent||``).trim():``}function d(e,t){let n=e&&e.getElementsByTagName?e.getElementsByTagName(t):[];return Array.from(n)}function f(e){let t=n().parseFromString(e,`text/xml`),r=t.getElementsByTagName(`parsererror`);if(r.length>0)throw Error(`File XML không hợp lệ: ${r[0].textContent||`Lỗi cú pháp XML`}`);let i=t.getElementsByTagName(`Project`);if(i.length===0)throw Error(`Không tìm thấy thẻ gốc <Project> trong file XML.`);let o=i[0],l=u(o,`Title`)||u(o,`Name`)||`Dự án nhập từ MS Project`,f=u(o,`StartDate`),p=f?f.slice(0,10):void 0,m=u(o,`MinutesPerDay`),h=m&&parseFloat(m)||480,g=[],_=[],v,y=d(t,`Calendar`);if(y.length>0){let e=y.find(e=>u(e,`IsBaseCalendar`)===`1`)||y[0],t=d(e,`WeekDay`),n=[];t.forEach(e=>{let t=parseInt(u(e,`DayType`)||`0`,10),r=u(e,`DayWorking`)===`1`;if(t>=1&&t<=7&&r){let e=(t-1)%7;n.includes(e)||n.push(e)}});let r=[];d(e,`Exception`).forEach(e=>{let t=u(e,`DayWorking`)===`0`,n=u(e,`FromDate`);if(t&&n&&n.length>=10){let e=n.slice(0,10);r.includes(e)||r.push(e)}}),n.length>0&&(n.sort((e,t)=>e-t),v={workDays:n,holidays:r})}let b=d(t,`Resource`);b.length>0&&g.push(`Đã bỏ qua ${b.length} danh mục nguồn lực từ MS Project (tiến độ dùng danh mục riêng).`);let x=d(t,`Task`),S=new Map,C=[],w=0;x.forEach(e=>{if(u(e,`IsNull`)===`1`)return;let t=u(e,`UID`)||``,n=parseInt(u(e,`OutlineLevel`)||`1`,10);if(t===`0`||n===0)return;let r=u(e,`Name`)||`Công việc UID ${t}`,i=u(e,`Summary`)===`1`,o=u(e,`Milestone`)===`1`,l=u(e,`Duration`)||``,f=0;if(!o){let e=s(l,h);f=e.days,e.isFractional&&_.push(`Công việc "${r}": Thời lượng lẻ (${e.rawDays.toFixed(1).replace(`.`,`,`)} ngày) được làm tròn lên ${f} ngày.`)}let p=i?`summary`:o||f===0?`milestone`:`task`,m=parseInt(u(e,`ConstraintType`)||`0`,10);if(m>0){let e=c[m]||`Loại ${m}`;g.push(`Ràng buộc ngày (${e}) ở công việc "${r}".`)}let v=u(e,`ActualStart`),y=u(e,`ActualFinish`);(v&&v!==`0000-00-00`||y&&y!==`0000-00-00`)&&g.push(`Ngày thực tế (ActualStart/ActualFinish) ở công việc "${r}".`);let b=parseFloat(u(e,`PercentComplete`)||`0`),x=isNaN(b)?0:Math.min(100,Math.max(0,b)),T=u(e,`Notes`)||``,E=d(e,`PredecessorLink`),D=[];E.forEach(e=>{let t=u(e,`PredecessorUID`),n=parseInt(u(e,`Type`)||`1`,10),r=parseFloat(u(e,`LinkLag`)||`0`)/(h*10),i=Math.ceil(r);Math.abs(i-r)>.001&&r!==0&&_.push(`Độ trễ liên kết tới UID ${t} (${r.toFixed(1).replace(`.`,`,`)} ngày) được làm tròn lên ${i} ngày.`),t&&t!==`0`&&(D.push({predUid:t,type:a(n),lag:isNaN(i)?0:i}),w++)});let O=`msp-${C.length+1}-${Date.now()}`;S.set(t,O),C.push({uid:t,id:O,name:r,outlineLevel:n,kind:p,durationDays:f,percentComplete:x,note:T,predecessors:D})});let T=C.reduce((e,t)=>Math.min(e,t.outlineLevel),1),E=C.map(e=>{let t=[];e.predecessors.forEach(n=>{let r=S.get(n.predUid);r&&r!==e.id&&t.push({fromId:r,type:n.type,lag:n.lag})});let n=Math.max(0,e.outlineLevel-T);return{id:e.id,level:n,kind:e.kind,name:e.name,durationDays:e.durationDays,links:t,resources:[],percentComplete:e.percentComplete,note:e.note}});return{projectName:l,startDate:p,calendar:v,tasksCount:E.length,linksCount:w,tasks:E,ignoredItems:g,roundingWarnings:_}}export{t as n,f as r,l as t};