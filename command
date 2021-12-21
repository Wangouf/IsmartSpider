frida-ps -U
adb forward tcp:27043 tcp:27043
adb forward tcp:27042 tcp:27042
adb push frida-server-15.1.14-android-arm /data/local/tmp/frida-server
adb shell
su
./data/local/tmp/fs