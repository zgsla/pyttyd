import './jsencrypt.min.js'

export function Encryptor() {
    var key = CryptoJS.lib.WordArray.random(32);
    var iv = CryptoJS.lib.WordArray.random(16);
    var password = JSON.stringify({
        'key': key.toString(CryptoJS.enc.Base64),
        'iv': iv.toString(CryptoJS.enc.Base64)
    })
    
    var encrypt = new JSEncrypt();
    var publickey = $('#publickey').data('text')
    encrypt.setPublicKey(publickey);
    return {
        key, 
        iv, 
        password,
        auth: encrypt.encrypt(password),
        encrypt: function (text) {
            var encrypted = CryptoJS.AES.encrypt(
                CryptoJS.enc.Utf8.parse(text),
                key,
                {
                    iv,
                    mode: CryptoJS.mode.CBC,
                    padding: CryptoJS.pad.Pkcs7
                }
            )
            return CryptoJS.enc.Base64.stringify(encrypted.ciphertext)
        },
        decrypt: function(encrypted) {
            var decryped = CryptoJS.AES.decrypt(
                encrypted,
                key,
                {
                    iv,
                    mode: CryptoJS.mode.CBC,
                    padding: CryptoJS.pad.Pkcs7
                }
            ).toString(CryptoJS.enc.Utf8)
            return JSON.parse(decryped);
        }
    }
}