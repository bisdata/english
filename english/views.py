
from django.shortcuts import render_to_response,render,redirect
from english.models import article,User,performance,question,wordmeaning,mcq,fillblank,truefalse,morethanonechoice,sample_question,sample_performance,theory,article_visited,topic_score,verb_form,common_words,dictionary,bookmark,adjective_form,list1,bookmark_questions,bookmark_attempted
import json
from django.db.models import Count
from django.http import HttpResponse,HttpResponseRedirect
from english.forms.register import RegistrationForm
from english.forms.authenticate import AuthenticationForm
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
import ast
import math
import urllib
from xml.dom import minidom
import sys,codecs,locale
import re 
import random,bs4,requests
from beautifulsoup import *
from sys import exit
from english.article_ques import question_generation
import nltk
from nltk.corpus import wordnet as wn
from english.anurag import anurag,final
from english.pos import vocab
from django.db.models import F
from random import shuffle



# Create your views here.
def show_article_list(request,bit=0):
	if not request.user.is_authenticated():
		return render_to_response("start.html")
	else:
		listing=list(article.objects.filter(article_type=1).values('id','image','heading','level','summary'))
		listing=json.dumps(listing)


		return render_to_response("list.html",{'list':listing,"email":request.user.email,'bit':bit})


def update2(request):
	key1 = "4558af08-f4f8-450a-967e-498a744be6f5"
	key2="43799629-23c3-49c8-b945-9b64e03935b0"
	music_url="http://media.merriam-webster.com/soundc11/" #/a/apple001.wav
	listing=list(article.objects.values('id','content'))
	listing=json.dumps(listing)
	listing=ast.literal_eval(listing)
	for i in range(len(listing)):
		f = listing[i]['content']

		#return HttpResponse(f)'''
		for word in f.split():
			k=word
			usock = urllib.urlopen('http://www.dictionaryapi.com/api/v1/references/collegiate/xml/'+ word +'?key='+key2)
			xmldoc = minidom.parse(usock)
			usock.close()  
			a= xmldoc.firstChild
			for i in range(1,len(a.childNodes)/2+1):
				entry = a.childNodes[i*2-1]
				if entry.hasAttribute("id"):
					word = entry.getAttribute("id")
					if word.find("[")>-1:
						pp = word.find("[")
						word=word[:pp]
					else:
						word=word
						b=wordmeaning.objects.filter(word_name=k).count()
						if k==word and a>0:
							try:
								su = entry.getElementsByTagName('sound')[0]
								soun = su.getElementsByTagName('wav')[0]
								sound = soun.childNodes[0].toxml()
								urllib.urlretrieve(music_url+sound[0]+'/'+sound,"C:/Python27/practice/regex/sound/"+sound)
							except:
								pass
								try:
									de = entry.getElementsByTagName('def')[0]
									dt = de.getElementsByTagName('dt')[0]
									meaning = dt.firstChild.toxml()
									if meaning.find("(")>-1 and meaning.find(")")>-1 :
										#print "Meaning1:" + meaning
										wordmeaning.objects.create(word_name=k,word_meaning=meaning)
									elif meaning.find("(")>-1:
										b = meaning.find("(")
										#print "Meaning2:" + meaning[:b-1]
										wordmeaning.objects.create(word_name=k,word_meaning=meaning[:b-1])
									else:
										#print "Meaning3:" + meaning
										wordmeaning.objects.create(word_name=k,word_meaning=meaning)
								except:
									pass
			
def open_article(request,articleid):
	if not request.user.is_authenticated():
		return render_to_response("start.html")
	else:
		parag=[]

		if_visited=article_visited.objects.filter(user_id=request.user,article_id__id=articleid).count()
		if if_visited==0:
			listing=list(article.objects.filter(id=articleid).values('id','image','heading','summary','content'))
			listing=json.dumps(listing)
			listing=ast.literal_eval(listing)
			news= open("article.txt","w")
			news.write(listing[0]['content'])
			news.close()
			topic=topic_score.objects.filter(user_id=request.user).count()
			
			if topic==0:
				topic_score.objects.create(user_id=request.user,noun_score=1,pronoun_score=2,adverb_score=3,verb_score=4,adjective_score=5,conjunction_score=6,article_score=7,determiner_score=8)
			#question_list=list(question.objects.filter(article_id__id=articleid).values('id','question_text','choice1','choice2','choice3','choice4'))
			#question_list=json.dumps(question_list)
			article_visited.objects.create(user_id=request.user,article_id_id=articleid)
			weak_list=list(topic_score.objects.filter(user_id=request.user).values('noun_score','pronoun_score','adjective_score','adverb_score','verb_score','determiner_score','conjunction_score'))
			weak_list=json.dumps(weak_list)
			weak_list=ast.literal_eval(weak_list)
			a=sorted(weak_list[0], key=weak_list[0].__getitem__)
			mydict={'noun_score':1,'pronoun_score':2,'adjective_score':3,'adverb_score':4,'verb_score':5,'conjunction_score':6,'article_score':7,'determiner_score':8}
			for i in range(len(a)):
				for key, value in mydict.items():
					if a[i]==key:
						a[i]=value
			
			
			countdict=[0,0,0]
			weak_list=list()
			weak_list.append(a[0])
			weak_list.append(a[1])
			weak_list.append(a[2])
			count_list=list(sample_question.objects.filter(article_id__id=articleid,question_type_type=2,subtopic__in=weak_list).values('subtopic'))
			count_list=json.dumps(count_list)
			count_list=ast.literal_eval(count_list)
			for i in range(len(count_list)):
				if count_list[i]['subtopic']==weak_list[0]:
					countdict[0]+=1
				elif count_list[i]['subtopic']==weak_list[1]:
					countdict[1]+=1
				elif count_list[i]['subtopic']==weak_list[2]:
					countdict[2]+=1
			for i in range(len(countdict)):
				if countdict[i]==0:
					weak_list[0]=a[3]
				elif countdict[1]==0:
					weak_list[1]=a[3]
				elif countdict[2]==0:
					weak_list[2]=a[3]
				elif countdict[0]==0 and countdict[1]==0:
					weak_list[0]=a[3]
					weak_list[1]=a[4]
				elif countdict[0]==0 and countdict[2]==0:
					weak_list[0]=a[3]
					weak_list[2]=a[4]
				elif countdict[1]==0 and countdict[2]==0:
					weak_list[1]=a[3]
					weak_list[2]=a[4]
				elif countdict[0]==0 and countdict[1]==0 and countdict[2]==0:
					weak_list[0]=a[3]
					weak_list[1]=a[4]
					weak_list[2]=a[5]






			
			

			grammar_list=list(sample_question.objects.filter(article_id__id=articleid,question_type_type=2,subtopic__in=weak_list).annotate(id1=F('id')).exclude(tag=1).values('id1','question_text','paragraph_pos','sentence_pos').order_by('subtopic')[:6])
			grammar_list=json.dumps(grammar_list)
			
			

			
			

			grammar_list=ast.literal_eval(grammar_list)
			weird_list=list(sample_question.objects.filter(tag=1,article_id__id=articleid,subtopic__in=weak_list).annotate(id1=F('id')).values('id1','question_text','subtopic','paragraph_pos','sentence_pos','word'))
			weird_list=json.dumps(weird_list)
			weird_list=ast.literal_eval(weird_list)

			
			
			sup_list=list()
			for i in range(len(weird_list)):
				sup_list.append(weird_list[i]['subtopic'])

			add_list=list(sample_question.objects.filter(tag=1,subtopic__in=sup_list).annotate(id1=F('id')).exclude(article_id__id=articleid).values('id1','question_text','subtopic','paragraph_pos','sentence_pos','word').order_by('subtopic')[:len(weird_list)])
			add_list=json.dumps(add_list)
			add_list=ast.literal_eval(add_list)
			vocabulary_list=list(sample_question.objects.filter(article_id__id=articleid,subtopic=9).annotate(id1=F('id')).exclude(tag=1).values('id1','question_text','word'))
			vocabulary_list=json.dumps(vocabulary_list)
			
			

			
			

			vocabulary_list=ast.literal_eval(vocabulary_list)
			#print vocabulary_list
			for i in range(len(weird_list)):
				for j in range(i,len(add_list)):
					if weird_list[i]['subtopic']==add_list[j]['subtopic']:
						add_list[j]['paragraph_pos']=weird_list[i]['paragraph_pos']
						add_list[j]['sentence_pos']=weird_list[i]['sentence_pos']
						add_list[j]['word']=weird_list[i]['word']
						a,b=add_list[i],add_list[j]
						add_list[i],add_list[j]=b,a
			#for i in range(len(add_list)):
				
##print str(add_list[i]['sentence_pos'])+":"+str(add_list[i]['paragraph_pos'])+add_list[i]['word']
			
			


			
			tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
			#for i in range(len(add_list)):
					##print str((add_list[i]['paragraph_pos']))+" "+  str(add_list[i]['sentence_pos'])+ str(add_list[i]['word']) +str(add_list[i]['id1'])+ "\n"
			#for i in range(len(grammar_list)):
				##print str((grammar_list[i]['paragraph_pos']))+" "+  str(grammar_list[i]['sentence_pos'])+ str(grammar_list[i]['id1']) +"\n"

			
			
			
			
			#para=final()
		 	#return HttpResponse(para)
		 	question2=[[] for i in range(len(grammar_list+add_list+vocabulary_list))]
		 	#return HttpResponse(len(question2))
			for i in range(len(grammar_list)):
				question2[i].insert(0,grammar_list[i]['id1'])
				question2[i].insert(1,grammar_list[i]['paragraph_pos'])
				question2[i].insert(2,grammar_list[i]['sentence_pos'])
			
			
			for i in range(len(grammar_list),len(grammar_list+add_list)):
				question2[i].insert(0,add_list[i-len(grammar_list)]['id1'])
				question2[i].insert(1,add_list[i-len(grammar_list)]['paragraph_pos'])
				question2[i].insert(2,add_list[i-len(grammar_list)]['sentence_pos'])
				question2[i].insert(3,add_list[i-len(grammar_list)]['word'])


			for i in range(len(grammar_list+add_list),len(grammar_list+add_list+vocabulary_list)):
				question2[i].insert(0,vocabulary_list[i-len(grammar_list+add_list)]['id1'])
				question2[i].insert(1,vocabulary_list[i-len(grammar_list+add_list)]['word'])
			#print question2
			

			
			


			#return HttpResponse(question2)
			#return HttpResponse(para)
			para=final(question2)
			
			'''for i in range(len(question2)):
				if len(question2[i])>2:
					sent = para[question2[i][0]][question2[i][1]]
					ques_word = question2[i][2]
					le = len(ques_word)
					loc = sent.index(ques_word)
					para[question2[i][0]][question2[i][1]]  = sent[:loc] + "<span " +"id="+ ">"+ ques_word +"</span>" + sent[(loc+le):]
				else:
					#print  para[question2[i][0]][question2[i][1]] 
					para[question2[i][0]][question2[i][1]] = "<span " +"id="+ ">"+ para[question2[i][0]][question2[i][1]]+"</span>"'''
			
			
			for i in range(len(para)):
				tet=""
				for j in range(len(para[i])):
					tet+=" " + para[i][j]
				tet = "<p>"+tet+"</p>"
				parag.append(tet)
			
			front_content=""
			for i in range(len(parag)):
				front_content += parag[i]
			##print front_content
			
			
			
			
			new_list=list()
			vocab_list=list()
			for i in range(len(grammar_list)):
				
				new_list.append(grammar_list[i]['id1'])
			another_list=list()
			for i in range(len(add_list)):
				
				another_list.append(add_list[i]['id1'])
			wow=new_list+another_list
			for i in range(len(vocabulary_list)):
				
				vocab_list.append(vocabulary_list[i]['id1'])
			

			for i in range(len(grammar_list)):
				p=sample_performance.objects.create(user_id=request.user,sample_question_id_id=grammar_list[i]['id1'],paragraph_pos=grammar_list[i]['paragraph_pos'],sentence_pos=grammar_list[i]['sentence_pos'],response=0,article_under_id=articleid)
			for i in range(len(add_list)):
				p=sample_performance.objects.create(user_id=request.user,sample_question_id_id=add_list[i]['id1'],paragraph_pos=add_list[i]['paragraph_pos'],sentence_pos=add_list[i]['sentence_pos'],response=0,article_under_id=articleid,word=add_list[i]['word'])
			for i in range(len(vocabulary_list)):
				p=sample_performance.objects.create(user_id=request.user,sample_question_id_id=vocabulary_list[i]['id1'],response=0,article_under_id=articleid,word=vocabulary_list[i]['word'])
			grammar_choices=list(mcq.objects.filter(sample_question_id__id__in=new_list).values('sample_question_id','choice1','choice2','choice3','choice4'))
			grammar_choices=json.dumps(grammar_choices)
			
			grammar_choices=ast.literal_eval(grammar_choices)
			add_choices=list(mcq.objects.filter(sample_question_id__id__in=another_list).values('sample_question_id','choice1','choice2','choice3','choice4'))
			add_choices=json.dumps(add_choices)
			add_choices=ast.literal_eval(add_choices)
			vocabulary_choices=list(mcq.objects.filter(sample_question_id__id__in=vocab_list).values('sample_question_id','choice1','choice2','choice3','choice4'))
			vocabulary_choices=json.dumps(vocabulary_choices)
			
			vocabulary_choices=ast.literal_eval(vocabulary_choices)

			responsejson=list()
			responsejson2=list()
			responsejson=(grammar_list+add_list+vocabulary_list)
			responsejson2=(grammar_choices+add_choices+vocabulary_choices)
			#print "hi response json is " +str(responsejson2)
			for i in range(len(responsejson)):
				for j in range(i,len(responsejson2)):
					if responsejson[i]['id1']==responsejson2[j]['sample_question_id']:
						responsejson2[j],responsejson2[i]=responsejson2[i],responsejson2[j]

			#return HttpResponse(front_content)
			#return HttpResponse(parag)
			return render_to_response("test.html",{'status':"not attempted",'question_list':responsejson,'choices_list':responsejson2,'content':front_content,'other_details':json.dumps(listing)})
			#?return render_to_response("test.html",{'content':"<p>ghhhhghghghg</p>"})
	   	else:
	   		listing=list(article.objects.filter(id=articleid).values('id','image','heading','summary','content'))
			listing=json.dumps(listing)
			listing=ast.literal_eval(listing)
			news= open("article.txt","w")
			news.write(listing[0]['content'])
			news.close()
	   		
	   		#attempted_list=list(performance.objects.filter(question_id2__article_id__id=articleid,user_id__id=request.user.id).values('question_id2__id','question_id2__choice1','response','question_id2__right_choice','question_id2__choice2','question_id2__choice3','question_id2__choice4'))
			attempted_grammar_list=list(sample_performance.objects.filter(user_id=request.user,article_under__id=articleid,sample_question_id__tag=0).exclude(sample_question_id__subtopic=9).annotate(id1=F('sample_question_id__id'),question_text=F('sample_question_id__question_text')).values('id1','question_text','response','sentence_pos','paragraph_pos'))
			attempted_grammar_list=json.dumps(attempted_grammar_list)
			#return HttpResponse(attempted_grammar_list)


			##print attempted_grammar_list
			
			#attempted_grammar_list=json.loads(attempted_grammar_list)
			attempted_grammar_list=ast.literal_eval(attempted_grammar_list)

			attempted_add_list=list(sample_performance.objects.filter(user_id=request.user,article_under__id=articleid,sample_question_id__tag=1).annotate(id1=F('sample_question_id__id'),question_text=F('sample_question_id__question_text')).values('id1','question_text','response','paragraph_pos','word','sentence_pos'))
			attempted_add_list=json.dumps(attempted_add_list)
			##print attempted_add_list
			
			#attempted_grammar_list=json.loads(attempted_grammar_list)
			attempted_add_list=ast.literal_eval(attempted_add_list)

			attempted_vocabulary_list=list(sample_performance.objects.filter(user_id=request.user,article_under__id=articleid,sample_question_id__subtopic=9).annotate(id1=F('sample_question_id__id'),question_text=F('sample_question_id__question_text')).values('id1','question_text','response','word'))
			attempted_vocabulary_list=json.dumps(attempted_vocabulary_list)
			#print attempted_vocabulary_list
			
			#attempted_grammar_list=json.loads(attempted_grammar_list)
			attempted_vocabulary_list=ast.literal_eval(attempted_vocabulary_list)


			question2=[[] for i in range(len(attempted_grammar_list+attempted_add_list+attempted_vocabulary_list))]
		 	#return HttpResponse(len(question2))
			for i in range(len(attempted_grammar_list)):
				question2[i].insert(0,attempted_grammar_list[i]['id1'])
				question2[i].insert(1,attempted_grammar_list[i]['paragraph_pos'])
				question2[i].insert(2,attempted_grammar_list[i]['sentence_pos'])
			
			
			for i in range(len(attempted_grammar_list),len(attempted_grammar_list+attempted_add_list)):
				question2[i].insert(0,attempted_add_list[i-len(attempted_grammar_list)]['id1'])
				question2[i].insert(1,attempted_add_list[i-len(attempted_grammar_list)]['paragraph_pos'])
				question2[i].insert(2,attempted_add_list[i-len(attempted_grammar_list)]['sentence_pos'])
				question2[i].insert(3,attempted_add_list[i-len(attempted_grammar_list)]['word'])


			for i in range(len(attempted_grammar_list+attempted_add_list),len(attempted_grammar_list+attempted_add_list+attempted_vocabulary_list)):
				question2[i].insert(0,attempted_vocabulary_list[i-len(attempted_grammar_list+attempted_add_list)]['id1'])
				question2[i].insert(1,attempted_vocabulary_list[i-len(attempted_grammar_list+attempted_add_list)]['word'])
			##print question2
			

			
			


			#return HttpResponse(question2)
			#return HttpResponse(para)
			para=final(question2)
			for i in range(len(para)):
				tet=""
				for j in range(len(para[i])):
					tet+=" " + para[i][j]
				tet = "<p>"+tet+"</p>"
				parag.append(tet)
			front_content=""
			for i in range(len(parag)):
				front_content += parag[i]
			new_list=list()
			vocab_list=list()

			for i in range(len(attempted_grammar_list)):
				
				new_list.append(attempted_grammar_list[i]['id1'])
			another_list=list()
			for i in range(len(attempted_add_list)):
				
				another_list.append(attempted_add_list[i]['id1'])

			for i in range(len(attempted_vocabulary_list)):
				
				vocab_list.append(attempted_vocabulary_list[i]['id1'])
			wow=new_list+another_list

			
			grammar_attempted_choices=list(mcq.objects.filter(sample_question_id__id__in=new_list).values('sample_question_id','choice1','choice2','choice3','choice4','right_choice'))
			grammar_attempted_choices=json.dumps(grammar_attempted_choices)

			
			grammar_attempted_choices=ast.literal_eval(grammar_attempted_choices)
			add_attempted_choices=list(mcq.objects.filter(sample_question_id__id__in=another_list).values('sample_question_id','choice1','choice2','choice3','choice4','right_choice'))
			add_attempted_choices=json.dumps(add_attempted_choices)
			add_attempted_choices=ast.literal_eval(add_attempted_choices)

			vocabulary_attempted_choices=list(mcq.objects.filter(sample_question_id__id__in=vocab_list).values('sample_question_id','choice1','choice2','choice3','choice4','right_choice'))
			vocabulary_attempted_choices=json.dumps(vocabulary_attempted_choices)

			
			vocabulary_attempted_choices=ast.literal_eval(vocabulary_attempted_choices)

			responsejson=list()
			responsejson2=list()
			responsejson=(attempted_grammar_list+attempted_add_list+attempted_vocabulary_list)
			responsejson2=(grammar_attempted_choices+add_attempted_choices+vocabulary_attempted_choices)
			for i in range(len(responsejson)):
				for j in range(i,len(responsejson2)):
					if responsejson[i]['id1']==responsejson2[j]['sample_question_id']:
						responsejson2[j],responsejson2[i]=responsejson2[i],responsejson2[j]
			
			


			return render_to_response("test.html",{'status':"attempted",'question_list':json.dumps(responsejson),'choices_list':json.dumps(responsejson2),'content':parag,'other_details':json.dumps(listing),"email":request.user.email})

			


			


		

def load_more(request,id):
	newarticle_list=list(article.objects.values('id','heading','level','summary').filter(id__in=[id,id-2,id-3,id-4,id-5,id-6]))
	newarticle_list=json.dumps(newarticle_list)
	return HttpResponse(newarticle_list)
@csrf_exempt
def response(request):
	current_user=request.user
	if request.method=='POST':
		newdict=json.loads(request.body)
		newdict=json.dumps(newdict)
		newdict=ast.literal_eval(newdict)
		
		question_id=str(newdict['question_id'])
		selected_choice=str(newdict['selected_choice'])
		question_type=str(newdict['question_type'])
		if question_type==1:
		
		
			right_choice=list(mcq.objects.filter(sample_question_id__id=question_id).values('right_choice'))
			right_choice=json.dumps(right_choice)
			right_choice=ast.literal_eval(right_choice)

		
		
			p=sample_performance.objects.get(sample_question_id_id=question_id,user_id=current_user)
			p.response=selected_choice
			p.save()
		else:
			right_choice=list(bookmark_questions.objects.filter(id=question_id).values('right_choice'))
			right_choice=json.dumps(right_choice)
			right_choice=ast.literal_eval(right_choice)
			bookmark_attempted.objects.create(user_id=request.user,question_id_id=question_id,response=selected_choice)
			return bookmark_questions_api(request,bit=1)

		
	
		
	return HttpResponse(right_choice[0]['right_choice'])


def performance_stats(request):
	if not request.user.is_authenticated():
		return render_to_response("start.html")
	else:
		
		current_user=request.user.id
		grammar_correct=performance.objects.filter(user_id__id=current_user,question_id2__genre=2,key=1).count()
		grammar_total=performance.objects.filter(user_id__id=current_user,question_id2__genre=2).count()
		grammar_percentage=0.0
		if grammar_total==0:
			grammar_total=2
		grammar_percentage=(float(grammar_correct) /float(grammar_total))*100
		grammar_list={'num_correct':grammar_correct,'num_total':grammar_total,'percentage':grammar_percentage}
		grammar_list=json.dumps(grammar_list)
		vocab_correct=performance.objects.filter(user_id__id=current_user,question_id2__genre=1,key=1).count()
		vocab_total=performance.objects.filter(user_id__id=current_user,question_id2__genre=1).count()
		vocab_percentage=0.0
		if vocab_total==0:
			vocab_total=2
		vocab_percentage=(float(vocab_correct) /float(vocab_total))*100
		vocab_list={'num_correct':vocab_correct,'num_total':vocab_total,'percentage':vocab_percentage}
		vocab_list=json.dumps(vocab_list)
		comp_correct=performance.objects.filter(user_id__id=current_user,question_id2__genre=3,key=1).count()
		comp_total=performance.objects.filter(user_id__id=current_user,question_id2__genre=3).count()
		comp_percentage=0.0
		if comp_total==0:
			comp_total=2
		comp_percentage=(float(comp_correct) /float(comp_total))*100
		comp_list={'num_correct':comp_correct,'num_total':comp_total,'percentage':comp_percentage}
		comp_list=json.dumps(comp_list)
		
		
		
		return render_to_response('profile.html',{'grammar':grammar_list,'vocab':vocab_list,'comp':comp_list,"email":request.user.email})






@csrf_exempt
def register(request):
	if request.method == 'POST':
		
		#user = User.objects.create_user(password=request.GET.get('password',''),email=request.GET.get('email',''))
		selectedpackages = json.loads(request.body)
		new_json = json.dumps(selectedpackages)
		#return HttpResponse(str(new_json))
		newdict = ast.literal_eval(new_json)
		check=User.objects.filter(email=newdict['email']).count()
		if check==0:
		#kk = selectedpackages.account
		#return HttpResponse(str(newdict['email']))

			user = User.objects.create_user(password=str(newdict['password']),email=str(newdict['email']))
			#topic_score.objects.create(user_id_id=user.id,noun_score=0,pronoun_score=0,adverb_score=0,verb_score=0,adjective_score=0,conjunction_score=0,article_score=0,determiner_score=0)
			return HttpResponse(str("1"))
		else:
			return HttpResponse(str("2"))

		


@csrf_exempt
def login(request):

	if request.method == 'POST':
		selectedpackages = json.loads(request.body)
		new_json = json.dumps(selectedpackages)
		#return HttpResponse(str(new_json))
		newdict = ast.literal_eval(new_json)
		check=User.objects.filter(email=newdict['email']).count()
		if check==0:
			return HttpResponse(str("1"))
		elif check==1:
			user = authenticate(email=str(newdict['email']), password=str(newdict['password']))
			if user is not None:
				django_login(request,user)
				return HttpResponse(str("2"))

		else:
			return HttpResponse(str("3"))


def register2(request):
	return render_to_response("register.html")



def review(request):
	question_arr=request.session['question_arr'].split()
	selected_arr=request.session['selected_responses'].split()
	clauses = ' '.join(['WHEN id=%s THEN %s' % (id, i) for i, id in enumerate(question_arr)])  
	ordering = 'CASE %s END' % clauses  

	question=list(sample_question.objects.filter(id__in=question_arr).values('id','question_text').extra(  
           select={'ordering': ordering}, order_by=('ordering',)))
	clauses = ' '.join(['WHEN id=%s THEN %s' % (sample_question_id, i) for i, sample_question_id in enumerate(question_arr)])
	ordering = 'CASE %s END' % clauses  
	choices=list(mcq.objects.filter(sample_question_id__id__in=question_arr).values('sample_question_id','choice1','choice2','choice3','choice4','right_choice').extra(  
           select={'ordering': ordering}, order_by=('ordering',)))
	question=json.dumps(question)
	choices=json.dumps(choices)
	question=ast.literal_eval(question)
	choices=ast.literal_eval(choices)

	return 	render_to_response("review.html",{'question':json.dumps(question),'choice':json.dumps(choices),'response':json.dumps(selected_arr),'correct_count':request.session['correct_count']})



@csrf_exempt
def sample_test(request):
	x = random.randint(0,7)
	#x=4 	
	if request.method=='POST':

		newdict=json.loads(request.body)
		newdict=json.dumps(newdict)
		newdict=ast.literal_eval(newdict)
		request.session['count']+=1
		request.session['selected_responses']=request.session['selected_responses'][:]+str(newdict['selected_choice'])+" "

		if request.session['count'] == 6:
			current_user=request.user
			p=sample_performance.objects.create(user_id=current_user,noun_score=request.session['level_dr'][0],determiner_score=request.session['level_dr'][7],pronoun_score=request.session['level_dr'][1]
	    		,adjective_score=request.session['level_dr'][2],adverb_score=request.session['level_dr'][3],verb_score=request.session['level_dr'][4],conjunction_score=request.session['level_dr'][5],article_score=request.session['level_dr'][6])
			review(request)
			
			

		
	#	return HttpResponse(newdict['selected_choice'])
		if request.session['level_dr'][request.session['x']]=="9":
			if newdict['selected_choice'] == request.session['right_choice']:
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"3"+request.session['level_dr'][request.session['x']+1:]
				request.session['correct_count']+=1
				
				
				
				
				
				
				
				
				
			else:

				
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"1"+request.session['level_dr'][request.session['x']+1:]
				
			request.session['x']=x


		elif request.session['level_dr'][request.session['x']]=="0":
			if newdict['selected_choice'] == request.session['right_choice']:
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"1"+request.session['level_dr'][request.session['x']+1:]
				request.session['correct_count']+=1
				
				
				
			else:

				
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"0"+request.session['level_dr'][request.session['x']+1:]
			request.session['x']=x



		elif request.session['level_dr'][request.session['x']]=="1":
			if newdict['selected_choice'] == request.session['right_choice']:
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"2"+request.session['level_dr'][request.session['x']+1:]
				request.session['correct_count']+=1


				
				
				
			else:

				
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"0"+request.session['level_dr'][request.session['x']+1:]
			request.session['x']=x


		elif request.session['level_dr'][request.session['x']]=="2":
			if newdict['selected_choice'] == request.session['right_choice']:
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"3"+request.session['level_dr'][request.session['x']+1:]
				request.session['correct_count']+=1
				
				
				
			else:

				
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"1"+request.session['level_dr'][request.session['x']+1:]
			request.session['x']=x



		elif request.session['level_dr'][request.session['x']]=="3":
			if newdict['selected_choice'] == request.session['right_choice']:
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"3"+request.session['level_dr'][request.session['x']+1:]
				request.session['correct_count']+=1
				
				
				
			else:

				
				request.session['level_dr']=request.session['level_dr'][:request.session['x']]+"2"+request.session['level_dr'][request.session['x']+1:]
			request.session['x']=x




		



			

		

		
		
		if request.session['level_dr'][x] == "9":
			


			
	


			question_arr=request.session['question_arr'].split()
			
			question=list(sample_question.objects.filter(level=2,subtopic=int(request.session['pos_arr'][x])).exclude(id__in=question_arr).order_by('id')[:1].values('id','question_text','question_type','level','subtopic'))
			question=json.dumps(question)
			
			question=ast.literal_eval(question)
			
			request.session['question_id']=question[0]['id']
			request.session['question_arr']=request.session['question_arr'][:]+str(request.session['question_id'])+" "
			if question[0]['question_type']=="1":
				choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="2":
				choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="3":
				choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="4":
				choice=list(fillblank.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(fillblank.objects.filter(sample_question_id__id=question_id).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)



		if request.session['level_dr'][x] == "0":
			
			question_arr=request.session['question_arr'].split()
			question=list(sample_question.objects.filter(level=1,subtopic=int(request.session['pos_arr'][x])).exclude(id__in=question_arr).order_by('id')[:1].values('id','question_text','question_type','level','subtopic'))
			question=json.dumps(question)
			question=ast.literal_eval(question)
			request.session['question_id']=question[0]['id']
			request.session['question_arr']=request.session['question_arr'][:]+str(request.session['question_id'])+" "
			if question[0]['question_type']=="1":
				choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="2":
				choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="3":
				choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="4":
				choice=list(fillblank.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(fillblank.objects.filter(sample_question_id__id=question_id).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)




		if request.session['level_dr'][x] == "1":
			
			
			question_arr=request.session['question_arr'].split()
			question=list(sample_question.objects.filter(level=1,subtopic=int(request.session['pos_arr'][x])).exclude(id__in=question_arr).order_by('id')[:1].values('id','question_text','question_type','level','subtopic'))
			question=json.dumps(question)
			question=ast.literal_eval(question)
			request.session['question_id']=question[0]['id']
			request.session['question_arr']=request.session['question_arr'][:]+str(request.session['question_id'])+" "
			if question[0]['question_type']=="1":
				choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="2":
				choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="3":
				choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="4":
				choice=list(fillblank.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(fillblank.objects.filter(sample_question_id__id=question_id).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)





		if request.session['level_dr'][x] == "2":
			
			question_arr=request.session['question_arr'].split()
			question=list(sample_question.objects.filter(level=2,subtopic=int(request.session['pos_arr'][x])).exclude(id__in=question_arr).order_by('id')[:1].values('id','question_text','question_type','level','subtopic'))
			question=json.dumps(question)
			question=ast.literal_eval(question)
			request.session['question_id']=question[0]['id']
			request.session['question_arr']=request.session['question_arr'][:]+str(request.session['question_id'])+" "
			if question[0]['question_type']=="1":
				choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="2":
				choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="3":
				choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)
			if question[0]['question_type']=="4":
				choice=list(fillblank.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
				right_choice=list(fillblank.objects.filter(sample_question_id__id=question_id).values('right_choice'))
				right_choice=json.dumps(right_choice)
				right_choice=ast.literal_eval(right_choice)
				request.session['right_choice']=right_choice[0]['right_choice']
				choice=json.dumps(choice)
				choice=ast.literal_eval(choice)
				responsejson=question+choice
				responsejson=json.dumps(responsejson)
				return HttpResponse(responsejson)






		if request.session['level_dr'][x] == "3":
			
			question_arr=request.session['question_arr'].split()
	        question=list(sample_question.objects.filter(level=3,subtopic=int(request.session['pos_arr'][x])).exclude(id__in=question_arr).order_by('id')[:1].values('id','question_text','question_type','level','subtopic'))
	        question=json.dumps(question)

	        question=ast.literal_eval(question)
	        request.session['question_id']=question[0]['id']
	        
	        request.session['question_arr']=request.session['question_arr'][:]+str(request.session['question_id'])+" "
	        if question[0]['question_type']=="1":
	            choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
	            right_choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
	            right_choice=json.dumps(right_choice)
	            right_choice=ast.literal_eval(right_choice)
	            request.session['right_choice']=right_choice[0]['right_choice']
	            choice=json.dumps(choice)
	            choice=ast.literal_eval(choice)
	            
	            
	            responsejson=question+choice
	            
	            responsejson=json.dumps(responsejson)
	            return HttpResponse(responsejson)
	        if question[0]['question_type']=="2":
	            choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
	            right_choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
	            right_choice=json.dumps(right_choice)
	            right_choice=ast.literal_eval(right_choice)
	            request.session['right_choice']=right_choice[0]['right_choice']
	            choice=json.dumps(choice)
	            choice=ast.literal_eval(choice)
	            
	            
	            responsejson=question+choice
	            
	            responsejson=json.dumps(responsejson)
	            return HttpResponse(responsejson)

	        if question[0]['question_type']=="3":
	            choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
	            
	            right_choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
	            right_choice=json.dumps(right_choice)
	            right_choice=ast.literal_eval(right_choice)
	            request.session['right_choice']=right_choice[0]['right_choice']
	            choice=json.dumps(choice)
	            choice=ast.literal_eval(choice)
	            
	            
	            responsejson=question+choice
	            
	            responsejson=json.dumps(responsejson)
	            return HttpResponse(responsejson)
	        if question[0]['question_type']=="4":
	            choice=list(fillblank.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
	            
	            right_choice=list(fillblank.objects.filter(sample_question_id__id=question_id).values('right_choice'))
	            right_choice=json.dumps(right_choice)
	            right_choice=ast.literal_eval(right_choice)
	            request.session['right_choice']=right_choice[0]['right_choice']
	            choice=json.dumps(choice)
	            choice=ast.literal_eval(choice)
	            
	            
	            responsejson=question+choice
	           
	            responsejson=json.dumps(responsejson)
	            return HttpResponse(responsejson)

	    







	   

	if request.method=='GET':
		request.session['pos_ar']=list()
		
		
		request.session['pos_ar'].append(list(["noun","pronoun","verb","adverb","adjective","cojunction","preposition","interjection"]))
		
		
		
		
		request.session['pos_arr']="12345678" #2345678
		
		request.session['level_arr']="0123"
		
		request.session['level_dr']="99999999"
		request.session['selected_responses']=""

		
		#request.session['level_dr'].update({0:-1,1:-1,2:-1,3:-1,4:-1,5:-1,6:-1,7:-1})
		request.session['question_arr']=""
		request.session['corr']=1
		request.session['right_choice']=2;
		request.session['question_id']=0;
		request.session['incorr']=0
		request.session['x']=x
		request.session['count']=1
		request.session['correct_count']=0
		question=list(sample_question.objects.filter(level=2,subtopic=int(request.session['pos_arr'][x])).order_by('id')[:1].values('id','question_text','question_type','level','subtopic'))
		question=json.dumps(question)
		
		
		question=ast.literal_eval(question)
		request.session['question_id']=question[0]['id']

		
		request.session['question_arr']=request.session['question_arr'][:]+str(request.session['question_id'])+" "
		if question[0]['question_type']=="1":
			choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
	        right_choice=list(mcq.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
	        right_choice=json.dumps(right_choice)
	        right_choice=ast.literal_eval(right_choice)
	        request.session['right_choice']=right_choice[0]['right_choice']
	        choice=json.dumps(choice)
	        choice=ast.literal_eval(choice)
	        
	            
	        
	        responsejson=question+choice
	        
	        
	        responsejson=json.dumps(responsejson)

	        return render_to_response("assessment.html",{'response':responsejson})
	        return HttpResponse(responsejson)
		if question[0]['question_type']==2:
			choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
	        right_choice=list(morethanonechoice.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
	        right_choice=json.dumps(right_choice)
	        right_choice=ast.literal_eval(right_choice)
	        request.session['right_choice']=right_choice[0]['right_choice']
	        choice=json.dumps(choice)
	        choice=ast.literal_eval(choice)
	        
	            
	        responsejson={}
	        responsejson.update(choice)
	        responsejson.update(question)
	        responsejson=json.dumps(responsejson)
	        return HttpResponse(responsejson)

		if question[0]['question_type']==3:
			choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
	            
	        right_choice=list(truefalse.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
	        right_choice=json.dumps(right_choice)
	        right_choice=ast.literal_eval(right_choice)
	        request.session['right_choice']=right_choice[0]['right_choice']
	        choice=json.dumps(choice)
	        choice=ast.literal_eval(choice)
	        
	            
	        responsejson={}
	        responsejson.update(choice)
	        responsejson.update(question)
	        responsejson=json.dumps(responsejson)
	        return HttpResponse(responsejson)
		if question[0]['question_type']==4:
			choice=list(fillblank.objects.filter(sample_question_id__id=request.session['question_id']).values('choice1','choice2','choice3','choice4'))
	            
	        right_choice=list(fillblank.objects.filter(sample_question_id__id=request.session['question_id']).values('right_choice'))
	        right_choice=json.dumps(right_choice)
	        right_choice=ast.literal_eval(right_choice)

	            
	        
	        request.session['right_choice']=right_choice[0]['right_choice']
	        choice=json.dumps(choice)
	        choice=ast.literal_eval(choice)
	        
	            
	        responsejson={}
	        responsejson.update(choice)
	        responsejson.update(question)
	        responsejson=json.dumps(responsejson)
	        return HttpResponse(responsejson)




def tutorial(request,headname):
	topic=list(theory.objects.filter(heading=headname).values('heading','long_description','short_summary','example'))
	subtopic=list(theory.objects.filter(is_subtopic=headname).values('heading','long_description','short_summary','example'))
	topic=json.dumps(topic)
	subtopic=json.dumps(subtopic)
	topic=ast.literal_eval(topic)
	subtopic=ast.literal_eval(subtopic)
	responsejson=topic+subtopic
	responsejson=json.dumps(responsejson)
	#return HttpResponse(json.dumps(responsejson))

	return render_to_response("tutorial.html",{'list':responsejson})




def grammar_response(request):
	if request.method=='POST':
		selectedpackages = json.loads(request.body)
		new_json = json.dumps(selectedpackages)
		newdict = ast.literal_eval(new_json)
		right_choice=mcq.objects.filter(sample_question_id__id=newdict['selected_response']).values('right_choice')
		right_choice=json.dumps(right_choice)
		right_choice=json.loads(right_choice)
		right_choice=ast.literal_eval(right_choice)
		if newdict['selected_response']==right_choice[0]['right_choice']:
			t=sample_performance.objects.filter(sample_question_id__id=newdict['id'],user_id__id=request.user)
			t.response=newdict['selected_response']
			t.save()



def generate_question(request):
	if_parsed=list(article.objects.filter(parsed=False).values('id','content'))
	if_parsed=json.dumps(if_parsed)
	if_parsed=ast.literal_eval(if_parsed)
	if_parsed_list=list()
	for i in range(len(if_parsed)):
		if_parsed_list.append(if_parsed[i]['id'])
	newlist2=list()
	
	
	for i in range(len(if_parsed)):
		news= open("eco.txt","w")
		news.write(if_parsed[i]['content'])
		news.close()
		
		question_list=question_generation()
		
		
		
		for j in range(len(question_list[0])):
			try:
				p=sample_question.objects.create(article_id_id=if_parsed[i]['id'],question_text=question_list[0][j][1][0]+":"+question_list[0][j][1][1],subtopic=2,level=1,question_type=1,question_type_type=2,tag=question_list[0][j][4],paragraph_pos=question_list[1][j][0],sentence_pos=question_list[1][j][1],word=question_list[0][j][5])
			except IndexError:
				p=sample_question.objects.create(article_id_id=if_parsed[i]['id'],question_text=question_list[0][j][1][0]+":"+question_list[0][j][1][1],subtopic=2,level=1,question_type=1,question_type_type=2,tag=question_list[0][j][4],paragraph_pos=question_list[1][j][0],sentence_pos=question_list[1][j][1])


				#newlist2.append(p.pk)

			mcq.objects.create(sample_question_id_id=p.id,choice1=question_list[0][j][0][0],choice2=question_list[0][j][0][1],choice3=question_list[0][j][0][2],choice4=question_list[0][j][0][3],right_choice=question_list[0][j][2])
	news.close()
	gen_vocab_questions(request,if_parsed_list)


def verb_forms_gen(request,mylist):
	for i in range(len(mylist)):
		a=0
		try:
		
			res = requests.get('http://www.merriam-webster.com/dictionary'+'/'+mylist[i])
			soup = bs4.BeautifulSoup(res.text)
			elems=soup.select('.definition-list')
			meaning=elems[0].getText()
			
			meaning=meaning.split(':')
			meaning= meaning[1].strip('\n').encode('utf-8')
			wordmeaning.objects.create(word_name=mylist[i],word_meaning=meaning)
			
		except IndexError:
			a=1

def findvocab(request,Word):
	newlist=list()
	newlist_array=list(bookmark.objects.exclude(word=Word).values('word'))
	newlist_array=json.dumps(newlist_array)
	newlist_array=ast.literal_eval(newlist_array)
	for i in range(len(newlist_array)):
		newlist.append(newlist_array[i]['word'])
	#print newlist



	'''if_parsed=list(article.objects.filter(parsed=False).values('id','content'))
	if_parsed=json.dumps(if_parsed)

	if_parsed=ast.literal_eval(if_parsed)
	
	
	for i in range(len(if_parsed)):
		b=vocab(if_parsed[i]['content'])
		myvocab=list()
		newvocab=list()
		for h in range(len(b)):
			find_word=common_words.objects.filter(word_anurag=b[h]).count()
			if find_word>0 and len(b[h])>2:
				myvocab.append(b[h])
		
		verb_forms_gen(request,mylist=myvocab)

				
		
					#pk=dictionary.objects.create(word_meaning=string)
					#url="http://words.bighugelabs.com/api/2/6315f684524176c55a924bccc603e395"+"/"+myvocab[i]+"/"+"json"
					#response = urllib.urlopen(url)
					#data = json.loads(response.read())
			
		
		
		newlist=myvocab'''
	question2=[[] for j in range(2)]	#syn=synonyms.objects.create(word_id=pk,synonym_def="jj")
	for j in range(1):
		#num=random.randint(0,len(newlist))
		#word=newlist[num]
		word=Word
		question2[j].insert(0,word)
		choice=list()
		k=list()
		newlistnew=['soldier','patriotic','big','random','happy']

		
		url="http://words.bighugelabs.com/api/2/6315f684524176c55a924bccc603e395"+"/"+word+"/"+"json"
		response = urllib.urlopen(url)
		try:
			data = json.loads(response.read())
			similar=list()
			antonym=list()
			

			for o in range(len(wn.synsets(word)[0].hypernyms())):
					try:
						choice.append(wn.synsets(word)[0].hypernyms()[o].name().split('.')[0])
					except IndexError:
						pass
			for f in range(len(wn.synsets(word)[0].hyponyms())):
				try:
					choice.append(wn.synsets(word)[0].hyponyms()[f].name().split('.')[0])
				except IndexError:
					pass
			try:
				similar=data['verb']['sim']
			except KeyError:
				pass
			try:
				similar=data['adjective']['sim']
			except KeyError:
				pass
			try:
				similar=data['noun']['sim']
			except KeyError:
				pass
			try:
				antonym=data['verb']['ant']
			except KeyError:
				pass
			try:
				antonym=data['adjective']['ant']
			except KeyError:
				pass
			try:
				antonym=data['noun']['ant']
			except KeyError:
				pass
			if len(similar)>0:
				for w in range(len(similar)):
					choice.append(similar[w])
			if len(antonym)>0:
				for y in range(len(antonym)):
					choice.append(antonym[y])
		except ValueError:
			pass


		
		if len(choice)>3:
			shuffle(choice)
		
			for i in range(len(choice)):
				if '-' not in choice[i] and len(k)<3 and '_' not in choice[i]:
					k.append(choice[i])
		#print len(choice)
		
		if len(choice) <3:
			for q in range(3-len(choice)):
				choice.append(newlist[q])
				
			k=choice

				

					
		#print "hry"+str(len(k))
		if len(k) <3:
			for i in range(3-len(choice)):
				k.append(newlistnew[random.randint(0,len(newlistnew))])
		#print len(k)
		k.append(word)
		shuffle(k)
		b=0
		for p in range(len(k)):
			if k[p]==word:
				b=p
		#print "word is"+word

		choice1=returndef(request,k)
		

		question2[j].append(choice1[0])
		question2[j].append(choice1[1])
		question2[j].append(choice1[2])
		question2[j].append(choice1[3])
		question2[j].append(b)
		#print question2
	return question2

@csrf_exempt
def bookmarks(request):
	if request.method=='POST':
		selectedpackages = json.loads(request.body)
		new_json = json.dumps(selectedpackages)
		newdict = ast.literal_eval(new_json)
		
		kk  =  newdict['word'].strip()
		meaning=list(wordmeaning.objects.filter(word_name=kk).values('word_meaning'))
		meaning=json.dumps(meaning)
		meaning=ast.literal_eval(meaning)
		exist=bookmark.objects.filter(word=kk).count()
		if exist==0:
			if len(meaning)>0:

			
				bookmark.objects.create(user=request.user,word=kk,word_meaning=meaning[0]['word_meaning'])
				return HttpResponse("bookmarked")
			else:
				res = requests.get('http://www.merriam-webster.com/dictionary'+'/'+kk)
				soup = bs4.BeautifulSoup(res.text)
				elems=soup.select('.definition-list')
				meaning=elems[0].getText()
				
				meaning=meaning.split(':')
				meaning= meaning[1].strip('\n')
				bookmark.objects.create(user=request.user,word=kk,word_meaning=meaning)
				return HttpResponse("bookmarked")
		else:
			return HttpResponse("already bookmarked")
	else:
		if not request.user.is_authenticated():
			return render_to_response("start.html")
		else:
			if request.user.is_authenticated():
				booklist=list(bookmark.objects.filter(user=request.user).values('word','word_meaning'))
				booklist=json.dumps(booklist)
				return render_to_response("vocab.html",{'wordlist':booklist})
			else:
				return render_to_response("start.html")
@csrf_exempt
def delbookmark(request):
	if request.method=='POST':
		selectedpackages = json.loads(request.body)
		new_json = json.dumps(selectedpackages)
		newdict = ast.literal_eval(new_json)
		
		kk  =  newdict['word'].strip()
		bookmark.objects.filter(word=kk).delete()
		return HttpResponse("deleted")
def testing(request):
	list2=['2','3','4']
	list3=['6','7']
	return HttpResponse(list2)
@csrf_exempt
def lookup(request):
	if request.method=='POST':
		selectedpackages = json.loads(request.body)
		new_json = json.dumps(selectedpackages)
		newdict = ast.literal_eval(new_json)
		kk  =  newdict['word'].strip()
		meaning=list(wordmeaning.objects.filter(word_name=kk).values('word_meaning'))
		meaning=json.dumps(meaning)
		meaning=ast.literal_eval(meaning)
		meaning=meaning[0]['word_meaning']
		meaning=meaning.split(':')
		meaning= meaning[1].strip('\n')
		#print meaning
		#return HttpResponse(str(meaning))
		return 22

def handler404(request):
    return render_to_response('404.html')


def logout(request):
	django_logout(request)
	return render_to_response("index.html")

def aboutus(request):
	return render_to_response("about.html")

def  index(request):
	return render_to_response("index.html")
def impwords(request):
	res = requests.get('https://www.vocabulary.com/lists/52473#view=notes')
	soup = bs4.BeautifulSoup(res.text)
	#elems=soup.findAll("li", {"class":"entry learnable"})
	elems=soup.findAll("li",{"class":"entry learnable"})
	
	td=[k.find("div",{"class":"definition"}) for k in elems]
	pd=[k.find("div",{"class":"example"}) for k in elems]
	
	
	for i in range(len(elems)):
		list1.objects.create(word_name=str(elems[i]['word']),word_meaning=str(td[i].getText()),word_example=str(pd[i].getText().encode('utf-8')))


def returndef(request,mylist):
	newchoicedef=list()
	newlistnew=['soldier','patriotic','big','random','happy']
	##print len(mylist)
	##print mylist
	for i in range(len(mylist)):
		check=wordmeaning.objects.filter(word_name=mylist[i]).count()
		if check==0:
			##print mylist[i]
			try:
				res = requests.get('http://www.merriam-webster.com/dictionary'+'/'+mylist[i])
				soup = bs4.BeautifulSoup(res.text)
				elems=soup.select('.definition-list')
				meaning=elems[0].getText()
				meaning=meaning.split(':')
				meaning= meaning[1].strip('\n')
				newchoicedef.append(meaning)
			except IndexError:
				a=random.randint(0,4)
				b=list()
				b.append(newlistnew[a])
				newmeaning=returndef(request,b)
				newchoicedef.append(newmeaning[0])

		else:
			meaning=""
			try:
				k=list(wordmeaning.objects.filter(word_name=mylist[i]).values('word_name','word_meaning'))
				k=json.dumps(k)
				k=ast.literal_eval(k)
				k=k[0]['word_meaning'].split(':')
				meaning=k
				k=k[1].strip('\n')
				newchoicedef.append(k)
			except IndexError:
				newchoicedef.append(meaning)
	##print newchoicedef
	return newchoicedef
def hehe(request):
	return render_to_response("privacy.html")
def start(request):

	if not request.user.is_authenticated():
		#return HttpResponse("hey man")
		return render_to_response("start.html")
	else:
		return show_article_list(request,bit=0)

def open_comp_article(request,articleid):
	if not request.user.is_authenticated():
		return render_to_response("start.html")
	else:
		if_visited=article_visited.objects.filter(user_id=request.user,article_id__id=articleid).count()
		lit=list(article.objects.filter(id=articleid).values('id','image','heading','summary','content','level'))
		lit=json.dumps(lit)
		buffer_list=list()
		if if_visited==0:
			
			question_list_mcq=list(sample_question.objects.filter(article_id__id=articleid,question_type=1).annotate(id1=F('id')).values('id1','article_id__id','question_type','question_text'))
			question_list_mcq=json.dumps(question_list_mcq)
			question_list_mcq=ast.literal_eval(question_list_mcq)
			for i in range(len(question_list_mcq)):
				buffer_list.append(question_list_mcq[i]['id1'])
			choice_list_mcq=list(mcq.objects.filter(sample_question_id__id__in=buffer_list).annotate(id1=F('sample_question_id__id')).values('id1','choice1','choice2','choice3','choice4','right_choice'))
			choice_list_mcq=json.dumps(choice_list_mcq)

			question_list_more=list(sample_question.objects.filter(article_id__id=articleid,question_type=2).annotate(id1=F('id')).values('id1','article_id__id','question_type','question_text'))
			question_list_more=json.dumps(question_list_more)
			question_list_more=ast.literal_eval(question_list_more)
			for i in range(len(question_list_more)):
				buffer_list.append(question_list_more[i]['id1'])
			choice_list_more=list(morethanonechoice.objects.filter(sample_question_id__id__in=buffer_list).annotate(id1=F('sample_question_id__id')).values('id1','choice1','choice2','choice3','choice4','right_choice'))
			choice_list_more=json.dumps(choice_list_more)
			#return HttpResponse(buffer_list)
			for i in range(len(buffer_list)):
				p=sample_performance.objects.create(user_id=request.user,sample_question_id_id=buffer_list[i],response=0,article_under_id=articleid)
			article_visited.objects.create(user_id=request.user,article_id_id=articleid)
			return render_to_response("editorial.html",{'mcq_questions':json.dumps(question_list_mcq),'morethanonechoice_questions':json.dumps(question_list_more),'mcq_choices':choice_list_mcq,'morethanonechoice_choices':choice_list_more,'list':lit})
		else:
			question_list_mcq=list(sample_performance.objects.filter(user_id=request.user,article_under__id=articleid,sample_question_id__question_type=1).annotate(id1=F('sample_question_id__id'),question_text=F('sample_question_id__question_text'),question_type=F('sample_question_id__question_type')).values('question_text','id1','question_type'))
			question_list_mcq=json.dumps(question_list_mcq)
			question_list_mcq=ast.literal_eval(question_list_mcq)
			for i in range(len(question_list_mcq)):
				buffer_list.append(question_list_mcq[i]['id1'])
			choice_list_mcq=list(mcq.objects.filter(sample_question_id__id__in=buffer_list).annotate(id1=F('sample_question_id__id')).values('id1','choice1','choice2','choice3','choice4','right_choice'))
			choice_list_mcq=json.dumps(choice_list_mcq)
			question_list_more=list(sample_performance.objects.filter(user_id=request.user,article_under__id=articleid,sample_question_id__question_type=2).annotate(id1=F('sample_question_id__id'),question_text=F('sample_question_id__question_text'),question_type=F('sample_question_id__question_type')).values('question_text','id1','question_type'))
			question_list_more=json.dumps(question_list_more)
			question_list_more=ast.literal_eval(question_list_more)
			for i in range(len(question_list_more)):
				buffer_list.append(question_list_more[i]['id1'])
			choice_list_more=list(morethanonechoice.objects.filter(sample_question_id__id__in=buffer_list).annotate(id1=F('sample_question_id__id')).values('id1','choice1','choice2','choice3','choice4','right_choice'))
			choice_list_more=json.dumps(choice_list_more)
			return render_to_response("editorial.html",{'mcq_questions':json.dumps(question_list_mcq),'morethanonechoice_questions':json.dumps(question_list_more),'mcq_choices':choice_list_mcq,'morethanonechoice_choices':choice_list_more,'list':lit})
	
	
def show_editorial_list(request,bit=0):
	if not request.user.is_authenticated():
		return render_to_response("start.html")
	else:
		listing=list(article.objects.filter(article_type=2).values('id','image','heading','level','summary'))
		listing=json.dumps(listing)


		return render_to_response("list.html",{'list':listing,"email":request.user.email,"bit":bit})



def bookmark_questions_api(request,bit):
	word_attempted=list(bookmark_attempted.objects.filter(user_id=request.user).values('question_id__word_used__word'))
	word_attempted=json.dumps(word_attempted)
	word_attempted=ast.literal_eval(word_attempted)
	word_attempted_list=list()
	for i in range(len(word_attempted)):
		word_attempted_list.append(word_attempted[i]['question_id__word_used__word'])
	

	word_free=list(bookmark.objects.filter(user_id=request.user).exclude(word__in=word_attempted_list).values('id','word'))
	word_free=json.dumps(word_free)
	
	word_free=ast.literal_eval(word_free)
	#print word_free
	v=random.randint(0,(len(word_free)-1))
	#print v 
	word_selected=word_free[v]['word']
	
	question=findvocab(request,word_selected)
	question_json={}
	question_json['question_text']=question[0][0]
	question_json['choice1']=question[0][1]
	question_json['choice2']=question[0][2]
	question_json['choice3']=question[0][3]
	question_json['choice4']=question[0][4]
	question_json['right_choice']=question[0][5]

	k=bookmark_questions.objects.create(word_used_id=word_free[v]['id'],question_text=question_json['question_text'],choice1=question_json['choice1'],choice2=question_json['choice2'],choice3=question_json['choice3'],choice4=question_json['choice1'],right_choice=question_json['right_choice'])
	question_json['id']=k.id

	if bit==0:

	

	

		return render_to_response("vocab_uestion.html",{'question':json.dumps(question_json)})
	else:
		question=question_json
		return HttpResponse(json.dumps(question))


def gen_vocab_questions(request,articleid):
	newlist=list()
	newlistnew=['soldier','patriotic','big','random','happy']
	if_parsed=list(article.objects.filter(id__in=articleid).values('id','content'))
	if_parsed=json.dumps(if_parsed)

	if_parsed=ast.literal_eval(if_parsed)
	myvocab=list()
	newvocab=list()
	
	
	for i in range(len(if_parsed)):
		b=vocab(if_parsed[i]['content'])
		
		for h in range(len(b)):
			find_word=common_words.objects.filter(word_anurag=b[h]).count()
			contains_word=wordmeaning.objects.filter(word_name=b[h]).count()
			if find_word==0 and len(b[h])>2 and contains_word==0:
				myvocab.append(b[h])
		
	



	
		
		
		newlist=myvocab
		
		for l in range(2):
			question2=list()	#syn=synonyms.objects.create(word_id=pk,synonym_def="jj")
			num=random.randint(0,len(newlist))
			word=newlist[num]
			
			question2.insert(0,word)
			choice=list()
			k=list()
			

			
			url="http://words.bighugelabs.com/api/2/6315f684524176c55a924bccc603e395"+"/"+word+"/"+"json"
			response = urllib.urlopen(url)
			try:
				data = json.loads(response.read())
				similar=list()
				antonym=list()
				

				for o in range(len(wn.synsets(word)[0].hypernyms())):
						try:
							choice.append(wn.synsets(word)[0].hypernyms()[o].name().split('.')[0])
						except IndexError:
							pass
				for f in range(len(wn.synsets(word)[0].hyponyms())):
					try:
						choice.append(wn.synsets(word)[0].hyponyms()[f].name().split('.')[0])
					except IndexError:
						pass
				try:
					similar=data['verb']['sim']
				except KeyError:
					pass
				try:
					similar=data['adjective']['sim']
				except KeyError:
					pass
				try:
					similar=data['noun']['sim']
				except KeyError:
					pass
				try:
					antonym=data['verb']['ant']
				except KeyError:
					pass
				try:
					antonym=data['adjective']['ant']
				except KeyError:
					pass
				try:
					antonym=data['noun']['ant']
				except KeyError:
					pass
				if len(similar)>0:
					for w in range(len(similar)):
						choice.append(similar[w])
				if len(antonym)>0:
					for y in range(len(antonym)):
						choice.append(antonym[y])
			except ValueError:
				pass


			
			if len(choice)>3:
				shuffle(choice)
			
				for q in range(len(choice)):
					if '-' not in choice[q] and len(k)<3 and '_' not in choice[q]:
						k.append(choice[q])
			#print len(choice)
			
			if len(choice) <3:
				for q in range(3-len(choice)):
					choice.append(newlist[q])
					
				k=choice

					

						
			#print "hry"+str(len(k))
			if len(k) <3:
				for i in range(3-len(choice)):
					k.append(newlistnew[random.randint(0,len(newlistnew))])
			#print len(k)
			k.append(word)
			shuffle(k) 
			
			b=0
			for p in range(len(k)):
				if k[p]==word:
					b=p
			#print "word is"+word

			choice1=returndef(request,k)
			

			question2.append(choice1[0])
			question2.append(choice1[1])
			question2.append(choice1[2])
			question2.append(choice1[3])
			question2.append(b)
			#print question2
			##print "question_text"+str(question2[j][0])
			##print "Word"+str(question2[j][0])
			#print "id"+str(if_parsed[i]['id'])
			k=sample_question.objects.create(article_id_id=if_parsed[i]['id'],question_text=question2[0],subtopic=9,level=1,question_type=1,question_type_type=2,word=question2[0],tag=0)
			mcq.objects.create(sample_question_id_id=k.id,choice1=choice1[0],choice2=choice1[1],choice3=choice1[2],choice4=choice1[3],right_choice=b)
	verb_forms_gen(request,mylist=myvocab)


def testingnew(request):
	if_parsed=list(article.objects.filter(parsed=False).values('id','content'))
	if_parsed=json.dumps(if_parsed)
	if_parsed=ast.literal_eval(if_parsed)
	myvocab=list()
	for i in range(len(if_parsed)):
		b=vocab(if_parsed[i]['content'])
		
		for h in range(len(b)):
			find_word=common_words.objects.filter(word_anurag=b[h]).count()
			contains_word=wordmeaning.objects.filter(word_name=b[h]).count()
			if find_word==0 and len(b[h])>2 and contains_word==0:
				myvocab.append(b[h])

	verb_forms_gen(request,mylist=myvocab)
