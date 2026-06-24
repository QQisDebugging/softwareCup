import{d as w,e as y,t as k,n as x,o as _}from"./iframe-B76myD0L.js";import"./preload-helper-Dp1pzeXC.js";const e=w({__name:"StatusPill",props:{status:{type:[String,Number,Boolean,null]},tone:{}},setup(o){return(v,R)=>(_(),y("span",{class:x(["status-pill",o.tone||"info"])},k(o.status??"-"),3))}});e.__docgenInfo=Object.assign({displayName:e.name??e.__name},{exportName:"default",displayName:"StatusPill",description:"",tags:{},props:[{name:"status",required:!1,type:{name:"union",elements:[{name:"string"},{name:"number"},{name:"boolean"},{name:"null"}]}},{name:"tone",required:!1,type:{name:"union",elements:[{name:'"ok"'},{name:'"warn"'},{name:'"danger"'},{name:'"info"'},{name:'"muted"'}]}}],sourceFiles:["D:/softwareCup/frontend/src/components/StatusPill.vue"]});const q={title:"Product/StatusPill",component:e,tags:["autodocs"],argTypes:{tone:{control:"select",options:["ok","warn","danger","info","muted"]}},args:{status:"可发布",tone:"ok"}},t={args:{status:"可发布",tone:"ok"}},a={args:{status:"待复核",tone:"warn"}},s={args:{status:"需处理",tone:"danger"}},n={render:()=>({components:{StatusPill:e},template:`
      <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <StatusPill status="可发布" tone="ok" />
        <StatusPill status="待复核" tone="warn" />
        <StatusPill status="需处理" tone="danger" />
        <StatusPill status="生成中" tone="info" />
        <StatusPill status="未开始" tone="muted" />
      </div>
    `})};var r,l,u;t.parameters={...t.parameters,docs:{...(r=t.parameters)==null?void 0:r.docs,source:{originalSource:`{
  args: {
    status: '可发布',
    tone: 'ok'
  }
}`,...(u=(l=t.parameters)==null?void 0:l.docs)==null?void 0:u.source}}};var i,m,c;a.parameters={...a.parameters,docs:{...(i=a.parameters)==null?void 0:i.docs,source:{originalSource:`{
  args: {
    status: '待复核',
    tone: 'warn'
  }
}`,...(c=(m=a.parameters)==null?void 0:m.docs)==null?void 0:c.source}}};var p,d,g;s.parameters={...s.parameters,docs:{...(p=s.parameters)==null?void 0:p.docs,source:{originalSource:`{
  args: {
    status: '需处理',
    tone: 'danger'
  }
}`,...(g=(d=s.parameters)==null?void 0:d.docs)==null?void 0:g.source}}};var S,f,P;n.parameters={...n.parameters,docs:{...(S=n.parameters)==null?void 0:S.docs,source:{originalSource:`{
  render: () => ({
    components: {
      StatusPill
    },
    template: \`
      <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <StatusPill status="可发布" tone="ok" />
        <StatusPill status="待复核" tone="warn" />
        <StatusPill status="需处理" tone="danger" />
        <StatusPill status="生成中" tone="info" />
        <StatusPill status="未开始" tone="muted" />
      </div>
    \`
  })
}`,...(P=(f=n.parameters)==null?void 0:f.docs)==null?void 0:P.source}}};const N=["Ready","ReviewRequired","Blocked","AllStates"];export{n as AllStates,s as Blocked,t as Ready,a as ReviewRequired,N as __namedExportsOrder,q as default};
