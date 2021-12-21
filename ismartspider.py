import hashlib
import time
import json
import requests
import frida
class RmotePhone:#调用前手机需安装frida
    def __init__(self):#加载frida
        device = frida.get_usb_device()
        pid = device.spawn(["com.up366.ismart"])
        session = device.attach(pid)
        device.resume(pid)
        src = '''
        function getUt(str) {
    var result1=''
    Java.perform(function(){
        var clazz = Java.use('com.up366.common.StringUtils')
        result1 = clazz.getUt(str,22)
    });
    return result1
}
function getdID() {
    var result2=''
    Java.perform(function(){
        var cls = Java.use("com.up366.common.global.GB")
        result2 = cls.globalCallBack.value.getUniqueDeviceId()
    })
    return result2
}
rpc.exports = {f1:getUt,f2:getdID}
        '''#jshook
        self.script = session.create_script(src)
        def on_msg(message,data):
            print(message)
        self.script.on('message',on_msg)
        self.script.load()
        self.did = ''
    def getUt(self, s: str) -> str:#获取登录时所用的ut值
        return self.script.exports.f1(s)
    def getUniqueDeviceId(self) -> str:#获取登录时所用的UniqueDeviceId值
        if self.did != '':
            return self.did
        else:
            rsp = self.script.exports.f2()
            self.did = rsp
            return rsp
class ismartUtils:
    def __init__(self,ph: RmotePhone):
        self.ph = ph
        self.userinfo = {}
        self.did = self.ph.getUniqueDeviceId()
    def _md5(s: str):
        return hashlib.md5(s.encode(encoding='utf-8')).hexdigest()

    def _pwdprocessor(pwd: str):
        return ismartUtils._md5("{0}fa&s*l%$k!fq$k!ld@fjlk".format(ismartUtils._md5(pwd)))

    def doLogin(self, username: str, pwd: str):#模拟登录，返回用户信息
        pwd = ismartUtils._pwdprocessor(pwd)
        ut = self.ph.getUt(username + pwd)
        data = f'password={pwd}&username={username}&ut={ut}'
        heads = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Android-Ismart-Moblie 2.4.3',
            'X-Requested-With': 'android',
            'clientId': self.did,
            'uid': '0',
            'XOT': '1.4.5-rc.1',
            'Connection': 'Keep-Alive',
            'Host': 'sso.ismartlearning.cn',
            'Content-Length': str(len(data)),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url = 'https://sso.ismartlearning.cn/v2/tickets-v2'
        response = requests.post(url=url, headers=heads, data=data.encode('utf-8'))
        dic = {}
        dic['cookies'] = response.cookies.get_dict()
        dic['content'] = json.loads(response.text)
        dic['headers'] = response.headers
        print('用户信息：',dic['content'])
        self.userinfo = dic
    def getServerTicket(self,data:str) -> str:#这里是service=https%3A%2F%2Fbook-api.ismartlearning.cn%2Fclient%2Fbooks%2Fbuy-book
        url ='https://sso.ismartlearning.cn/v1/serviceTicket'
        heads = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Android-Ismart-Moblie 2.4.3',
            'X-Requested-With': 'android',
            'clientId': ph.getUniqueDeviceId(),
            'uid': str(self.userinfo['content']['data']['uid']),
            'XOT': '1.4.5-rc.1',
            'Connection': 'Keep-Alive',
            'Host': 'sso.ismartlearning.cn',
            'Content-Length': str(len(data)),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie':f"CASTGC={self.userinfo['cookies']['CASTGC']}; acw_tc={self.userinfo['cookies']['acw_tc']}; SESSION={self.userinfo['cookies']['SESSION']}; BIGipServergj_zuul_pool={self.userinfo['cookies']['BIGipServergj_zuul_pool']}"
        }
        response = requests.post(url,data=data.encode('utf-8'),headers=heads)
        print('获取st：',json.loads(response.text)['data']['serverTicket'])
        return json.loads(response.text)['data']['serverTicket']
    def getbuy_books(self,st:str) -> str:#返回新的session值
        url = 'https://book-api.ismartlearning.cn/client/books/buy-book?ticket=' + st
        heads = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Android-Ismart-Moblie 2.4.3',
            'X-Requested-With': 'android',
            'clientId': self.did,
            'uid': str(self.userinfo['content']['data']['uid']),
            'XOT': '1.4.5-rc.1',
            'Connection': 'Keep-Alive',
            'Host': 'book-api.ismartlearning.cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f"CASTGC={self.userinfo['cookies']['CASTGC']}"
        }
        response = requests.get(url,headers=heads)
        print('书籍信息：',response.text)
        print('新的session：',response.headers['Set-Cookie'].split(';')[0].split('=')[1])
        return response.headers['Set-Cookie'].split(';')[0].split('=')[1]
    def getBooktree(self,bookId:str,bookType:int,nsession:str) -> dict:#获取图书节点信息,新大学英语视听说1：bookId=BC9B3ABD9ED9E97007029CF062EAF442&bookType=2
        url = 'https://book-api.ismartlearning.cn/client/books/tree'
        data = f'bookId={bookId}&bookType={bookType}'
        heads = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Android-Ismart-Moblie 2.4.3',
            'X-Requested-With': 'android',
            'clientId': self.did,
            'uid': str(self.userinfo['content']['data']['uid']),
            'XOT': '1.4.5-rc.1',
            'Connection': 'Keep-Alive',
            'Host': 'book-api.ismartlearning.cn',
            'Content-Length': str(len(data)),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie' : f"SESSION={nsession}; CASTGC={self.userinfo['cookies']['CASTGC']}"
        }
        response = requests.post(url,headers=heads,data=data.encode('utf-8'))
        print('获取节点信息成功')
        return json.loads(response.text)

if __name__ == '__main__':
    ph = RmotePhone()
    time.sleep(1)
    obj = ismartUtils(ph)
    obj.doLogin('账号', '密码')
    st = obj.getServerTicket('service=https%3A%2F%2Fbook-api.ismartlearning.cn%2Fclient%2Fbooks%2Fbuy-book')
    nsession = obj.getbuy_books(st)
    dic = obj.getBooktree('BC9B3ABD9ED9E97007029CF062EAF442', 2, nsession)
    with open('answer.json','w') as f:
        f.write(json.dumps(dic))



