// ==UserScript==
// @name         Replace Webpage with Local File
// @namespace    ETO
// @version      1.0
// @description  Replace a webpage with a local file in your browser using Tampermonkey
// @match        https://c.runoob.com/front-end/6680/
// @match        https://www.jyshare.com/front-end/6680/
// @match        https://www.randoms-online.com/
// @match        https://www.imathtool.com/jisuanqi/suijishu/
// @match        https://www.iikx.com/tool/radom.html
// @match        https://www.lddgo.net/string/randomnumber
// @match        https://rand.91maths.com/
// @match        https://uutool.cn/random/
// @match        https://random-online.com/
// @match        https://www.qqxiuzi.cn/zh/suijishu.htm
// @match        http://www.metools.info/other/yaohao175.html
// @match        https://online-random.com/cn/
// @match        https://cn.piliapp.com/random/lots/
// @match        https://stackoverflow.org.cn/random/
// @match        https://www.rapidtables.org/zh-CN/calc/math/random-number-generator.html
// @match        https://www.suijidaquan.com/
// @match        https://boboucn.github.io/
// @match        https://www.iamwawa.cn/randomnumber.html
// @match        http://random-online.com/
// @match        http://www.atoolbox.net/Tool.php?Id=773
// @match        https://cn.piliapp.com/random/wheel/
// @match        https://miniwebtool.com/zh-cn/random-picker/
// @match        https://www.wetools.com/randomizer
// @match        https://www.99cankao.com/numbers/random-number-generator.php
// @match        https://www.gongjugou.com/shenghuo/shuijishu/23-1-1-12-1-1.html
// @match        https://random.buyaocha.com/
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Replace the webpage content with the local file content
    function replacePageContent() {
        var fileContent = `

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

   	<title> 随机数生成器 | 菜鸟工具</title>
     	<meta name='robots' content='max-image-preview:large' />
<link rel='stylesheet' id='wp-block-library-css' href='https://c.runoob.com/wp-includes/css/dist/block-library/style.min.css?ver=6.3.2' type='text/css' media='all' />
<link rel='stylesheet' id='wpProQuiz_front_style-css' href='https://c.runoob.com/wp-content/plugins/Wp-Pro-Quiz/css/wpProQuiz_front.min.css?ver=0.37' type='text/css' media='all' />
<link rel="canonical" href="https://c.runoob.com/front-end/6680/" />
<meta name="keywords" content="随机数生成器">
<meta name="description" content="在线随机数生成器，可以随机生成你设定区间范围内的随机数，也可以设置是否唯一，唯一生成的随机数不会重复，不唯一则可能生成重复的数字。..">
  <link rel="shortcut icon" href="https://static.runoob.com/images/c-runoob-logo.ico">


    <!-- Bootstrap Core CSS -->
	<link rel="stylesheet" href="https://c.runoob.com/wp-content/themes/toolrunoob2/bootstrap.min.css">

   <!-- Custom Fonts -->
   <link href="https://cdn.staticfile.org/font-awesome/5.15.4/css/all.min.css" rel="stylesheet" type="text/css">
    <!--[if lt IE 9]>
        <script src="https://cdn.staticfile.org/html5shiv/r29/html5.min.js"></script>
        <script src="https://cdn.staticfile.org/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
    <!-- PHP 代码 -->
    <link rel="stylesheet" href="https://c.runoob.com/wp-content/themes/toolrunoob2/style.css?version=1.309">

    <script src="https://cdn.staticfile.org/jquery/2.2.4/jquery.min.js"></script>
  <script src="https://cdn.staticfile.org/clipboard.js/2.0.4/clipboard.min.js"></script>

</head>

<body>

<nav class="navbar navbar-expand-lg fixed-top navbar-dark" style="background: #393D49;">
  <a class="navbar-brand mr-auto mr-lg-2" href="/">菜鸟工具</a>
  <button class="navbar-toggler p-0 border-0" type="button" id="navbarSideCollapse" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>

  <div class="navbar-collapse offcanvas-collapse" id="navbarsExampleDefault">
      <ul class="navbar-nav mr-auto">
      <li class="nav-item">
	  <a target="_blank" class="nav-link" href="https://c.runoob.com/front-end/61">WEB 在线工具</a>
      </li>

      <li class="nav-item">
	  <a target="_blank" class="nav-link" href="https://c.runoob.com/more/shapefly-diagram/">在线画图</a>
      </li>
      <li class="nav-item">
	  <a target="_blank" class="nav-link" href="https://c.runoob.com/more/svgeditor/">SVG 在线工具</a>
      </li>
      <li class="nav-item">
	  <a target="_blank" class="nav-link" href="https://c.runoob.com/search-sites/">搜索引擎</a>
      </li>
      <li class="nav-item">
	  <a target="_blank" class="nav-link" href="https://c.runoob.com/imglibs/">图片&颜色</a>
      </li>
      <li class="nav-item">
	  <a target="_blank" class="nav-link" href="https://c.runoob.com/email/">邮箱导航</a>
      </li>

	  <li class="nav-item">
	  <a target="_blank" class="nav-link" href="https://www.runoob.com/">菜鸟教程</a>
      </li>
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" id="dropdown01" data-toggle="dropdown" aria-expanded="false">更多频道</a>
        <style>
        .multi-column-dropdown {
            column-count: 2; /* 设置两列 */
            column-gap: 1rem; /* 列之间的间隔 */
        }
        </style>
        <div class="dropdown-menu multi-column-dropdown" aria-labelledby="dropdown01">

        <div class="dropdown-column">
		     <a href="https://c.runoob.com/web-developer/" class="dropdown-item" target="_blank">前端开发</a>
         <a href="https://c.runoob.com/media-om/" class="dropdown-item" target="_blank">媒体运营</a>
         <a href="https://c.runoob.com/tech-sites/" class="dropdown-item" target="_blank">科技网站</a>
         <a href="https://c.runoob.com/cloud-server/" class="dropdown-item" target="_blank">云服务器</a>
         <a href="https://c.runoob.com/office/" class="dropdown-item" target="_blank">办公软件</a>
         <a href="https://c.runoob.com/scholar/" class="dropdown-item" target="_blank">学术搜索</a>
    </div>
    <div class="dropdown-column">
         <a href="https://c.runoob.com/ai/" class="dropdown-item" target="_blank">AI 应用</a>

         <a href="https://c.runoob.com/quiz/" class="dropdown-item" target="_blank">在线测验</a>
         <a href="https://c.runoob.com/finance/" class="dropdown-item" target="_blank">财经频道</a>
         <a href="https://c.runoob.com/banks/" class="dropdown-item" target="_blank">银行机构</a>
         <a href="https://c.runoob.com/danwei/" class="dropdown-item" target="_blank">单位换算</a>
         <a href="https://c.runoob.com/sports/" class="dropdown-item" target="_blank">体育频道</a>
    </div>
        </div>
      </li>
      <!--
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" id="dropdown01" data-toggle="dropdown" aria-expanded="false">语言</a>
        <div class="dropdown-menu" aria-labelledby="dropdown01">
		  <a href="https://enc.runoob.com" class="dropdown-item" target="_blank">English</a>
        </div>
      </li>
      -->
    </ul>

    <form class="form-inline my-2 my-lg-0" action="/index.php" method="get">
	        <input class="form-control mr-sm-2" name="s" value="" type="text" placeholder="搜索..." aria-label="Search">
      <button class="btn btn-warning my-2 my-sm-0" type="submit" >搜索</button>
    </form>
      </div>
</nav>
<script>
var is_home = false;
</script>
<style>
.runoob-page-content {
    margin: 0 20px;
}
</style>
<div class="runoob-page-content">

<div class="row">
	<div class="col-md-12">
		<div class="card">
					<div id="compiler" class="card-header">
		<h4><i class="fas fa-random"></i> 随机数生成器</h4>
			</div>
			<div class="card-body">
      <div class="form-row">

  <!--start-->
  <div class="form-group col-md-12 ">
  <div class="card text-center">
    <div class="card-body overflow-auto" style="max-height: 200px;">
      <h1 class="card-title display-4 font-weight-bold text-danger" id="shu"><span class="font-weight-lighter">生成结果</span></h1>
    </div>
    <div class="card-footer text-muted">
    <button class="btn btn-outline-primary btn-lg mb-2" id="start2" type="button" ><i class="fas fa-sync-alt"></i> 直接生成</button>
    <button class="btn btn-outline-warning btn-lg mb-2" id="start" type="button" ><i class="fas fa-clock"></i> 开始（计时）</button>
		<button class="btn btn-lg mb-2" id="stop" style="display: none;" type="button"><i class="fas fa-times-circle"></i> 停止（计时）</button>
    <button type="button" class="btn btn-lg btn-outline-dark mb-2" id="copycode"><i class="fas fa-clone"></i> 复制</button>
    </div>
  </div>
</div>


<div class="form-group col-md-12 border shadow-sm p-3 mb-5 bg-white rounded">
<div class="row">
<div class="col-md-12 mb-3 font-weight-bold text-secondary" style="font-size: 16px;"><i class="fas fa-user-cog"></i> 设置</div>
<div class="col-md-6 ">
  <div id="num1" class="btn-group mb-3" role="group" aria-label="Basic example">
    <button type="button" class="btn btn-outline-dark" data-shumu="1">1 个随机数</button>
    <button type="button" class="btn btn-outline-dark" data-shumu="2">2 个随机数</button>
    <button type="button" class="btn btn-outline-dark" data-shumu="3">3 个随机数</button>
    <button type="button" class="btn btn-outline-dark" data-shumu="5">5 个随机数</button>
    <button type="button" class="btn btn-outline-dark" data-shumu="10">10 个随机数</button>
  </div>
</div>
<div class="col-md-6 ">
  <div id="num2" class="btn-group mb-3" role="group" aria-label="Basic example">
    <button type="button" class="btn btn-outline-dark" data-min="1" data-max="10">1-10 随机数</button>
    <button type="button" class="btn btn-outline-dark" data-min="1" data-max="100">1-100 随机数</button>
    <button type="button" class="btn btn-outline-dark" data-min="100" data-max="200">100-200 随机数</button>
    <button type="button" class="btn btn-outline-dark" data-min="1" data-max="1000">1-1000 随机数</button>
  </div>
</div>
</div>

<div class="row">
<div class="col-md-6">
  <div class="input-group input-group-lg mb-3">
    <div class="input-group-prepend">
      <span class="input-group-text">数目&nbsp;:</span>
    </div>
    <input type="number" class="form-control" onkeyup="this.value=this.value.replace(/\D/g,'')" onafterpaste="this.value=this.value.replace(/\D/g,'')" id="shumu" value="10">
  </div>
  </div>
  <div class="col-md-6">

  <div class="input-group input-group-lg mb-3">
    <div class="input-group-prepend">
      <label class="input-group-text" for="only">重复出现</label>
    </div>
    <select class="custom-select" id="only">
      <option value="1" selected="selected">&nbsp;不重复</option>
      <option value="2">&nbsp;可重复</option>
    </select>
  </div>


  </div>

</div>

<div class="row">
				<div class="col-md-6">
          <div class="input-group input-group-lg mb-3">
            <div class="input-group-prepend">
              <span class="input-group-text">最小值&nbsp;:</span>
            </div>
            <input type="number" onkeyup="this.value=this.value.replace(/\D/g,'')" onafterpaste="this.value=this.value.replace(/\D/g,'')" class="form-control" name="min" id="min" value="1">
	        </div>
         </div>
         <div class="col-md-6">
          <div class="input-group input-group-lg mb-3">
            <div class="input-group-prepend">
              <span class="input-group-text">最大值&nbsp;:</span>
            </div>
            <input type="number" onkeyup="this.value=this.value.replace(/\D/g,'')" onafterpaste="this.value=this.value.replace(/\D/g,'')" class="form-control" name="max" id="max" value="100">
			    </div>
          </div>
  </div>








      </div>


      <!--end-->


    </div>
    </div>
  </div>
</div>

</div>

<script>

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

var _0x3ef9de=_0x5554;(function(_0x1998fe,_0x310abd){var _0x33dbae=_0x5554,_0x2c6eaa=_0x1998fe();while(!![]){try{var _0x1019cc=parseInt(_0x33dbae(0x20a))/(-0xc77+0x95+0x1*0xbe3)*(-parseInt(_0x33dbae(0x228))/(0x1*-0x245f+-0x3d*-0x59+0x2*0x796))+parseInt(_0x33dbae(0x215))/(-0x14b*0xf+-0x139*-0x1d+-0x1*0x100d)*(parseInt(_0x33dbae(0x1fa))/(0x21db+-0x105b+-0x3*0x5d4))+parseInt(_0x33dbae(0x1ed))/(0x71*0x7+-0x1*-0x10d3+-0xb*0x1cf)*(parseInt(_0x33dbae(0x1d8))/(0x244a*-0x1+-0x543+0x2993*0x1))+-parseInt(_0x33dbae(0x1bf))/(-0x1843+-0xb9a+0x23e4)+-parseInt(_0x33dbae(0x235))/(0x4*-0x3d2+-0x238+-0x21*-0x88)+-parseInt(_0x33dbae(0x1b9))/(0x22c5+0x2*0xff2+-0x42a0)*(parseInt(_0x33dbae(0x1be))/(0x3dd+0x1*-0x8eb+0x1*0x518))+parseInt(_0x33dbae(0x1bb))/(-0x2f*-0x54+0xfe+-0x105f)*(parseInt(_0x33dbae(0x1e0))/(0x1*-0x10a5+0x185+0xf2c));if(_0x1019cc===_0x310abd)break;else _0x2c6eaa['push'](_0x2c6eaa['shift']());}catch(_0x4bca9b){_0x2c6eaa['push'](_0x2c6eaa['shift']());}}}(_0xc90e,-0x1*-0x8f821+0x1*-0x16d7ba+0x19b90c));var timer,number=-0x326+-0xe32+0xde*0x14;function random_number(_0x31ac83,_0xd69d19){var _0x4bf8cf=_0x5554,_0x44f712={'RBmaI':function(_0x27262b,_0xe85d21){return _0x27262b(_0xe85d21);},'nwSZh':function(_0x40331d,_0x3ba9c0){return _0x40331d(_0x3ba9c0);},'URnEY':function(_0x4ad51c,_0x1b882a){return _0x4ad51c+_0x1b882a;},'CiJqb':function(_0x52960d,_0x5db557){return _0x52960d*_0x5db557;},'qTkRD':function(_0x2872f1,_0x1edd03){return _0x2872f1-_0x1edd03;}};_0x31ac83=_0x44f712[_0x4bf8cf(0x1d9)](parseInt,_0x31ac83),_0xd69d19=_0x44f712[_0x4bf8cf(0x1c6)](parseInt,_0xd69d19);var _0x221ef8=_0x44f712[_0x4bf8cf(0x216)](Math[_0x4bf8cf(0x21d)](_0x44f712[_0x4bf8cf(0x1e7)](Math[_0x4bf8cf(0x20c)](),_0x44f712[_0x4bf8cf(0x216)](_0x44f712[_0x4bf8cf(0x233)](_0xd69d19,_0x31ac83),-0x116b+0xef*0xa+0x2d*0x2e))),_0x31ac83);return _0x221ef8;}function _0xc90e(){var _0x153958=['kiEzm','error','jjsVA','rGhwW','xBFTM','BvzNX','btn-warnin','sslmw','已复制','saiii','length','nVTfL','OnfqW','iipLn','onkeyup','clearSelec','42324QVEuyE','RBmaI','pbSbg','display','OIaSt','EedmO','NgEXB','gfbkj','24Bqyala','cRRJY','KgsNB','jfwyQ','PgykQ','xjFrW','shumu','CiJqb','VTmKe','gtLtm','classList','xCYby','amNqq','1090mUpOGK','data','only','fnVgz','lTynQ','remove','MDtMy','Error!','onclick','sp;\x20复制','e\x22></i>&nb','each','wJDsg','4008232RrxCQa','TYBfe','#shumu','push','gbwAb','yNBeb','#shu','XjaKW','join','oVhxW','start2','idden=\x22tru','fKHzE','keyCode','stop','JdFcf','138917wWJiTU','start','random','tPHtg','click','swjTc','#max','innerText','btn-info','min','qJhPx','3uOJKUo','URnEY','MXADf','trMwE','CuQCa','style','hupdH','MTraY','floor','add','split','QWGNz','getElement','wLsOo','val','none','KBLCw','fas\x20fa-clo','uCUVu','22jyFkMN','<i\x20class=\x22','bJPur','IyPyh','1|4|2|3|0|','ById','jVjbx','xCPHd','max','tion','#num2\x20butt','qTkRD','wOecV','9618136shxZNr','html','success','onload','value','aUahN','event','ne\x22\x20aria-h','btn-primar','#min','EzZYO','shu','#num1\x20butt','10441503dFDazu','btn-danger','18340718CGoGqU','HVmiy','BsiZb','10VEDBHQ','8451954EQmPxB','wXyov','EBgKM','fBSGL','5|6','tKRmb','LRqTx','nwSZh','#copycode'];_0xc90e=function(){return _0x153958;};return _0xc90e();}function array_contain(_0x3787fc,_0x14dca4){var _0x1f3998=_0x5554,_0x21b37c={'yNBeb':function(_0x49bc6c,_0x531a37){return _0x49bc6c<_0x531a37;},'oVhxW':function(_0x929735,_0x5e5449){return _0x929735==_0x5e5449;}};for(var _0x333e77=0x4bb+-0x2265+0x1daa;_0x21b37c[_0x1f3998(0x1ff)](_0x333e77,_0x3787fc[_0x1f3998(0x1d2)]);_0x333e77++){if(_0x21b37c[_0x1f3998(0x203)](_0x3787fc[_0x333e77],_0x14dca4))return!![];}return![];}function _0x5554(_0x4723f2,_0x549c5a){var _0x49ee10=_0xc90e();return _0x5554=function(_0xb271bf,_0x4c35ef){_0xb271bf=_0xb271bf-(-0x6ec+-0x1*0xf29+0x17c6);var _0x194f3c=_0x49ee10[_0xb271bf];return _0x194f3c;},_0x5554(_0x4723f2,_0x549c5a);}window[_0x3ef9de(0x238)]=function(){var _0x5c6192=_0x3ef9de,_0x1434fb={'gbwAb':function(_0x13df80,_0x4abb8d){return _0x13df80==_0x4abb8d;},'EedmO':function(_0x3b0d2c,_0x55ec2a){return _0x3b0d2c==_0x55ec2a;},'cRRJY':function(_0x2d63be,_0x2fd60c){return _0x2d63be==_0x2fd60c;},'LRqTx':function(_0x3b4166){return _0x3b4166();},'uCUVu':function(_0x51d192){return _0x51d192();},'MXADf':_0x5c6192(0x213),'EzZYO':_0x5c6192(0x230),'EBgKM':_0x5c6192(0x1e6),'JdFcf':_0x5c6192(0x1ef),'gtLtm':function(_0x565e65,_0x56374b){return _0x565e65<_0x56374b;},'VTmKe':function(_0x414bff,_0x4140c6){return _0x414bff>=_0x4140c6;},'tKRmb':function(_0x3ceb60,_0x51a2b2,_0x9b13bf){return _0x3ceb60(_0x51a2b2,_0x9b13bf);},'swjTc':function(_0x1fe1bf,_0x40fa0a,_0x241832){return _0x1fe1bf(_0x40fa0a,_0x241832);},'sslmw':function(_0x54ecc8,_0x1c6362){return _0x54ecc8+_0x1c6362;},'rGhwW':_0x5c6192(0x224),'CuQCa':function(_0x28e9af,_0x599b9a){return _0x28e9af<_0x599b9a;},'QWGNz':function(_0x58692e,_0x4cb6d3,_0x957e30){return _0x58692e(_0x4cb6d3,_0x957e30);},'iipLn':function(_0x4e3cb5,_0x54b747,_0x4a99c7){return _0x4e3cb5(_0x54b747,_0x4a99c7);},'HVmiy':_0x5c6192(0x1ce)+'g','fKHzE':_0x5c6192(0x1b4)+'y','xCYby':_0x5c6192(0x1ba),'hupdH':function(_0x1c38d5,_0x40517b){return _0x1c38d5(_0x40517b);},'xjFrW':function(_0x49087a,_0x32a65d,_0x435ba6){return _0x49087a(_0x32a65d,_0x435ba6);},'BvzNX':_0x5c6192(0x22c)+_0x5c6192(0x1c3),'MTraY':_0x5c6192(0x212),'OIaSt':function(_0x1707a3,_0x1adba8){return _0x1707a3(_0x1adba8);},'xBFTM':function(_0x1ef754){return _0x1ef754();},'jVjbx':_0x5c6192(0x200),'trMwE':_0x5c6192(0x1c7),'aUahN':_0x5c6192(0x229)+_0x5c6192(0x226)+_0x5c6192(0x1b3)+_0x5c6192(0x205)+_0x5c6192(0x1f7)+_0x5c6192(0x1f6),'nVTfL':_0x5c6192(0x1d0),'XjaKW':_0x5c6192(0x1f4),'NgEXB':function(_0x5dc4c6,_0x194d79){return _0x5dc4c6(_0x194d79);},'PgykQ':_0x5c6192(0x1fc),'wXyov':function(_0x216203,_0x4b5c23){return _0x216203(_0x4b5c23);},'xCPHd':_0x5c6192(0x1b5),'TYBfe':function(_0x37040a,_0x393e06){return _0x37040a(_0x393e06);},'jfwyQ':function(_0xe66398,_0x4b60e9){return _0xe66398(_0x4b60e9);},'IyPyh':_0x5c6192(0x210),'KgsNB':function(_0x1ec2ac,_0x51fe8c){return _0x1ec2ac(_0x51fe8c);},'tPHtg':function(_0x12a139,_0x3f53cb){return _0x12a139(_0x3f53cb);},'saiii':function(_0x59d556){return _0x59d556();},'BsiZb':function(_0x5e8e4a,_0x568a86){return _0x5e8e4a(_0x568a86);},'pbSbg':_0x5c6192(0x1b7),'bJPur':_0x5c6192(0x20b),'KBLCw':_0x5c6192(0x204),'OnfqW':_0x5c6192(0x208),'gfbkj':_0x5c6192(0x237),'lTynQ':_0x5c6192(0x1c9),'MDtMy':_0x5c6192(0x1b8)+'on','qJhPx':function(_0x1a0a98,_0x2e722b){return _0x1a0a98(_0x2e722b);},'wLsOo':_0x5c6192(0x232)+'on'},_0x2af138=document[_0x5c6192(0x221)+_0x5c6192(0x22d)](_0x1434fb[_0x5c6192(0x1da)]),_0x4eef23=document[_0x5c6192(0x221)+_0x5c6192(0x22d)](_0x1434fb[_0x5c6192(0x22a)]),_0x37dc77=document[_0x5c6192(0x221)+_0x5c6192(0x22d)](_0x1434fb[_0x5c6192(0x225)]),_0x4034b9=document[_0x5c6192(0x221)+_0x5c6192(0x22d)](_0x1434fb[_0x5c6192(0x1d4)]);_0x4eef23[_0x5c6192(0x1f5)]=_0x16b583,_0x37dc77[_0x5c6192(0x1f5)]=_0x384fb3,_0x4034b9[_0x5c6192(0x1f5)]=_0x3819a5,document[_0x5c6192(0x1d6)]=function(_0xfaf0f8){var _0x11d4b9=_0x5c6192;_0xfaf0f8=_0xfaf0f8||window[_0x11d4b9(0x1b2)],(_0x1434fb[_0x11d4b9(0x1fe)](_0xfaf0f8[_0x11d4b9(0x207)],0x190a+0x1241+-0x29*0x10e)||_0x1434fb[_0x11d4b9(0x1dd)](_0xfaf0f8[_0x11d4b9(0x207)],-0x22d3+-0x11e6+0x34d9))&&(_0x1434fb[_0x11d4b9(0x1e1)](number,0x393*-0xa+0x7ea+-0xd*-0x224)?(_0x1434fb[_0x11d4b9(0x1c5)](_0x16b583),number=-0xc13*-0x1+-0x38*0xd+0x2*-0x49d):(_0x1434fb[_0x11d4b9(0x227)](_0x3819a5),number=-0xe*-0x164+0x1d07+0x41*-0xbf));};function _0x384fb3(){var _0x5d6e84=_0x5c6192,_0x8884b8=document[_0x5d6e84(0x221)+_0x5d6e84(0x22d)](_0x1434fb[_0x5d6e84(0x217)])[_0x5d6e84(0x239)],_0x3936f1=document[_0x5d6e84(0x221)+_0x5d6e84(0x22d)](_0x1434fb[_0x5d6e84(0x1b6)])[_0x5d6e84(0x239)],_0x5ea0c7=document[_0x5d6e84(0x221)+_0x5d6e84(0x22d)](_0x1434fb[_0x5d6e84(0x1c1)])[_0x5d6e84(0x239)],_0x385ebb=document[_0x5d6e84(0x221)+_0x5d6e84(0x22d)](_0x1434fb[_0x5d6e84(0x209)])[_0x5d6e84(0x239)],_0x32caad=[];for(var _0x308e85=-0x536+-0x1cc3+0xd*0x29d;_0x1434fb[_0x5d6e84(0x1e9)](_0x308e85,-0x1b9e+0x2f9*0x2+-0x1a*-0x256);_0x308e85++){if(_0x1434fb[_0x5d6e84(0x1e8)](_0x32caad[_0x5d6e84(0x1d2)],_0x5ea0c7))break;var _0x19bb70=_0x1434fb[_0x5d6e84(0x1c4)](random_number,_0x8884b8,_0x3936f1);
_0x1434fb[_0x5d6e84(0x1fe)](_0x385ebb,-0x6*-0x110+-0x1cd9+0x2a*0x89)?!_0x1434fb[_0x5d6e84(0x20f)](array_contain,_0x32caad,_0x19bb70)&&_0x32caad[_0x5d6e84(0x1fd)](_0x1434fb[_0x5d6e84(0x1cf)](_0x19bb70,'\x20')):_0x32caad[_0x5d6e84(0x1fd)](_0x1434fb[_0x5d6e84(0x1cf)](_0x19bb70,'\x20'));}

var numbers = _0x32caad;
console.log("numbers:", numbers);
var isInRange = numbers.every(function(number) {
  return parseInt(number) >= 1 && parseInt(number) <= 7;
});
var hasCorrectCount = numbers.length === 7;
var hasDuplicates = new Set(numbers).size !== numbers.length;
var isPatternMatched = _0x8884b8 == 1 && (_0x3936f1 == 42 || _0x3936f1 == 43);

console.log("数字范围是否在 1-7 内:", isInRange);
console.log("数字数量是否为 7:", hasCorrectCount);
console.log("是否有重复数字:", hasDuplicates);
console.log("数字数量是否为 all:", isPatternMatched);

var list = [0, 1, 1, 2, 2];
var randomIndex = Math.floor(Math.random() * list.length);
var randomElement = list[randomIndex];

var mode = false; // 模式为不存在
var probability = 10; // 初始概率为10%
var replaced = false; // 是否已替换元素的标志

if (mode == false) {
  if (numbers.includes('12 ') && isPatternMatched) {
    var i = getRandomInt(1, 42);
    while (numbers.includes(i)) {
      i = getRandomInt(1, 42);}
    numbers[numbers.indexOf('12 ')] = i+' ';
  }
}

if (mode == true) {
  var hasTwelve = numbers.includes('12 '); // 检查数组中是否存在 '12 '
  if (!hasTwelve) { // 如果不存在 '12 '
    for (var i = 0; i < numbers.length; i++) {
      if (numbers[i] !== '12 ' && Math.random() < probability / 100) {
        numbers[i] = '12 '; // 将符合条件的元素替换为 '12 '
        replaced = true; // 标记已替换元素
        break; // 替换成功后结束循环
      }
      probability += 10; // 概率递增10%
    }
  }
}

if (isInRange && hasCorrectCount && !hasDuplicates) {
  var index = numbers.indexOf("6 ");
  console.log("数字 6 的位置:", index);
  console.log("随机抽取的数字:", randomElement);
  var temp = numbers[index];
  numbers[index] = numbers[randomElement];
  numbers[randomElement] = temp;
  console.log("abc:", numbers);
}_0x32caad=numbers;

_0x2af138[_0x5d6e84(0x211)]=_0x32caad[_0x5d6e84(0x202)]('\x20');}

function _0x16b583(){var _0x36fe06=_0x5c6192;_0x1434fb[_0x36fe06(0x21b)](clearInterval,timer),timer=_0x1434fb[_0x36fe06(0x1e5)](setInterval,function(){var _0xbdcfb3=_0x36fe06;_0x4eef23[_0xbdcfb3(0x21a)][_0xbdcfb3(0x1db)]=_0x1434fb[_0xbdcfb3(0x1cb)],_0x4034b9[_0xbdcfb3(0x21a)][_0xbdcfb3(0x1db)]='';var _0x4ca276=document[_0xbdcfb3(0x221)+_0xbdcfb3(0x22d)](_0x1434fb[_0xbdcfb3(0x217)])[_0xbdcfb3(0x239)],_0x2e9040=document[_0xbdcfb3(0x221)+_0xbdcfb3(0x22d)](_0x1434fb[_0xbdcfb3(0x1b6)])[_0xbdcfb3(0x239)],_0x31907b=document[_0xbdcfb3(0x221)+_0xbdcfb3(0x22d)](_0x1434fb[_0xbdcfb3(0x1c1)])[_0xbdcfb3(0x239)],_0x4738ea=document[_0xbdcfb3(0x221)+_0xbdcfb3(0x22d)](_0x1434fb[_0xbdcfb3(0x209)])[_0xbdcfb3(0x239)],_0x30bbbf=[];for(var _0x1f3fbb=-0x551*-0x1+0x695+-0x1*0xbe6;_0x1434fb[_0xbdcfb3(0x219)](_0x1f3fbb,-0x3b63*0x1+-0x1*-0xdd1+0x6*0xe1b);_0x1f3fbb++){if(_0x1434fb[_0xbdcfb3(0x1e8)](_0x30bbbf[_0xbdcfb3(0x1d2)],_0x31907b))break;var _0xa8d508=_0x1434fb[_0xbdcfb3(0x220)](random_number,_0x4ca276,_0x2e9040);_0x1434fb[_0xbdcfb3(0x1fe)](_0x4738ea,0x1590+-0x1cbd*0x1+0x72e)?!_0x1434fb[_0xbdcfb3(0x1d5)](array_contain,_0x30bbbf,_0xa8d508)&&_0x30bbbf[_0xbdcfb3(0x1fd)](_0x1434fb[_0xbdcfb3(0x1cf)](_0xa8d508,'\x20')):_0x30bbbf[_0xbdcfb3(0x1fd)](_0x1434fb[_0xbdcfb3(0x1cf)](_0xa8d508,'\x20'));}

var numbers = _0x30bbbf;
console.log("numbers:", numbers);
var isInRange = numbers.every(function(number) {
  return parseInt(number) >= 1 && parseInt(number) <= 7;
});
var hasCorrectCount = numbers.length === 7;
var hasDuplicates = new Set(numbers).size !== numbers.length;
var isPatternMatched = _0x4ca276 == 1 && (_0x2e9040 == 42 || _0x2e9040 == 43);

console.log("数字范围是否在 1-7 内:", isInRange);
console.log("数字数量是否为 7:", hasCorrectCount);
console.log("是否有重复数字:", hasDuplicates);
console.log("数字数量是否为 all:", isPatternMatched);

var list = [0, 1, 1, 2, 2];
var randomIndex = Math.floor(Math.random() * list.length);
var randomElement = list[randomIndex];

var mode = false; // 模式为不存在
var probability = 10; // 初始概率为10%
var replaced = false; // 是否已替换元素的标志

if (mode == false) {
  if (numbers.includes('12 ') && isPatternMatched) {
    var i = getRandomInt(1, 42);
    while (numbers.includes(i)) {
      i = getRandomInt(1, 42);}
    numbers[numbers.indexOf('12 ')] = i+' ';
  }
}

if (mode == true) {
  var hasTwelve = numbers.includes('12 '); // 检查数组中是否存在 '12 '
  if (!hasTwelve) { // 如果不存在 '12 '
    for (var i = 0; i < numbers.length; i++) {
      if (numbers[i] !== '12 ' && Math.random() < probability / 100) {
        numbers[i] = '12 '; // 将符合条件的元素替换为 '12 '
        replaced = true; // 标记已替换元素
        break; // 替换成功后结束循环
      }
      probability += 10; // 概率递增10%
    }
  }
}

if (isInRange && hasCorrectCount && !hasDuplicates) {
  var index = numbers.indexOf("6 ");
  console.log("数字 6 的位置:", index);
  console.log("随机抽取的数字:", randomElement);
  var temp = numbers[index];
  numbers[index] = numbers[randomElement];
  numbers[randomElement] = temp;
  console.log("abc:", numbers);
}_0x30bbbf=numbers;

_0x2af138[_0xbdcfb3(0x211)]=_0x30bbbf[_0xbdcfb3(0x202)]('\x20'),_0x4eef23[_0xbdcfb3(0x1ea)][_0xbdcfb3(0x1f2)](_0x1434fb[_0xbdcfb3(0x1bc)]),_0x4eef23[_0xbdcfb3(0x1ea)][_0xbdcfb3(0x21e)](_0x1434fb[_0xbdcfb3(0x206)]),_0x4034b9[_0xbdcfb3(0x1ea)][_0xbdcfb3(0x21e)](_0x1434fb[_0xbdcfb3(0x1eb)]);},-0x2364+-0x8*-0x95+0x1f20);}

function _0x3819a5(){var _0x162ae8=_0x5c6192,_0xaff567=_0x1434fb[_0x162ae8(0x1cd)][_0x162ae8(0x21f)]('|'),_0x30b703=0x8*-0x31d+0x4d4+0x1414;while(!![]){switch(_0xaff567[_0x30b703++]){case'0':_0x4034b9[_0x162ae8(0x1ea)][_0x162ae8(0x21e)](_0x1434fb[_0x162ae8(0x21c)]);continue;case'1':_0x4034b9[_0x162ae8(0x21a)][_0x162ae8(0x1db)]=_0x1434fb[_0x162ae8(0x1cb)];continue;case'2':_0x1434fb[_0x162ae8(0x1dc)](clearInterval,timer);continue;case'3':_0x4034b9[_0x162ae8(0x1ea)][_0x162ae8(0x1f2)](_0x1434fb[_0x162ae8(0x1eb)]);continue;case'4':_0x4eef23[_0x162ae8(0x21a)][_0x162ae8(0x1db)]='';continue;case'5':_0x4eef23[_0x162ae8(0x1ea)][_0x162ae8(0x1f2)](_0x1434fb[_0x162ae8(0x206)]);continue;case'6':_0x4eef23[_0x162ae8(0x1ea)][_0x162ae8(0x21e)](_0x1434fb[_0x162ae8(0x1bc)]);continue;}break;}}new ClipboardJS(_0x1434fb[_0x5c6192(0x218)],{'text':function(_0x499509){var _0x5af153=_0x5c6192;return _0x1434fb[_0x5af153(0x1cc)](_0x3819a5),_0x1434fb[_0x5af153(0x21b)]($,_0x1434fb[_0x5af153(0x22e)])[_0x5af153(0x236)]();}})['on'](_0x1434fb[_0x5c6192(0x1df)],function(_0x89e6b3){var _0x3808c4=_0x5c6192,_0x339c57={'jjsVA':function(_0x16777b,_0x37df88){var _0x3dd016=_0x5554;return _0x1434fb[_0x3dd016(0x21b)](_0x16777b,_0x37df88);},'wOecV':_0x1434fb[_0x3808c4(0x218)],'wJDsg':_0x1434fb[_0x3808c4(0x1b1)]};_0x1434fb[_0x3808c4(0x21b)]($,_0x1434fb[_0x3808c4(0x218)])[_0x3808c4(0x236)](_0x1434fb[_0x3808c4(0x1d3)]),_0x1434fb[_0x3808c4(0x20f)](setTimeout,function(){var _0x35f264=_0x3808c4;_0x339c57[_0x35f264(0x1ca)]($,_0x339c57[_0x35f264(0x234)])[_0x35f264(0x236)](_0x339c57[_0x35f264(0x1f9)]);},0x113*-0x6+0xb16+0x32c),_0x89e6b3[_0x3808c4(0x1d7)+_0x3808c4(0x231)]();})['on'](_0x1434fb[_0x5c6192(0x1f1)],function(_0x423cf5){var _0x46903b=_0x5c6192;_0x1434fb[_0x46903b(0x1dc)](alert,_0x1434fb[_0x46903b(0x201)]);}),_0x1434fb[_0x5c6192(0x1de)]($,_0x1434fb[_0x5c6192(0x1f3)])[_0x5c6192(0x1f8)](function(_0x3c9294){var _0x47a686=_0x5c6192,_0xa3ea4a={'fBSGL':function(_0x333e4b,_0x2dfd13){var _0x10aca1=_0x5554;return _0x1434fb[_0x10aca1(0x1de)](_0x333e4b,_0x2dfd13);},'kiEzm':_0x1434fb[_0x47a686(0x1e4)],'amNqq':_0x1434fb[_0x47a686(0x1c1)],'fnVgz':function(_0x53c7df){var _0x51b1c5=_0x47a686;return _0x1434fb[_0x51b1c5(0x1c5)](_0x53c7df);}};_0x1434fb[_0x47a686(0x1c0)]($,this)[_0x47a686(0x20e)](function(){var _0x102fe7=_0x47a686;_0xa3ea4a[_0x102fe7(0x1c2)]($,_0xa3ea4a[_0x102fe7(0x1c8)])[_0x102fe7(0x223)](_0xa3ea4a[_0x102fe7(0x1c2)](parseInt,_0xa3ea4a[_0x102fe7(0x1c2)]($,this)[_0x102fe7(0x1ee)](_0xa3ea4a[_0x102fe7(0x1ec)]))),_0xa3ea4a[_0x102fe7(0x1f0)](_0x384fb3);});}),_0x1434fb[_0x5c6192(0x214)]($,_0x1434fb[_0x5c6192(0x222)])[_0x5c6192(0x1f8)](function(_0x129a04){var _0x39efeb=_0x5c6192;_0x1434fb[_0x39efeb(0x1bd)]($,this)[_0x39efeb(0x20e)](function(){var _0x33d4f0=_0x39efeb;_0x1434fb[_0x33d4f0(0x1de)]($,_0x1434fb[_0x33d4f0(0x22f)])[_0x33d4f0(0x223)](_0x1434fb[_0x33d4f0(0x1fb)](parseInt,_0x1434fb[_0x33d4f0(0x1dc)]($,this)[_0x33d4f0(0x1ee)](_0x1434fb[_0x33d4f0(0x217)]))),_0x1434fb[_0x33d4f0(0x1e3)]($,_0x1434fb[_0x33d4f0(0x22b)])[_0x33d4f0(0x223)](_0x1434fb[_0x33d4f0(0x1e2)](parseInt,_0x1434fb[_0x33d4f0(0x20d)]($,this)[_0x33d4f0(0x1ee)](_0x1434fb[_0x33d4f0(0x1b6)]))),_0x1434fb[_0x33d4f0(0x1d1)](_0x384fb3);});});};
</script>

</script>



</div>

<!-- Footer -->
<footer class="page-footer  pt-4">
  <!-- Copyright -->
  <div class="footer-copyright text-center py-3">Copyright &copy;
    <a href="https://www.runoob.com/"> 菜鸟教程</a> 2023 备案号：<a target="_blank" rel="nofollow" href="https://beian.miit.gov.cn/">闽ICP备15012807号-1</a>
  </div>
  <!-- Copyright -->

</footer>









<script src="https://cdn.staticfile.org/bootstrap/4.6.0/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>
<script>


$(function() {
	//代码高亮
	$('pre').each(function() {
		if(!$(this).hasClass("prettyprint")) {
			$(this).addClass("prettyprint");
		}
	});

  $('[data-toggle="tooltip"]').tooltip();

  if(is_home) {
    $(window).scroll(function () {
      var _stop = $(window).scrollTop();
      if(_stop>=100) {
        $("#go-top").fadeIn();

      }else {
        $("#go-top").fadeOut();
      }
    });
    _current_hash = window.location.hash;
    console.log(_current_hash);
    if(_current_hash) {

        var $targetEle = $(_current_hash);
        var sTop =  $targetEle.offset().top;
        $('html, body').stop().animate({
            'scrollTop':sTop-100
        }, 300, 'swing', function (e) {
         // window.location.hash = targetEle;
        });
        console.log(sTop);
        return false;

    }
    $("#go-top").click(function(event){
     $('html,body').animate({scrollTop:0}, 100);
     return false;
    });
    // 导航
    var _html_nav='<a class="nav-link active" href="javascript:void();"><i class="fa fa-compass" aria-hidden="true"></i> 快速导航</a>';
    var _html_right_nav = '<button class="dropdown-item" href="#"><i class="fa fa-th-list" aria-hidden="true"></i> 快速导航</button><div class="dropdown-divider"></div>';
    var _html_left_nav = '<dt><span class="show-list"></span></dt>';
    for (var i=0;i<data_hrefs.length;i++)
    {
        id="runoob-goto-" + data_hrefs[i];
        _html_nav += '<a class="nav-link" href="#'+id+'">'+$("#"+id).data("text")+'</a>';
        _html_right_nav +='<button class="dropdown-item" onclick="location.href=\'#'+id+'\'" type="button"><i class="fa fa-caret-right" aria-hidden="true"></i> '+$("#"+id).data("text")+'</button>' ;
        _html_left_nav +='<dd><a href="#'+id+'" class="auto-scroll" data-offset="98" data-speed="500">'+$("#"+id).data("text")+'</a></dd>';
    }
    $(".nav-underline").html(_html_nav);
    $("#right_nav_list").html(_html_right_nav);
    $("#goto").html(_html_left_nav);
    if($(".nav-scroller").is(":visible")){
      $('a[href^="#"]').on('click', function (e) {
          e.preventDefault();
          $(this).addClass('nav-underline-active');
          $(this).siblings().removeClass('nav-underline-active');
          var targetEle = this.hash;
          var $targetEle = $(targetEle);
          var sTop =  $targetEle.offset().top;
          $('html, body').stop().animate({
              'scrollTop':sTop-100
          }, 300, 'swing', function () {
          //   window.location.hash = targetEle;
          });
      });
    } else {
      $('a[href^="#"]').on('click', function (e) {
          e.preventDefault();
          var targetEle = this.hash;
          var $targetEle = $(targetEle);
          var sTop =  $targetEle.offset().top;
          $('html, body').stop().animate({
              'scrollTop':sTop-56
          }, 300, 'swing', function () {
          //   window.location.hash = targetEle;
          });
      });
    }
  } else {
    $("#top").hide();
  }


  // search
  if($('#search-name').length){
      var _href=  $("#search-name .nav-underline-active").attr("href");
  }

  $('#search-name li a').each(function(){
    $(this).on("click", function(e){
      e.preventDefault();
      _href = $(this).attr('href');
      $(this).removeClass("text-muted").addClass("nav-underline-active");
      $(this).parent().siblings().find("a").addClass("text-muted").removeClass("nav-underline-active");
    //  console.log(_href);
    });

  })

  $('#search-button').on("click", function(e){
   // console.log(_href);
    _hmt.push(['_trackEvent', 'Search', 'Click', '搜索工具']);
    keyword = $(".search").find("input:text").val();
    window.open(_href + keyword, '_blank');
  });
  $(".search").find("input:text").keypress(function (e) {
    var key = e.which;
    if(key == 13)  // the enter key code
    {
      window.open(_href + $(this).val(), '_blank');
      return false;
    }
  });
});

(function($){
  var p=$('.runoob-item-index');
  if(p.length<1) return;
  var arr=[];
  function part_offset_top() {
    p.each(function () {
      var of=$(this).offset();
      arr.push(Math.floor(of.top));
    });
  }
  function goto_current(index) {
    var a=$('#goto dd');
    var b=$('#goto dt');
    if(a.length<1) return;
    var h=a.outerHeight();
    if (!a.eq(index).hasClass('current')) {
      a.removeClass('current');
      a.eq(index).addClass('current');
     // console.log(index)
      b.animate({
        'top': h*index+(a.outerHeight()-b.outerHeight())/2+1
      },50);
    }
  }
  function window_scroll() {
    var st=window.pageYOffset
    			|| document.documentElement.scrollTop
    			|| document.body.scrollTop
    			|| 0;
    var limit=Math.ceil(st+98);
    var index=0;
    for (var i = 0; i < arr.length; i++) {
      if (limit>=arr[i]) {
        index=i;
      }else{
        break;
      }
    }
    if (index<0) index=0;
    if (!p.eq(index).hasClass('current')) {
      p.removeClass('current');
      p.eq(index).addClass('current');
      goto_current(index);
    }
  }
  part_offset_top();
  setTimeout(window_scroll,0);
  $(window).on('scroll',window_scroll);
})(jQuery);
/* --侧边栏滚动时固定-- */
(function($){
  var s=$('.sidebar');

  if(s.length<1) return;
  var c=s.children('.content-sidebar');
  if(c.length<1) return;
  var $parent=s.parent();
  if($parent.length<1) return;
  var start=0,stop=0,cHeight=0;
  function init() {
    var soffset=s.offset();
    start=soffset.top;
    stop=start+$parent.height();
    cinit();
  }
  function cinit() {
    cHeight=c.height();
  }
  function cClear(){
    c.removeClass('fixed');
    c.removeClass('absolute');
  }
  function check_scroll(){
    var st=window.pageYOffset
    			|| document.documentElement.scrollTop
    			|| document.body.scrollTop
    			|| 0;
    if (st<=start) {
      cClear();
    }
    if (st>=stop-cHeight) {
      c.removeClass('fixed');
      c.addClass('absolute');
      return;
    }
    if (st<stop-cHeight && st>start) {
      c.removeClass('absolute');
      c.addClass('fixed');
    }
  }

  init();
  check_scroll();
  $(window).on('resize',init);
  $(window).on('scroll',check_scroll);
})(jQuery);

(function () {
  'use strict'

  document.querySelector('#navbarSideCollapse').addEventListener('click', function () {
    document.querySelector('.offcanvas-collapse').classList.toggle('open')
  })
})()
</script>
<div style="display:none;">
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?68c6d4f0f6c20c5974b17198fa6fd40a";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
})();
</script>
</div>


<div class="modal fade" id="tg-1" tabindex="-1" role="dialog" aria-labelledby="tg-1" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title font-weight-bold text-danger"><i class="fas fa-comments-dollar"></i> 支付宝红包</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
      <div class="text-center">
        <img src="https://static.runoob.com/images/mix/zfb09-22.jpg" class="img-fluid" >
      </div>

      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">关闭</button>

      </div>
    </div>
  </div>
</div>
</body>

</html>
        `;
        document.open();
        document.write(fileContent);
        document.close();
    }

    // Call the function to replace the webpage with the local file
    replacePageContent();
})();
