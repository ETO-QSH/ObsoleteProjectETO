const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);
window = dom.window;
document = window.document;
XMLHttpRequest = window.XMLHttpRequest;

// 设置 Cookie 的函数
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
}

const JSEncrypt = require('jsencrypt');
const { strEnc } = require('./des.js');

// 登录函数
function login(u, p, publicKey) {

    setCookie('neusoft_cas_un', u, 7);
    setCookie('neusoft_cas_pd', strEnc(p, 'neusoft', 'cas', 'pd'), 7);

    var encrypt = new JSEncrypt();
    encrypt.setPublicKey(publicKey);

    var encryptedUsername = encrypt.encrypt(u);
    var encryptedPassword = encrypt.encrypt(p);

    // 返回加密后的用户名和密码
    return {
        neusoft_cas_un: u,
        neusoft_cas_pd: strEnc(p, 'neusoft', 'cas', 'pd'),
        encryptedUsername: encryptedUsername,
        encryptedPassword: encryptedPassword
    };
}

// 暴露 login 函数供外部调用
module.exports = {
    login: login
};