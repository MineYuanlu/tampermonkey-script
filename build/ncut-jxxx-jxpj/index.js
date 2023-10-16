// ==UserScript==
// @name          NCUT 教学评价
// @namespace     bid.yuanlu
// @version       1.0.20231016.1058578
// @description   自动进行教学评价
// @author        yuanlu
// @grant         none
// @icon          https://www.google.com/s2/favicons?sz=64&domain=ncut.edu.cn
// @include       http://jxxx.ncut.edu.cn/xs/grxx.asp?id=12*
// @include       http://jxxx.webvpn.ncut.edu.cn/xs/grxx.asp?id=12*
// @include       https://jxxx.ncut.edu.cn/xs/grxx.asp?id=12*
// @include       https://jxxx.webvpn.ncut.edu.cn/xs/grxx.asp?id=12*
// @require       https://code.jquery.com/jquery-latest.js
// @run-at        document-end
// ==/UserScript==


(function () {
    'use strict';
    var $ = window.jQuery;
    var id = 'yuanlu_ncut_jxpj_loaded';
    if ($("#".concat(id)).length)
        return;
    $('body').append("<div id=\"".concat(id, "\" />")); //标识
    function getSelecter() {
        return document.getElementsByName('kcxuanze')[0];
    }
    var autoSelect = function () {
        var list = $('option');
        for (var i = 0; i < list.length; i++) {
            var ele = list[i];
            if (ele.value === 'all')
                continue;
            if (ele.text.indexOf('(未评)') < 0)
                continue;
            console.log('自动选择:', ele.text);
            ele.selected = true;
            $('#submit3').click();
            return;
        }
        if (getSelecter().selectedIndex) {
            list[0].selected = true;
            $('#submit3').click();
        }
    };
    if (getSelecter().selectedOptions[0].text.indexOf('(未评)') < 0)
        autoSelect();
    $('body').prepend('教学评价自动填充已加载 - yuanlu.');
    var allOption = $('input[value=E]');
    if (!allOption.length)
        return;
    setTimeout(function () { return allOption.click(); }, 500); //自动选择"完全赞同"
    $('#submit01').click(function () { return setTimeout(autoSelect, 500); });
})();
