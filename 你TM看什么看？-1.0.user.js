// ==UserScript==
// @name        你TM看什么看？
// @namespace   your-namespace
// @version     1.0
// @description ETO
// @match       https://48kezn.lqzb.fun/*
// @grant       none
// ==/UserScript==

(function () {
  'use strict';

  var originalContent = document.documentElement.innerHTML;
  var replaceFlag = localStorage.getItem('replaceFlag');
  var storedTime = localStorage.getItem('storedTime');

  if (replaceFlag === null) {
    replaceFlag = 'true';
  }

  // 替换的 HTML 内容
  var replacementHTML = `
    <style>
      .custom-font {
        font-family: 萝莉体, sans-serif;
        font-size: 32px;
        color: #FF0000;
      }
      .center-text {
        text-align: center;
      }
      .custom-button {
        background-color: green;
        color: white;
        font-size: 24px;
        padding: 10px 20px;
        font-family: Arial, sans-serif;
        display: block;
        margin: 0 auto;
      }
    </style>
    <div class="custom-content center-text">
      <p class="custom-font">敲，给脸了啊</p>
      <p class="custom-font">随地大小便还***事多是吧</p>
      <p class="custom-font">地址栏不会用是吧</p>
      <p class="custom-font">就你***还***说这逼话</p>
      <p class="custom-font">什么东西还来威胁你爷啊</p>
      <p class="custom-font">在我账号里面不知道嘚瑟什么</p>
      <p class="custom-font">老子丢你***一个按钮</p>
      <p class="custom-font">这个保你***五分钟一次</p>
      <p class="custom-font">你***就爱用不用</p>
      <p class="custom-font">受不了就出门左转Flash，爷不伺候</p>
    </div>

    <button id="restoreButton" class="custom-button">恢复页面</button>
  `;


  // 如果本地存储中没有记录的时间，则进行替换操作
  if (!storedTime) {
    replacePage();
    return;
  }

  // 获取当前时间
  var currentTime = Date.now();
  // 计算时间差，单位为毫秒
  var timeDiff = currentTime - parseInt(storedTime);

  // 如果时间差大于5分钟（300000毫秒），则进行替换操作
  if (timeDiff > 300000) {
    replacePage();
    replaceFlag = 'True'
  }

  // 如果标记为不替换，则不进行替换操作
  if (replaceFlag === 'false') {
    return;
  }

  // 创建一个新的元素并设置其内容为替换的 HTML 内容
  var newElement = document.createElement('div');
  newElement.innerHTML = replacementHTML;

  // 添加恢复按钮点击事件
  newElement.querySelector('#restoreButton').addEventListener('click', function () {
    // 设置标记为不替换
    localStorage.setItem('replaceFlag', 'false');
    // 记录当前时间
    localStorage.setItem('storedTime', Date.now());
    // 恢复原始页面内容
    document.documentElement.innerHTML = originalContent;
  });

  // 替换页面内容
  document.documentElement.innerHTML = '';
  document.body.appendChild(newElement);

  function replacePage() {
    // 清空页面内容
    document.documentElement.innerHTML = '';

    // 创建一个新的元素并设置其内容为替换的 HTML 内容
    var newElement = document.createElement('div');
    newElement.innerHTML = replacementHTML;

    // 添加恢复按钮点击事件
    newElement.querySelector('#restoreButton').addEventListener('click', function () {
      // 设置标记为不替换
      localStorage.setItem('replaceFlag', 'false');
      // 记录当前时间
      localStorage.setItem('storedTime', Date.now());
      // 恢复原始页面内容
      document.documentElement.innerHTML = originalContent;
    });

    // 替换页面内容
    document.documentElement.innerHTML = '';
    document.body.appendChild(newElement);
  }
})();
