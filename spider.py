from bs4 import BeautifulSoup
import requests
import re
import time
import json
from lxml import etree
def get_topics(topics):
    headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
    }
    a=requests.session()
    '''
    s=a.get('https://www.zhihu.com/topics',headers=headers)
    soup=BeautifulSoup(s.text,'html.parser')
    hrefs=soup.find_all("a",target='_blank')
    for x in hrefs:
        ornum=x.get("href")
        num=re.findall('/topic/(\d*)',ornum)
        if num:
            topics.add(num[0])
    '''
    father_topicid=[1761,3324,833,99,69,113]
    for i in father_topicid:
        offset=0
        while 1:
            time.sleep(0.2)
            data = {'method': 'next',
                    "params": json.dumps({"topic_id": i, "offset": offset, "hash_id": ""})}
            try:
                nexts=a.post('https://www.zhihu.com/node/TopicsPlazzaListV2',data=data,headers=headers)
                n=json.loads(nexts.text)['msg']
                if len(n) == 0:
                    print("break 0")
                    break
            except:
                print("break 1")
                break

            for x in n:
                topic_id=re.findall('<a target="_blank" href="/topic/(\d*)">', x)[0]
                topic_name=re.findall('<strong>(.*)</strong>', x)[0]
                topics.add((topic_id, topic_name))
            offset += 20
            print(len(topics))
    print(topics)

def get_top_answer(url,topic_name,top_answer_list,question_id_set):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
    }
    offset=0
    topics = {}
    topics['topic']=topic_name
    top_answers = []
    count = 0
    while count<20:
        s=requests.get(url+str(offset)+'&limit=10',headers=headers)
        try:
            data=json.loads(s.text)['data']

        except:
            print("break 2")
            break
        for x in data:
            #print(x['target']['author'])
            #print(x['target']['voteup_count'])
            try:
                #print(x['target']['question'])
                answer = {}
                answer['question_title']=x['target']['question']['title']
                answer['question_url']=x['target']['question']['url'].replace('api/v4/','')
                question_id_set.add(re.findall('questions/(\d*)',x['target']['question']['url'])[0])
                answer['username']=x['target']['author']['name']
                answer['userlink']=x['target']['author']['url'].replace('api/v4/','')
                answer['answer_url']=x['target']['url'].replace('api/v4/','')
                answer['content']=x['target']['content']
                answer['voteup']=x['target']['voteup_count']
                top_answers.append(answer)
                #print(x['target']['content'])
                count=count+1
            except:
                pass
        print('count'+str(count))
        offset+=10
        paging=json.loads(s.text)['paging']
        if paging['is_end']==True:
            break

    topics['top_answer_20']=top_answers
    if count >= 20:
        top_answer_list.append(topics)


def from_topic_to_answer(topics,question_id_set):
    top_answer_list=[]
    url1='https://www.zhihu.com/api/v4/topics/'
    url2='/feeds/essence?include=data%5B%3F(target.type%3Dtopic_sticky_module)%5D.target.data%5B%3F(target.type%3Danswer)%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F(target.type%3Dtopic_sticky_module)%5D.target.data%5B%3F(target.type%3Danswer)%5D.target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Dtopic_sticky_module)%5D.target.data%5B%3F(target.type%3Darticle)%5D.target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Dtopic_sticky_module)%5D.target.data%5B%3F(target.type%3Dpeople)%5D.target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Danswer)%5D.target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F(target.type%3Danswer)%5D.target.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Darticle)%5D.target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Cauthor.badge%5B%3F(type%3Dbest_answerer)%5D.topics%3Bdata%5B%3F(target.type%3Dquestion)%5D.target.annotation_detail%2Ccomment_count%3B&offset='
    while len(topics)!=0 and len(top_answer_list)<500:
        time.sleep(0.2)
        topic_tup=topics.pop()
        print(topic_tup)
        url=url1+topic_tup[0]+url2
        get_top_answer(url,topic_tup[1],top_answer_list,question_id_set)
    with open('D:\\top_answer.json','w+',encoding='utf-8') as f:
       json.dump(top_answer_list,f,ensure_ascii=False,indent=4)


def get_question_answer(question_id_set):
    origin_url='https://www.zhihu.com/question/'
    next_url1='https://www.zhihu.com/api/v4/questions/'
    next_url2='/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset='
    next_url3='&platform=desktop&sort_by=default'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
    }
    count=0
    question_answer_list=[]
    while count<500 and len(question_id_set)!=0:
        try:
            count+=1
            question_dic = {}
            question_topics=[]
            question_answer=[]
            question_id=question_id_set.pop()
            s=requests.get(origin_url+str(question_id),headers=headers)

            ''' get detail description
            soup = BeautifulSoup(s.text, "html.parser")
            load_text = soup.find("script", id="js-initialData")
            details=detailjson.loads(load_text.get_text())['initialState']['entities']['questions'][str(question_id)]['detail']
            '''
            soup = BeautifulSoup(s.text, "html.parser")
            question_dic['title'] = soup.find_all('h1', attrs={"class": "QuestionHeader-title"})[0].get_text()
            tag_contents = soup.find_all('a', attrs={"class": "TopicLink"})
            for tag in tag_contents:
                tags={}
                tags['tag']=tag.get_text()
                tags['link']='https'+tag.get("href")
                question_topics.append(tags)
            question_dic['topics']=question_topics
            offset=0
            while 1:
                next_url=next_url1+str(question_id)+next_url2+str(offset)+next_url3
                time.sleep(0.2)
                try:
                    ans=requests.get(next_url,headers=headers)
                    ans.encoding = 'utf-8'
                    data = json.loads(ans.text)['data']
                    for x in data:
                        answer_detail={}
                        answer_detail['userName']=x['author']['name']
                        answer_detail['userLink'] =x['author']['url'].replace('api/v4/','')
                        answer_detail['content'] =x['content']
                        answer_detail['upvote'] =x['voteup_count']
                        answer_detail['comment'] =''
                        question_answer.append(answer_detail)
                    offset+=5
                    paging= json.loads(ans.text)['paging']
                    if paging['is_end']==True:
                        break
                    print(offset)
                except:
                    print("break 3")
                    break

            question_dic['answer']=question_answer
            question_answer_list.append(question_dic)
            print('当前问题：'+str(question_id)+'总数'+str(count))
        except:
            count-=1
    with open('D:\\answer.json','w+',encoding='utf-8') as f:
       json.dump(question_answer_list,f,ensure_ascii=False,indent=4)



topics=set()
question_id_set=set()
get_topics(topics)
from_topic_to_answer(topics,question_id_set)
print("\n\n\ntopics ok\n\n\n")
get_question_answer(question_id_set)

