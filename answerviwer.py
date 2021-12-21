import json
import os
import zipfile
import requests
import re

class _SinglePageObj:#容器类
    def __init__(self, id, fileId, parentId, name):
        self.id = id
        self.fileId = fileId
        self.parentId = parentId
        self.name = name
class _SingleChapterObj:
    def __init__(self, id, parentId, name):
        self.id = id
        self.parentId = parentId
        self.name = name
class _SingleUnitObj:
    def __init__(self, id, name):
        self.id = id
        self.name = name
class AnswerViewer:
    def __init__(self,jsonfile='answer.json'):
        with open(jsonfile,'r') as f:
            j:dict = json.loads(f.read())
        self.chapter2page = {}#储存chapter(id)对于的page
        for item in j['data']['pages']:
            id = item['id']
            parentid = item['parentId']
            fileId = item['fileId']
            name = item['name']
            pageobj = _SinglePageObj(id,fileId,parentid,name)
            if parentid in self.chapter2page.keys():
                self.chapter2page[parentid].append(pageobj)
            else:
                self.chapter2page[parentid] = []
                self.chapter2page[parentid].append(pageobj)
        self.unitdict2chapters = {}#unit(id)对于的chapter
        self.unitlist = []
        for item in j['data']['chapters']:
            if 'Unit' in item['name']:
                obj = _SingleUnitObj(item['id'],item['name'])
                self.unitlist.append(obj)
        for item in j['data']['chapters']:
            if 'Unit' not in item['name']:
                id = item['id']
                parentid = item['parentId']
                name = item['name']
                obj = _SingleChapterObj(id,parentid,name)
                if parentid in self.unitdict2chapters.keys():
                    self.unitdict2chapters[parentid].append(obj)
                else:
                    self.unitdict2chapters[parentid] = []
                    self.unitdict2chapters[parentid].append(obj)
    def _download_paser(self, fileId:str) -> str:
        heads = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
        }
        url = f'http://fs.ismartlearning.cn/download/{fileId}'
        print(f'正在下载{fileId}')
        down_res = requests.get(url=url,headers=heads)
        with open(f'{fileId}.zip','wb+') as f:
            f.write(down_res.content)
        z = zipfile.ZipFile(f'{fileId}.zip')
        if 'correctAnswer.xml' in z.namelist():
            with z.open('correctAnswer.xml') as f:
                content = f.read().decode('utf-8')
            li = list(re.findall('<!\[CDATA\[.*]]>',content))
            for i in range(len(li)):
                li[i] = li[i][9:-3]
            answer = ','.join(li)
            z.close()
            os.remove(f'{fileId}.zip')
            return answer
        else:
            return '答案略'
    def search(self):
        for i in self.unitlist:
            print(i.name)
        unit = eval(input('请输入单元序号:'))-1
        print('================================')
        for i in self.unitdict2chapters[self.unitlist[unit].id]:
            print(i.name)
        chapter = eval(input('请输入章节序号:')) - 1
        print('================================')
        chapterid = self.unitdict2chapters[self.unitlist[unit].id][chapter].id
        for i in self.chapter2page[chapterid]:
            print(i.name)
        print('================================')
        level = eval(input('请输入关卡序号:')) - 1
        fid = self.chapter2page[chapterid][level].fileId
        answer = self._download_paser(fid)
        print('答案是：',answer)
if __name__ == '__main__':
    a = AnswerViewer()
    a.search()