/**
 * iconfont.js — SVG Symbol Sprite
 *
 * 线性 outline 风格图标集
 * 灵感: Feather Icons (CC0 协议) + Material Design
 * viewBox: 0 0 24 24 | stroke: currentColor | stroke-width: 1.5
 *
 * 在 main.ts 中 import './assets/iconfont/iconfont.js'
 * 使用: <SvgIcon name="dashboard" /> (推荐)
 * 或: <svg><use href="#icon-dashboard"/></svg>
 */
;(function () {
  'use strict'

  var SPRITE_ID = 'svg-sprite-icons'
  if (document.getElementById(SPRITE_ID)) return

  var div = document.createElement('div')
  div.innerHTML =
    '<svg xmlns="http://www.w3.org/2000/svg" id="' +
    SPRITE_ID +
    '" style="display:none" width="0" height="0">' +
    // 1 仪表盘（dashboard）- speedometer/gauge
    '<symbol id="icon-dashboard" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<circle cx="12" cy="12" r="10"/>' +
    '<path d="M12 6v6l4 2"/>' +
    '</symbol>' +
    // 2 项目管理（project）- folder
    '<symbol id="icon-project" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>' +
    '</symbol>' +
    // 3 报表中心（report）- bar chart
    '<symbol id="icon-report" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M4 20V10"/><path d="M9 20v-4"/><path d="M14 20V8"/><path d="M19 20V4"/>' +
    '</symbol>' +
    // 4 账号管理（account）- user profile
    '<symbol id="icon-account" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<circle cx="12" cy="8" r="5"/>' +
    '<path d="M2 21a10 10 0 0 1 20 0"/>' +
    '</symbol>' +
    // 5 合同文件（contract）- document
    '<symbol id="icon-contract" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
    '<path d="M14 2v6h6"/>' +
    '<path d="M8 13h8"/><path d="M8 17h8"/>' +
    '</symbol>' +
    // 6 待处理（pending）- clock
    '<symbol id="icon-pending" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<circle cx="12" cy="12" r="10"/>' +
    '<path d="M12 6v6l4 2"/>' +
    '</symbol>' +
    // 7 AI 分析（ai）- CPU/chip
    '<symbol id="icon-ai" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<rect x="5" y="5" width="14" height="14" rx="2"/>' +
    '<path d="M12 9v6"/><path d="M9 12h6"/>' +
    '<path d="M5 9H3"/><path d="M5 15H3"/><path d="M21 9h-2"/><path d="M21 15h-2"/>' +
    '<path d="M9 5V3"/><path d="M15 5V3"/><path d="M9 21v-2"/><path d="M15 21v-2"/>' +
    '</symbol>' +
    // 8 已完成（done）- check-circle
    '<symbol id="icon-done" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<circle cx="12" cy="12" r="10"/>' +
    '<path d="M8 12l3 3 5-5"/>' +
    '</symbol>' +
    // 9 风险（risk）- warning triangle
    '<symbol id="icon-risk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M12 2L2 22h20L12 2z"/>' +
    '<path d="M12 10v5"/>' +
    '<circle cx="12" cy="18" r="1" fill="currentColor" stroke="none"/>' +
    '</symbol>' +
    // 10 搜索（search）
    '<symbol id="icon-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<circle cx="11" cy="11" r="7"/>' +
    '<path d="M16 16l4 4"/>' +
    '</symbol>' +
    // 11 导出（export）- download
    '<symbol id="icon-export" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M12 3v12"/>' +
    '<path d="M5 10l7 7 7-7"/>' +
    '<path d="M5 21h14"/>' +
    '</symbol>' +
    // 12 编辑（edit）- pencil
    '<symbol id="icon-edit" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>' +
    '<path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>' +
    '</symbol>' +
    // 13 删除（delete）- trash
    '<symbol id="icon-delete" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M3 6h18"/>' +
    '<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>' +
    '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>' +
    '</symbol>' +
    // 14 查看（view）- eye
    '<symbol id="icon-view" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M1 12s3-8 11-8 11 8 11 8-3 8-11 8-11-8-11-8z"/>' +
    '<circle cx="12" cy="12" r="3"/>' +
    '</symbol>' +
    // 15 确认（confirm）- checkmark
    '<symbol id="icon-confirm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M5 13l4 4L19 7"/>' +
    '</symbol>' +
    // 16 返回（back）- arrow left
    '<symbol id="icon-back" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M19 12H5"/><path d="M12 5l-7 7 7 7"/>' +
    '</symbol>' +
    // 17 退出（logout）- power
    '<symbol id="icon-logout" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M15 4a8 8 0 1 1-6 0"/>' +
    '<path d="M12 2v8"/>' +
    '</symbol>' +
    // 18 文件（file）- document
    '<symbol id="icon-file" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>' +
    '<path d="M13 2v7h7"/>' +
    '</symbol>' +
    // 19 文件副本（file-copy）- duplicate
    '<symbol id="icon-file-copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M14 2H8a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>' +
    '<path d="M14 2v4h4"/>' +
    '<path d="M6 6H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2"/>' +
    '</symbol>' +
    // 20 验收（acceptance）- clipboard with check
    '<symbol id="icon-acceptance" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M15 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>' +
    '<rect x="9" y="2" width="6" height="4" rx="1"/>' +
    '<path d="M9 13l2 2 4-4"/>' +
    '</symbol>' +
    // 21 盾牌（shield）- security
    '<symbol id="icon-shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>' +
    '</symbol>' +
    '</svg>'

  document.body.prepend(div.firstChild)
})()
