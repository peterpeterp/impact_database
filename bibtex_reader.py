import sys  

reload(sys)  
sys.setdefaultencoding('utf8')


class bibliography(object):
	def __init__(self,test=None):
		self._articles=[]
		self._meta={'author':{},'year':{},'title':{},'publisher':{},'keywords':{}}

	def clean(self,string):
		string=string.replace('{','').replace('}','').replace(',','').replace('\t','')
		while string[0]==' ':string=''.join(string[1:])
		while string[-1]==' ':string=''.join(string[0:-1])
		return string.encode('utf-8')

	def extract_keywords(self,string):
		string=string.replace('{','').replace('}','')
		while string[0]==' ':string=''.join(string[1:])
		while string[-1]==' ':string=''.join(string[0:-1])
		keywords=string.split(',')
		keywords=list(filter(None, keywords))
		keywords=[key.lower().replace('\\&','and') for key in keywords]
		return keywords

	class article(object):

		def __init__(SELF,bibtex,bibli,index):
			SELF.bibtex=bibtex
			SELF.author=''
			SELF.title=''
			SELF.year=''
			SELF.publisher=''
			SELF.institution=''
			SELF.journal=''
			SELF.url=''
			SELF.doi=''
			SELF.abstract=''
			SELF.keywords=[]
			for line in bibtex.split('\n'):
				if len(line.split('='))>1:
					if bibli.clean(line.split('=')[0]).lower()=='doi': 
						doi=bibli.clean(line.split('=')[1])
						SELF.doi=doi

					if bibli.clean(line.split('=')[0]).lower()=='url': 
						url=bibli.clean(line.split('=')[1])
						SELF.url=url

					if bibli.clean(line.split('=')[0]).lower()=='abstract': 
						abstract=bibli.clean(line.split('=')[1])
						SELF.abstract=abstract

					if bibli.clean(line.split('=')[0]).lower()=='institution': 
						institution=bibli.clean(line.split('=')[1])
						SELF.institution=institution

					if bibli.clean(line.split('=')[0]).lower()=='journal': 
						journal=bibli.clean(line.split('=')[1])
						SELF.journal=journal

					if bibli.clean(line.split('=')[0]).lower()=='author': 
						author_list=bibli.clean(line.split('=')[1]).split(' and')
						if len(author_list)>1: author=author_list[0]+' et al.'
						if len(author_list)==1: author=author_list[0]
						SELF.author=author
						if author not in bibli._meta['author']:bibli._meta['author'][author]=[]
						bibli._meta['author'][author].append(index)

					if bibli.clean(line.split('=')[0]).lower()=='title': 
						title=bibli.clean(line.split('=')[1])
						SELF.title=title
						if title not in bibli._meta['title']:bibli._meta['title'][title]=[]
						bibli._meta['title'][title].append(index)

					if bibli.clean(line.split('=')[0]).lower()=='year': 
						year=bibli.clean(line.split('=')[1])
						SELF.year=year
						if year not in bibli._meta['year']:bibli._meta['year'][year]=[]
						bibli._meta['year'][year].append(index)

					if bibli.clean(line.split('=')[0]).lower()=='publisher': 
						publisher=bibli.clean(line.split('=')[1])
						SELF.publisher=publisher
						if publisher not in bibli._meta['publisher']:bibli._meta['publisher'][publisher]=[]
						bibli._meta['publisher'][publisher].append(index)


					if bibli.clean(line.split('=')[0]).lower()=='keywords': 
						keywords=bibli.extract_keywords(line.split('=')[1])
						SELF.keywords=keywords

			if len(list(filter(lambda x: (x.lower() in ['ngo','international institution','governmental institution']),SELF.keywords)))!=0:
				SELF.keywords.append('grey literature')

			for key in SELF.keywords:
				if key not in bibli._meta['keywords']:bibli._meta['keywords'][key]=[]
				bibli._meta['keywords'][key].append(index)	







	def add_article(self,bibtex):
		new=self.article(bibtex=bibtex,bibli=self,index=len(self._articles))
		self._articles.append(new)

	def filter(self,filters):
		to_filter={}
		possible=range(len(self._articles))
		selected=range(len(self._articles))

		for key in filters.keys():
			for accepted in filters[key]:
				for item in possible:
					if (item not in self._meta[key][accepted]) & (item in selected):
						selected.remove(item)
				
		return(selected)




	def count_occurence_of_keyword(self,selected):
		occurence=[]
		for i in selected:
			occurence+=self._articles[i].keywords

		freq_dict={}
		for key in occurence:
			if key not in freq_dict.keys():
				freq_dict[key]=0
			freq_dict[key]+=1

		word_count=list()
		for key in freq_dict.keys():
			word_count.append((key,freq_dict[key]))
		return occurence,freq_dict,word_count

	def count_occurence_of_author(self,selected):
		occurence=[]
		for i in selected:
			occurence+=[self._articles[i].author]

		freq_dict={}
		for key in occurence:
			if key not in freq_dict.keys():
				freq_dict[key]=0
			freq_dict[key]+=1

		word_count=list()
		for key in freq_dict.keys():
			word_count.append((key,freq_dict[key]))
		return occurence,freq_dict,word_count

	def count_occurence_of_institution(self,selected):
		occurence=[]
		for i in selected:
			occurence+=[self._articles[i].institution]

		freq_dict={}
		for key in occurence:
			if key not in freq_dict.keys():
				freq_dict[key]=0
			freq_dict[key]+=1

		word_count=list()
		for key in freq_dict.keys():
			word_count.append((key,freq_dict[key]))
		return occurence,freq_dict,word_count

	def count_occurence_of_journal(self,selected):
		occurence=[]
		for i in selected:
			occurence+=[self._articles[i].journal]

		freq_dict={}
		for key in occurence:
			if key not in freq_dict.keys():
				freq_dict[key]=0
			freq_dict[key]+=1

		word_count=list()
		for key in freq_dict.keys():
			word_count.append((key,freq_dict[key]))
		return occurence,freq_dict,word_count



