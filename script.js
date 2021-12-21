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